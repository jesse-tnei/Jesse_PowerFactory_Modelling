# Engine wrapper for IPSA / PyIPSA
import os
from typing import Optional

import ipsa

from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineContainer import EngineContainer as EngineContainer
from Code.Framework.IPSA.EngineIPSADataFactory import EngineIPSADataFactory

class EngineIPSA(EngineContainer):
    """
    Engine class for IPSA/PyIPSA.
    Mirrors the high-level responsibilities of EnginePowerFactory:
      - initialise IPSA interface
      - open/close a network
      - get active network handle
      - access diagrams and basic network ops
    """

    def __init__(self, logger=None):
        EngineContainer.__init__(self)
        self.m_oMsg = gbl.Msg
        self.m_strTypeOfEngine = "Automated IPSA Tool"
        self.m_strVersion = "IPSA PyIPSA v3 API"
        self.m_iface = None
        self.m_network = None
        self.bus_uids = {}  # Track bus name -> UID mapping
        self._initialise_ipsa_interface()
        self.data_factory = EngineIPSADataFactory()

    # ---- Identity / metadata ----
    def isipsa(self) -> bool:
        """Check if this is an IPSA engine."""
        return True

    def getversion(self) -> str:
        """Return a displayable version string for this engine shell."""
        return self.m_strVersion

    # ---- Startup / interface ----
    def _initialise_ipsa_interface(self) -> None:
        """
        Create the IscInterface once per process.
        IPSA requires a single interface instance per process"""
        try:
            self.m_iface = ipsa.IscInterface()
            if self.m_oMsg:
                self.m_oMsg.AddInfo("Created IPSA IscInterface.")
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to create IPSA interface: {e}")
            raise

    # ---- Network I/O ----
    def opennetwork(self, **kwargs) -> bool:
        """
        Open an IPSA network file (.i3f / .i2f) and set as active.
        Returns True if successful. Uses IscInterface.ReadFile() which returns IscNetwork.
        """
        filepath = kwargs.get("filepath", None)
        if not os.path.isfile(filepath):
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Network file not found: {filepath}")
            return False
        try:
            self.m_network = self.m_iface.ReadFile(filepath)
            if self.m_oMsg:
                self.m_oMsg.AddInfo(f"Opened IPSA network: {filepath}")
            return True
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to open IPSA network '{filepath}': {e}")
            return False

    def createnetwork(self,
                      base_mva: float = 100.0,
                      freq_hz: float = 50.0,
                      with_diagram: bool = True,
                      single_line: bool = True,
                      geo_scale: float = 1.0,
                      units: int = 1) -> bool:
        """
        Create a new blank network and set as active
        """
        try:
            ok = self.m_iface.CreateNewNetwork(base_mva, freq_hz, with_diagram, single_line,
                                               geo_scale, units)
            if not ok:
                if self.m_oMsg:
                    self.m_oMsg.AddError("CreateNewNetwork returned False.")
                return False
            self.m_network = self.m_iface.GetNetwork()
            if self.m_oMsg:
                self.m_oMsg.AddInfo("Created new IPSA network.")
            return True
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to create network: {e}")
            return False

    def load_network_from_datamodel(self, save_file_path=None):
        """
        Load network from framework DataModel into IPSA engine
        Args:
            save_file_path (str, optional): Path to save IPSA file. If None, uses default naming.
        Returns:
            bool: Success status
        """
        try:
            self.m_oMsg.AddRawMessage("Loading network from framework DataModel to IPSA...")
            # Build IPSA network model from framework DataModel
            ipsa_model = self.data_factory.build_ipsa_network_model_from_datamodel()
            # Validate the model
            warnings = self.data_factory.validate_ipsa_model(ipsa_model)
            if warnings:
                self.m_oMsg.AddRawMessage("Validation warnings:")
                for warning in warnings:
                    self.m_oMsg.AddRawMessage(f"  - {warning}")
            # Clear existing IPSA network
            self.ClearNetwork()
            # Load components into IPSA engine
            success = self._load_ipsa_components_to_engine(ipsa_model)
            if success and save_file_path:
                # Save the IPSA file
                self.save_ipsa_file(save_file_path)
            return success
        except Exception as e:
            self.m_oMsg.AddRawMessage(f"Error loading network from DataModel: {str(e)}")
            return False
    def closenetwork(self) -> bool:
        """
        Close the current network (fails if there is unsaved data).
        """
        try:
            bOK = self.m_iface.CloseNetwork()
            if bOK:
                self.m_network = None
                if self.m_oMsg:
                    self.m_oMsg.AddInfo("Closed IPSA network.")
            else:
                if self.m_oMsg:
                    self.m_oMsg.AddWarning("CloseNetwork returned False (unsaved data?).")
            return bOK
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to close network: {e}")
            return False

    def _load_ipsa_components_to_engine(self, ipsa_model):
        """
        Load IPSA_Network_Model components into the IPSA engine
        Args:
            ipsa_model (IPSA_Network_Model): Complete IPSA network model
        Returns:
            bool: Success status
        """
        try:
            # Add busbars
            for busbar in ipsa_model.list_oBusbar:
                self.AddBusbar(busbar)
            # Add lines (branches)
            for line in ipsa_model.list_oLine:
                self.AddBranch(line)
            # Add transformers
            for transformer in ipsa_model.list_o2WindingTx:
                self.AddTransformer(transformer)
            # Add loads
            for load in ipsa_model.list_oLoad:
                self.AddLoad(load)
            # Add generators
            for generator in ipsa_model.list_oGenerator:
                self.AddSynMachine(generator)
            counts = ipsa_model.get_component_counts()
            self.m_oMsg.AddRawMessage(f"Successfully loaded {sum(counts.values())} components to IPSA engine")
            return True
        except Exception as e:
            self.m_oMsg.AddRawMessage(f"Error loading components to IPSA engine: {str(e)}")
            return False
    def save_ipsa_file(self, file_path):
        """
        Save current IPSA network to file
        Args:
            file_path (str): Full path where to save the IPSA file
        Returns:
            bool: Success status
        """
        try:
            # Ensure file has correct extension
            if not file_path.endswith(('.i2f', '.i3f')):
                file_path += '.i2f'
            success = self.WriteFile(file_path)
            if success:
                self.m_oMsg.AddRawMessage(f"IPSA network saved to: {file_path}")
            else:
                self.m_oMsg.AddRawMessage(f"Failed to save IPSA network to: {file_path}")
            return success
        except Exception as e:
            self.m_oMsg.AddRawMessage(f"Error saving IPSA file: {str(e)}")
            return False
    def load_etys_data_and_save(self, save_file_path=None):
        """
        Complete pipeline: Load ETYS data from DataModel and save IPSA file
        Args:
            save_file_path (str, optional): Path to save IPSA file
        Returns:
            bool: Success status
        """
        if save_file_path is None:
            import os
            save_file_path = os.path.join(os.getcwd(), "ETYS_Network.i2f")
        return self.load_network_from_datamodel(save_file_path)
    def _get_bus_uid_by_name(self, bus_name):
        """Get bus UID by name from tracking dictionary"""
        return self.bus_uids.get(bus_name)
    def getactivenetwork(self):
        """Return the active IscNetwork or None."""
        return self.m_network

    # ---- Network operations ----
    def setslackbus(self, busbar_python_name: str) -> bool:
        """
        Set the slack bus by its Python name (as returned by IscNetComponent.GetName()).
        Uses IscNetwork.SetBusbarSlack().
        """
        if not self.m_network:
            if self.m_oMsg:
                self.m_oMsg.AddError("No active IPSA network.")
            return False
        try:
            self.m_network.SetBusbarSlack(busbar_python_name)
            if self.m_oMsg:
                self.m_oMsg.AddInfo(f"Set slack busbar: {busbar_python_name}")
            return True
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to set slack busbar '{busbar_python_name}': {e}")
            return False

    def writenetwork(self, filepath: str) -> bool:
        """Save the current network to file. Uses IscNetwork.WriteFile()"""
        if not self.m_network:
            if self.m_oMsg:
                self.m_oMsg.AddError("No active IPSA network to save.")
            return False
        try:
            ok = self.m_network.WriteFile(
                filepath)  # -> bool  :contentReference[oaicite:13]{index=13}
            if self.m_oMsg:
                self.m_oMsg.AddInfo(f"Saved IPSA network to: {filepath}"
                                    if ok else f"WriteFile returned False for: {filepath}")
            return ok
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to save network: {e}")
            return False

    # ---- Diagrams ----
    def getdiagram(self, name: Optional[str] = None, uid: Optional[int] = None):
        """
        Fetch a diagram by name or UID. Uses IscInterface.GetDiagram()
        """
        if not self.m_network:
            if self.m_oMsg:
                self.m_oMsg.AddError("No active IPSA network.")
            return None
        if name is None and uid is None:
            if self.m_oMsg:
                self.m_oMsg.AddWarning("getdiagram: provide a name or uid.")
            return None
        try:
            if name is not None:
                return self.m_iface.GetDiagram(self.m_network, name)
            return self.m_iface.GetDiagram(self.m_network, uid)
        except Exception as e:
            if self.m_oMsg:
                self.m_oMsg.AddError(f"Failed to get diagram: {e}")
            return None
    def ClearNetwork(self):
        """Clear existing network by creating a new one"""
        self.bus_uids.clear()  # Clear the tracking dictionary
        return self.createnetwork()

    def WriteFile(self, filepath):
        """Write network to file using real IPSA API"""
        if not self.m_network:
            return False
        return self.m_network.WriteFile(filepath)

    def AddBusbar(self, ipsa_busbar):
        """Create busbar using real IPSA API"""
        if not self.m_network:
            return False
        uid = self.m_network.CreateBusbar(ipsa_busbar.Name)
        elem = self.m_network.GetBusbar(uid)
        ipsa_busbar.configure_in_ipsa(elem)
        # Track the UID for later lookup
        self.bus_uids[ipsa_busbar.Name] = uid
        return uid

    def AddBranch(self, ipsa_branch):
        """Create branch using real IPSA API - needs bus UID lookup"""
        if not self.m_network:
            return False
        # Need to implement bus UID tracking or lookup by name
        from_uid = self._get_bus_uid_by_name(ipsa_branch.FromBusName)
        to_uid = self._get_bus_uid_by_name(ipsa_branch.ToBusName)
        if from_uid is None or to_uid is None:
            return False
        uid = self.m_network.CreateBranch(from_uid, to_uid, ipsa_branch.Name)
        elem = self.m_network.GetBranch(uid)
        ipsa_branch.configure_in_ipsa(elem)
        return uid

    def AddTransformer(self, ipsa_transformer):
        """Create transformer using real IPSA API"""
        if not self.m_network:
            return False
        from_uid = self._get_bus_uid_by_name(ipsa_transformer.FromBusName)
        to_uid = self._get_bus_uid_by_name(ipsa_transformer.ToBusName)
        if from_uid is None or to_uid is None:
            return False
        uid = self.m_network.CreateTransformer(from_uid, to_uid, ipsa_transformer.Name)
        elem = self.m_network.GetTransformer(uid)
        ipsa_transformer.configure_in_ipsa(elem)
        return uid

    def AddLoad(self, ipsa_load):
        """Create load using real IPSA API"""
        if not self.m_network:
            return False
        bus_uid = self._get_bus_uid_by_name(ipsa_load.BusName)
        if bus_uid is None:
            return False
        uid = self.m_network.CreateLoad(bus_uid, ipsa_load.Name)
        elem = self.m_network.GetLoad(uid)
        ipsa_load.configure_in_ipsa(elem)
        return uid

    def AddSynMachine(self, ipsa_generator):
        """Create synchronous machine using real IPSA API"""
        if not self.m_network:
            return False
        bus_uid = self._get_bus_uid_by_name(ipsa_generator.BusName)
        if bus_uid is None:
            return False
        uid = self.m_network.CreateSynMachine(bus_uid, ipsa_generator.Name)
        elem = self.m_network.GetSynMachine(uid)
        ipsa_generator.configure_in_ipsa(elem)
        return uid
