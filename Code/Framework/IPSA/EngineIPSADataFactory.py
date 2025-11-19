"""
EngineIPSADataFactory - Converts Framework DataModel to IPSA Component Objects
Provides conversion methods to transform framework components into IPSA-ready objects.
Part of the Jesse PowerFactory Modelling Framework.
"""

import pandas as pd
import math
from typing import Dict, List, Optional, Tuple
from Code import GlobalEngineRegistry as gbl
from Code.Framework.IPSA.EngineIPSAComponents import *


class EngineIPSADataFactory:
    """Converts Framework DataModel components to IPSA component objects"""

    def __init__(self):
        self.msg = gbl.Msg if hasattr(gbl, 'Msg') and gbl.Msg else None
    # =====================================================================
    # Utility Methods
    # =====================================================================
    def _safe_float(self, val, default=0.0):
        """Safely convert value to float"""
        try:
            if pd.isna(val) or val is None:
                return default
            return float(val)
        except (ValueError, TypeError):
            return default
    def _safe_str(self, val, default=""):
        """Safely convert value to string"""
        if pd.isna(val) or val is None:
            return default
        return str(val).strip()
    def _safe_int(self, val, default=0):
        """Safely convert value to int"""
        try:
            if pd.isna(val) or val is None:
                return default
            return int(val)
        except (ValueError, TypeError):
            return default

    # =====================================================================
    # Busbar Conversion Methods
    # =====================================================================
    def convert_framework_busbar_to_ipsa(self, busbar_datamodel) -> IPSA_IscBusbar:
        """
        Convert framework Busbar to IPSA_IscBusbar
        Args:
            busbar_datamodel: Framework Busbar object
        Returns:
            IPSA_IscBusbar: IPSA-ready busbar object
        """
        ipsa_busbar = IPSA_IscBusbar()

        # Basic properties
        ipsa_busbar.Name = self._safe_str(busbar_datamodel.BusID)
        ipsa_busbar.NomVoltkV = self._safe_float(busbar_datamodel.kV, 132.0)
        # Create comment with available information
        comment_parts = [
            f"Framework Busbar: {ipsa_busbar.Name}",
            f"Nominal Voltage: {ipsa_busbar.NomVoltkV} kV"
        ]
        if hasattr(busbar_datamodel, 'name') and busbar_datamodel.name:
            comment_parts.append(f"Name: {busbar_datamodel.name}")
        if hasattr(busbar_datamodel, 'Disconnected'):
            status = "Disconnected" if busbar_datamodel.Disconnected else "Connected"
            comment_parts.append(f"Status: {status}")
        ipsa_busbar.Comment = "\n".join(comment_parts)
        # Coordinate handling (if available)
        ipsa_busbar.X_coordinate = ""
        ipsa_busbar.Y_coordinate = ""
        return ipsa_busbar

    # =====================================================================
    # Branch Conversion Methods
    # =====================================================================
    def convert_framework_branch_to_ipsa(self, branch_datamodel) -> Optional[IPSA_IscBranch]:
        """
        Convert framework Branch to IPSA_IscBranch
        Args:
            branch_datamodel: Framework Branch object
        Returns:
            IPSA_IscBranch or None: IPSA-ready branch object
        """
        # Skip if transformer (handled separately)
        if hasattr(branch_datamodel, 'IsTransformer') and branch_datamodel.IsTransformer:
            return None
        ipsa_branch = IPSA_IscBranch()
        # Basic connectivity
        ipsa_branch.FromBusName = self._safe_str(branch_datamodel.BusID1)
        ipsa_branch.ToBusName = self._safe_str(branch_datamodel.BusID2)
        ipsa_branch.Name = self._safe_str(branch_datamodel.BranchID,
                                         f"{ipsa_branch.FromBusName}-{ipsa_branch.ToBusName}")
        # Status
        ipsa_branch.Status = 0 if (hasattr(branch_datamodel, 'ON') and branch_datamodel.ON) else -1
        # Electrical parameters (with safe defaults)
        ipsa_branch.ResistancePU = max(self._safe_float(getattr(branch_datamodel, 'R', 0)), 0.0001)
        ipsa_branch.ReactancePU = max(self._safe_float(getattr(branch_datamodel, 'X', 0)), 0.001)
        ipsa_branch.SusceptancePU = self._safe_float(getattr(branch_datamodel, 'B', 0))
        # Zero sequence (if available)
        ipsa_branch.ZSResistancePU = self._safe_float(getattr(branch_datamodel, 'R0', 0))
        ipsa_branch.ZSReactancePU = self._safe_float(getattr(branch_datamodel, 'X0', 0))
        # Ratings (with defaults)
        default_rating = 9999.0
        winter_rating = self._safe_float(getattr(branch_datamodel, 'WinterRating', default_rating), default_rating)
        summer_rating = self._safe_float(getattr(branch_datamodel, 'SummerRating', default_rating), default_rating)
        ipsa_branch.RatingMVAs = [winter_rating, summer_rating, winter_rating]
        # Length
        ipsa_branch.LengthKm = max(self._safe_float(getattr(branch_datamodel, 'Length', 1.0)), 0.001)
        # Line type determination
        ipsa_branch.Type = self._determine_branch_type(branch_datamodel)
        # Special flags
        ipsa_branch.ZeroImpedance = (hasattr(branch_datamodel, 'IsZeroLength') and 
                                   branch_datamodel.IsZeroLength)
        # Comment
        ipsa_branch.Comment = self._create_branch_comment(branch_datamodel)
        return ipsa_branch
    def _determine_branch_type(self, branch_datamodel) -> int:
        """Determine IPSA branch type from framework branch"""
        # Check if branch has type information
        if hasattr(branch_datamodel, 'BranchType'):
            branch_type = self._safe_str(branch_datamodel.BranchType).lower()
            if 'cable' in branch_type:
                return 2  # Cable
            elif 'overhead' in branch_type or 'ohl' in branch_type:
                return 1  # Overhead line
            elif 'composite' in branch_type:
                return 4  # Composite
        # Default to overhead line
        return 1
    def _create_branch_comment(self, branch_datamodel) -> str:
        """Create comment for IPSA branch"""
        comment_parts = [
            f"Framework Branch: {getattr(branch_datamodel, 'BranchID', 'Unknown')}",
            f"From: {getattr(branch_datamodel, 'BusID1', 'Unknown')}",
            f"To: {getattr(branch_datamodel, 'BusID2', 'Unknown')}"
        ]
        if hasattr(branch_datamodel, 'name') and branch_datamodel.name:
            comment_parts.append(f"Name: {branch_datamodel.name}")
        if hasattr(branch_datamodel, 'BranchType'):
            comment_parts.append(f"Type: {branch_datamodel.BranchType}")
        return "\n".join(comment_parts)

    # =====================================================================
    # Transformer Conversion Methods
    # ====================================================================
    def convert_framework_transformer_to_ipsa(self, transformer_datamodel) -> Optional[IPSA_IscTransformer]:
        """
        Convert framework transformer Branch to IPSA_IscTransformer
        Args:
            transformer_datamodel: Framework Branch object with IsTransformer=True
        Returns:
            IPSA_IscTransformer or None: IPSA-ready transformer object
        """
        # Only process transformers
        if not (hasattr(transformer_datamodel, 'IsTransformer') and transformer_datamodel.IsTransformer):
            return None
        ipsa_transformer = IPSA_IscTransformer()
        # Basic connectivity
        ipsa_transformer.FromBusName = self._safe_str(transformer_datamodel.BusID1)
        ipsa_transformer.ToBusName = self._safe_str(transformer_datamodel.BusID2)
        ipsa_transformer.Name = self._safe_str(transformer_datamodel.BranchID,
                                             f"{ipsa_transformer.FromBusName}-{ipsa_transformer.ToBusName}-Tx")
        # Type (assume super grid for high voltage)
        ipsa_transformer.Type = 5  # Super Grid
        ipsa_transformer.Winding = 2  # 2-winding transformer
        # Electrical parameters
        ipsa_transformer.CoreLossRPU = max(self._safe_float(getattr(transformer_datamodel, 'R', 0)), 0.0001)
        ipsa_transformer.MagnetXPU = max(self._safe_float(getattr(transformer_datamodel, 'X', 0)), 0.001)
        # Rating
        ipsa_transformer.RatingMVA = self._safe_float(
            getattr(transformer_datamodel, 'WinterRating', 100.0), 100.0)
        # Tap changer settings (conservative defaults)
        ipsa_transformer.TapNominalPC = 0.0
        ipsa_transformer.TapStartPC = 0.0
        ipsa_transformer.MinTapPC = -10.0
        ipsa_transformer.TapStepPC = 0.625
        ipsa_transformer.MaxTapPC = 10.0
        ipsa_transformer.LockTap = False
        ipsa_transformer.SpecVPU = 1.0
        ipsa_transformer.RBWidthPC = 2.0
        # Check for tap changer status from framework
        if hasattr(transformer_datamodel, 'tapchangeronestatus'):
            ipsa_transformer.LockTap = (transformer_datamodel.tapchangeronestatus == 0)
        # Quad booster parameters (if applicable)
        ipsa_transformer.PhShiftDeg = 0.0
        ipsa_transformer.MinPhShiftDeg = -20.0
        ipsa_transformer.MaxPhShiftDeg = 20.0
        ipsa_transformer.PhShiftStepDeg = 0.5
        ipsa_transformer.SpecPowerMW = 0.0
        ipsa_transformer.SpecPowerAtSend = True
        # Comment
        ipsa_transformer.Comment = self._create_transformer_comment(transformer_datamodel)
        return ipsa_transformer
    def _create_transformer_comment(self, transformer_datamodel) -> str:
        """Create comment for IPSA transformer"""
        comment_parts = [
            f"Framework Transformer: {getattr(transformer_datamodel, 'BranchID', 'Unknown')}",
            f"From: {getattr(transformer_datamodel, 'BusID1', 'Unknown')}",
            f"To: {getattr(transformer_datamodel, 'BusID2', 'Unknown')}"
        ]
        if hasattr(transformer_datamodel, 'name') and transformer_datamodel.name:
            comment_parts.append(f"Name: {transformer_datamodel.name}")
        if hasattr(transformer_datamodel, 'WinterRating'):
            comment_parts.append(f"Rating: {transformer_datamodel.WinterRating} MVA")
        return "\n".join(comment_parts)

    # =====================================================================
    # Load Conversion Methods
    # =====================================================================
    def convert_framework_load_to_ipsa(self, load_datamodel) -> IPSA_IscLoad:
        """
        Convert framework Load to IPSA_IscLoad
        Args:
            load_datamodel: Framework Load object
        Returns:
            IPSA_IscLoad: IPSA-ready load object
        """
        ipsa_load = IPSA_IscLoad()
        # Basic properties
        ipsa_load.BusName = self._safe_str(load_datamodel.BusID)
        ipsa_load.Name = self._safe_str(load_datamodel.LoadID, f"{ipsa_load.BusName}_Load")
        # Power values
        ipsa_load.RealMW = self._safe_float(load_datamodel.MW, 0.0)
        ipsa_load.ReactiveMVAr = self._safe_float(load_datamodel.MVar, 0.0)
        # If no reactive power specified, assume 10% of real power
        if ipsa_load.ReactiveMVAr == 0.0 and ipsa_load.RealMW > 0.0:
            ipsa_load.ReactiveMVAr = ipsa_load.RealMW * 0.1
        # Status
        ipsa_load.Status = 0 if (hasattr(load_datamodel, 'ON') and load_datamodel.ON) else -1
        # Comment
        comment_parts = [
            f"Framework Load: {ipsa_load.Name}",
            f"Bus: {ipsa_load.BusName}",
            f"Real Power: {ipsa_load.RealMW} MW",
            f"Reactive Power: {ipsa_load.ReactiveMVAr} MVAr"
        ]
        if hasattr(load_datamodel, 'name') and load_datamodel.name:
            comment_parts.append(f"Name: {load_datamodel.name}")
        ipsa_load.Comment = "\n".join(comment_parts)
        return ipsa_load

    # =====================================================================
    # Generator Conversion Methods
    # =====================================================================
    def convert_framework_generator_to_ipsa(self, generator_datamodel) -> IPSA_IscSynMachine:
        """
        Convert framework Generator to IPSA_IscSynMachine
        Args:
            generator_datamodel: Framework Generator object
        Returns:
            IPSA_IscSynMachine: IPSA-ready generator object
        """
        ipsa_generator = IPSA_IscSynMachine()
        # Basic properties
        ipsa_generator.BusName = self._safe_str(generator_datamodel.BusID)
        ipsa_generator.Name = self._safe_str(generator_datamodel.GenID,
                                           f"{ipsa_generator.BusName}_Gen")
        # Status
        ipsa_generator.Status = 0 if (hasattr(generator_datamodel, 'ON') and generator_datamodel.ON) else -1
        # Voltage control
        ipsa_generator.VoltPU = 1.0
        ipsa_generator.VoltBandwidthPC = 5.0
        # Power settings
        ipsa_generator.GenMW = self._safe_float(generator_datamodel.MW, 0.0)
        ipsa_generator.GenMVAr = self._safe_float(generator_datamodel.MVar, 0.0)
        ipsa_generator.GenRatedMW = self._safe_float(getattr(generator_datamodel, 'MWCapacity',
                                                           generator_datamodel.MW), 0.0)
        # Reactive power limits
        ipsa_generator.GenMVArMax = self._safe_float(getattr(generator_datamodel, 'Qmax',
                                                           ipsa_generator.GenRatedMW * 0.3), 0.0)
        ipsa_generator.GenMVArMin = self._safe_float(getattr(generator_datamodel, 'Qmin',
                                                           -ipsa_generator.GenMVArMax), 0.0)
        # Apparent power rating
        ipsa_generator.GenRatedMVA = max(ipsa_generator.GenRatedMW,
                                       abs(ipsa_generator.GenMVArMax)) / 0.95 if ipsa_generator.GenRatedMW > 0 else 0.0
        # Technology type (default)
        ipsa_generator.GenTechnology = 0
        # External grid handling
        if hasattr(generator_datamodel, 'IsExternalGrid') and generator_datamodel.IsExternalGrid:
            # External grids typically have higher capacity
            if ipsa_generator.GenRatedMW == 0:
                ipsa_generator.GenRatedMW = 1000.0  # Default external grid capacity
                ipsa_generator.GenRatedMVA = 1000.0 / 0.95
        # Comment
        ipsa_generator.Comment = self._create_generator_comment(generator_datamodel)
        return ipsa_generator
    def _create_generator_comment(self, generator_datamodel) -> str:
        """Create comment for IPSA generator"""
        comment_parts = [
            f"Framework Generator: {getattr(generator_datamodel, 'GenID', 'Unknown')}",
            f"Bus: {getattr(generator_datamodel, 'BusID', 'Unknown')}"
        ]
        if hasattr(generator_datamodel, 'name') and generator_datamodel.name:
            comment_parts.append(f"Name: {generator_datamodel.name}")
        if hasattr(generator_datamodel, 'IsExternalGrid') and generator_datamodel.IsExternalGrid:
            comment_parts.append("Type: External Grid")
        if hasattr(generator_datamodel, 'MWCapacity'):
            comment_parts.append(f"Capacity: {generator_datamodel.MWCapacity} MW")
        return "\n".join(comment_parts)

    # =====================================================================
    # Main Conversion Method
    # =====================================================================
    def build_ipsa_network_model_from_datamodel(self) -> IPSA_Network_Model:
        """
        Create complete IPSA_Network_Model from framework DataModel
        Returns:
            IPSA_Network_Model: Complete IPSA network model ready for engine loading
        """
        if not hasattr(gbl, 'DataModelManager') or gbl.DataModelManager is None:
            raise RuntimeError("DataModelManager not initialized")
        if self.msg:
            self.msg.AddRawMessage("Building IPSA Network Model from Framework DataModel...")
        ipsa_model = IPSA_Network_Model()
        # Convert busbars
        for busbar in gbl.DataModelManager.Busbar_TAB:
            ipsa_busbar = self.convert_framework_busbar_to_ipsa(busbar)
            ipsa_model.list_oBusbar.append(ipsa_busbar)
        # Convert branches and transformers
        for branch in gbl.DataModelManager.Branch_TAB:
            if hasattr(branch, 'IsTransformer') and branch.IsTransformer:
                # Convert as transformer
                ipsa_transformer = self.convert_framework_transformer_to_ipsa(branch)
                if ipsa_transformer:
                    ipsa_model.list_o2WindingTx.append(ipsa_transformer)
            else:
                # Convert as line
                ipsa_branch = self.convert_framework_branch_to_ipsa(branch)
                if ipsa_branch:
                    ipsa_model.list_oLine.append(ipsa_branch)
        # Convert loads
        for load in gbl.DataModelManager.Load_TAB:
            ipsa_load = self.convert_framework_load_to_ipsa(load)
            ipsa_model.list_oLoad.append(ipsa_load)
        # Convert generators
        for generator in gbl.DataModelManager.Gen_TAB:
            ipsa_generator = self.convert_framework_generator_to_ipsa(generator)
            ipsa_model.list_oGenerator.append(ipsa_generator)
        # Log results
        if self.msg:
            counts = ipsa_model.get_component_counts()
            self.msg.AddRawMessage(f"IPSA Network Model created with:")
            for component_type, count in counts.items():
                if count > 0:
                    self.msg.AddRawMessage(f"  {component_type}: {count}")
        return ipsa_model
    # =====================================================================
    # Validation Methods
    # =====================================================================
    def validate_ipsa_model(self, ipsa_model: IPSA_Network_Model) -> List[str]:
        """
        Validate IPSA network model for common issues
        Returns:
            List[str]: List of validation warnings/errors
        """
        warnings = []
        # Check for empty model
        counts = ipsa_model.get_component_counts()
        if counts['busbars'] == 0:
            warnings.append("No busbars found in model")
        # Check for isolated busbars
        connected_buses = set()
        for line in ipsa_model.list_oLine:
            connected_buses.add(line.FromBusName)
            connected_buses.add(line.ToBusName)
        for tx in ipsa_model.list_o2WindingTx:
            connected_buses.add(tx.FromBusName)
            connected_buses.add(tx.ToBusName)
        isolated_buses = []
        for busbar in ipsa_model.list_oBusbar:
            if busbar.Name not in connected_buses:
                isolated_buses.append(busbar.Name)
        if isolated_buses:
            warnings.append(f"Isolated busbars found: {isolated_buses}")
        # Check for missing generators
        if counts['generators'] == 0:
            warnings.append("No generators found - network may not solve")
        return warnings