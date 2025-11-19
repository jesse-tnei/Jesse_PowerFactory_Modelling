"""
IPSA Component Classes - Data model classes for IPSA network components
Provides component-specific data structures and configuration methods for IPSA engine integration.
Part of the Jesse PowerFactory Modelling Framework.
"""

import ipsa
import math
from typing import List, Optional


class IPSA_IscBusbar:
    """Model for IscBusbar"""
    def __init__(self):
        self.Name = ''  # Gets the busbar name
        self.NomVoltkV = 0.0  # Nominal bus voltage in kV
        # self.ControlType = 0  # Type of busbar (e.g. slack, PV, PQ, etc.)
        self.Comment = ''  # Comment field

        # Diagram-only attributes (not applied here)
        self.X_coordinate = ''  # X coordinate
        self.Y_coordinate = ''  # Y coordinate
    def configure_in_ipsa(self, obj):
        """
        Apply all busbar settings to the IPSA COM object.
        """
        obj.SetSValue(ipsa.IscBusbar.Name, self.Name)
        obj.SetDValue(ipsa.IscBusbar.NomVoltkV, self.NomVoltkV)
        # obj.SetIValue(ipsa.IscBusbar.ControlType, self.ControlType)
        obj.SetSValue(ipsa.IscBusbar.Comment, self.Comment)


class IPSA_IscBranch:
    """Model for IscBranch"""
    def __init__(self):
        self.FromUID = 0  # Unique component ID for the "From" busbar
        self.ToUID = 0  # Unique component ID for the "To" busbar
        self.FromBusName = ''  # Sending busbar name
        self.ToBusName = ''  # Receiving busbar name
        self.Name = ''  # Branch name
        self.HideLabel = False  # If the branch label should be hidden on the diagram
        self.Type = 0  # Branch/line type (0 = Unset, 1 = Overhead, etc.)
        self.Status = 0  # Line status
        self.ResistancePU = 0.001  # Positive sequence resistance
        self.ReactancePU = 0.001  # Positive sequence reactance
        self.SusceptancePU = 0.0  # Positive sequence susceptance
        self.ZSResistancePU = 0.0  # Zero sequence resistance
        self.ZSReactancePU = 0.0  # Zero sequence reactance
        self.ZeroImpedance = False  # Treated as a zero impedance line
        self.RatingMVAs = [9999.0, 9999.0, 9999.0]  # List of ratings in MVA
        self.LengthKm = 0.001  # Branch length in km
        self.Comment = ''  # Additional comments
    def configure_in_ipsa(self, obj):
        """
        Apply all branch/line settings to the IPSA COM object.
        """
        obj.SetBValue(ipsa.IscBranch.HideLabel, self.HideLabel)              # Boolean HideLabel
        obj.SetIValue(ipsa.IscBranch.Type, self.Type)                        # Integer Type
        obj.SetIValue(ipsa.IscBranch.Status, self.Status)                    # Integer Status
        obj.SetDValue(ipsa.IscBranch.ResistancePU, self.ResistancePU)        # Float ResistancePU
        obj.SetDValue(ipsa.IscBranch.ReactancePU, self.ReactancePU)          # Float ReactancePU
        obj.SetDValue(ipsa.IscBranch.SusceptancePU, self.SusceptancePU)      # Float SusceptancePU
        obj.SetDValue(ipsa.IscBranch.ZSResistancePU, self.ZSResistancePU)    # Float ZSResistancePU
        obj.SetDValue(ipsa.IscBranch.ZSReactancePU, self.ZSReactancePU)      # Float ZSReactancePU
        obj.SetBValue(ipsa.IscBranch.ZeroImpedance, self.ZeroImpedance)      # Boolean ZeroImpedance
        for idx, val in enumerate(self.RatingMVAs):
            obj.SetRatingMVA(idx, val)                                        # List[Float] RatingMVAs
        obj.SetDValue(ipsa.IscBranch.LengthKm, self.LengthKm)                # Float LengthKm
        obj.SetSValue(ipsa.IscBranch.Comment, self.Comment)                  # String Comment


class IPSA_IscTransformer:
    """Model for 2-winding transformers"""
    def __init__(self):
        self.FromBusName = ''  # Sending busbar name
        self.ToBusName = ''  # Receiving busbar name
        self.Name = ''  # Name
        self.Type = 0  # (0 = Unknown, 5 = Super Grid, etc.)
        self.Winding = 2  # (2 = Xx0 i.e. YnYn0)
        self.CoreLossRPU = 0.0  # Core loss resistance
        self.MagnetXPU = 0.0  # Magnetising reactance
        self.TapNominalPC = 0.0  # Nominal tap position
        self.TapStartPC = 0.0  # Start tap position
        self.MinTapPC = 0.0  # Minimum tap position
        self.TapStepPC = 0.0  # Tap step
        self.MaxTapPC = 0.0  # Maximum tap position
        self.LockTap = False
        self.SpecVPU = 0.0  # voltage target
        self.RBWidthPC = 0.0  # voltage sensing relay bandwidth (should be larger than tap step size)
        self.RatingMVA = 0.0  # rating of transformer
        self.Comment = ''  # Additional comments

        # quad-booster specific parameters
        self.PhShiftDeg = 0.0    # initial phase-shift angle (°)
        self.MinPhShiftDeg = 0.0  # minimum angle (°)
        self.MaxPhShiftDeg = 0.0  # maximum angle (°)
        self.PhShiftStepDeg = 0.0  # step size (°)
        self.SpecPowerMW = 0.0   # target real power through the unit (MW)
        self.SpecPowerAtSend = False  # apply SpecPowerMW at the sending end
    def configure_in_ipsa(self, obj):
        """
        Apply all transformer settings to the IPSA COM object.
        """
        # set winding resistance & reactance as "line" values
        obj.SetLineDValue(ipsa.IscBranch.ResistancePU, self.CoreLossRPU)
        obj.SetLineDValue(ipsa.IscBranch.ReactancePU, self.MagnetXPU)

        # transformer-specific parameters
        obj.SetIValue(ipsa.IscTransformer.Type, self.Type)
        obj.SetIValue(ipsa.IscTransformer.Winding, self.Winding)
        obj.SetDValue(ipsa.IscTransformer.TapNominalPC, self.TapNominalPC)
        obj.SetDValue(ipsa.IscTransformer.TapStartPC, self.TapStartPC)
        obj.SetDValue(ipsa.IscTransformer.MinTapPC, self.MinTapPC)
        obj.SetDValue(ipsa.IscTransformer.TapStepPC, self.TapStepPC)
        obj.SetDValue(ipsa.IscTransformer.MaxTapPC, self.MaxTapPC)
        obj.SetBValue(ipsa.IscTransformer.LockTap, self.LockTap)
        obj.SetDValue(ipsa.IscTransformer.SpecVPU, self.SpecVPU)
        obj.SetDValue(ipsa.IscTransformer.RBWidthPC, self.RBWidthPC)
        obj.SetDValue(ipsa.IscTransformer.RatingMVA, self.RatingMVA)
        obj.SetSValue(ipsa.IscTransformer.Comment, self.Comment)

        # quad-booster-specific parameters
        obj.SetDValue(ipsa.IscTransformer.PhShiftDeg, self.PhShiftDeg)
        obj.SetDValue(ipsa.IscTransformer.MinPhShiftDeg, self.MinPhShiftDeg)
        obj.SetDValue(ipsa.IscTransformer.MaxPhShiftDeg, self.MaxPhShiftDeg)
        obj.SetDValue(ipsa.IscTransformer.PhShiftStepDeg, self.PhShiftStepDeg)
        obj.SetDValue(ipsa.IscTransformer.SpecPowerMW, self.SpecPowerMW)
        obj.SetBValue(ipsa.IscTransformer.SpecPowerAtSend, self.SpecPowerAtSend)


class IPSA_Isc3WTransformer:
    """Model for 3-winding transformers"""

    def __init__(self):
        self.FromBusName = ''  # Sending busbar name
        self.ToBusName = ''  # Receiving busbar name
        self.ThreeBusName = ''  # Tertiary busbar name
        self.Name = ''  # Name
        self.Winding = 7  # (7 = xxd11 i.e. Yn0Yn0d11)
        self.W1W2ResistancePU = 0.0
        self.W1W2ReactancePU = 0.0
        self.W1W3ResistancePU = 0.0
        self.W1W3ReactancePU = 0.0
        self.W2W3ResistancePU = 0.0
        self.W2W3ReactancePU = 0.0
        self.W1TapNominalPC = 0.0  # Nominal tap position
        self.W1TapStartPC = 0.0  # Start tap position
        self.W1MinTapPC = 0.0  # Minimum tap position
        self.W1TapStepPC = 0.0  # Tap step
        self.W1MaxTapPC = 0.0  # Maximum tap position
        self.LockTap = False
        self.W1SpecVPU = 0.0  # voltage target
        self.W1RBWidthPC = 0.0  # voltage sensing relay bandwidth (should be larger than tap step size)
        self.W1RatingMVAs = 0.0  # rating of transformer
        self.W2RatingMVAs = 0.0
        self.W3RatingMVAs = 0.0
        self.Comment = ''  # Additional comments

    def configure_in_ipsa(self, obj):
        """
        Apply all transformer settings to the IPSA COM object.
        """
        # set winding resistance & reactance as "line" values
        obj.SetDValue(ipsa.Isc3WTransformer.W1W2ResistancePU, self.W1W2ResistancePU)
        obj.SetDValue(ipsa.Isc3WTransformer.W1W2ReactancePU, self.W1W2ReactancePU)
        obj.SetDValue(ipsa.Isc3WTransformer.W1W3ResistancePU, self.W1W3ResistancePU)
        obj.SetDValue(ipsa.Isc3WTransformer.W1W3ReactancePU, self.W1W3ReactancePU)
        obj.SetDValue(ipsa.Isc3WTransformer.W2W3ResistancePU, self.W2W3ResistancePU)
        obj.SetDValue(ipsa.Isc3WTransformer.W2W3ReactancePU, self.W2W3ReactancePU)

        obj.SetIValue(ipsa.IscTransformer.Winding, self.Winding)
        obj.SetDValue(ipsa.Isc3WTransformer.W1TapNominalPC, self.W1TapNominalPC)
        obj.SetDValue(ipsa.Isc3WTransformer.W1TapStartPC, self.W1TapStartPC)
        obj.SetDValue(ipsa.Isc3WTransformer.W1MinTapPC, self.W1MinTapPC)
        obj.SetDValue(ipsa.Isc3WTransformer.W1TapStepPC, self.W1TapStepPC)
        obj.SetDValue(ipsa.Isc3WTransformer.W1MaxTapPC, self.W1MaxTapPC)
        obj.SetBValue(ipsa.Isc3WTransformer.LockTap, self.LockTap)
        obj.SetDValue(ipsa.Isc3WTransformer.W1SpecVPU, self.W1SpecVPU)
        obj.SetDValue(ipsa.Isc3WTransformer.W1RBWidthPC, self.W1RBWidthPC)
        obj.SetListDValue(ipsa.Isc3WTransformer.W1RatingMVAs, [self.W1RatingMVAs])
        obj.SetListDValue(ipsa.Isc3WTransformer.W2RatingMVAs, [self.W2RatingMVAs])
        obj.SetListDValue(ipsa.Isc3WTransformer.W3RatingMVAs, [self.W3RatingMVAs])


class IPSA_IscLoad:
    """Model for loads"""
    def __init__(self):
        self.BusName = ''  # Connected busbar name
        self.Name = ''  # Name
        self.Status = 0  # Load status
        self.RealMW = 0.0  # Real power in MW
        self.ReactiveMVAr = 0.0  # Reactive power in MVAr
        self.Comment = ''  # Additional comments
    def configure_in_ipsa(self, obj):
        """
        Apply all load settings to the IPSA COM object.
        """
        obj.SetIValue(ipsa.IscLoad.Status, self.Status)
        obj.SetDValue(ipsa.IscLoad.RealMW, self.RealMW)
        obj.SetDValue(ipsa.IscLoad.ReactiveMVAr, self.ReactiveMVAr)
        obj.SetSValue(ipsa.IscLoad.Comment, self.Comment)


class IPSA_IscSynMachine:
    """Model for synchronous machines"""
    def __init__(self):
        self.BusName = ''  # Connected busbar name
        self.Name = ''  # Name
        self.Status = 0  # Machine status
        self.VoltPU = 1.0
        self.VoltBandwidthPC = 5.0
        # self.CtlBusbar = 0
        self.GenMW = 0.0  # Generated real power
        self.GenMVAr = 0.0  # Generated reactive power
        self.GenRatedMW = 0.0  # Rated power
        self.GenMVArMax = 0.0  # Rated reactive power max
        self.GenMVArMin = 0.0  # Rated reactive power min
        self.GenRatedMVA = 0.0  # Rated apparent power
        self.GenTechnology = 0  # Generator technology type
        self.Comment = ''  # Additional commen
    def configure_in_ipsa(self, obj):
        """
        Apply generator (SynMachine) settings to the IPSA COM object.
        """
        obj.SetIValue(ipsa.IscSynMachine.Status, self.Status)
        obj.SetDValue(ipsa.IscSynMachine.VoltPU, self.VoltPU)
        obj.SetDValue(ipsa.IscSynMachine.VoltBandwidthPC, self.VoltBandwidthPC)
        obj.SetDValue(ipsa.IscSynMachine.GenMW, self.GenMW)
        obj.SetDValue(ipsa.IscSynMachine.GenMVAr, self.GenMVAr)
        obj.SetDValue(ipsa.IscSynMachine.GenRatedMW, self.GenRatedMW)
        obj.SetDValue(ipsa.IscSynMachine.GenMVArMax, self.GenMVArMax)
        obj.SetDValue(ipsa.IscSynMachine.GenMVArMin, self.GenMVArMin)
        obj.SetDValue(ipsa.IscSynMachine.GenRatedMVA, self.GenRatedMVA)
        obj.SetIValue(ipsa.IscSynMachine.GenTechnology, self.GenTechnology)
        obj.SetSValue(ipsa.IscSynMachine.Comment, self.Comment)


class IPSA_IscGridInfeed:
    """Model for grid infeeds"""
    def __init__(self):
        self.BusName = ''  # Connected busbar name
        self.Name = ''  # Name of the grid infeed
        self.Status = 0  # Grid infeed status
        self.VoltPU = 0.0
        self.GenMW = 0.0
        self.GenMVAr = 0.0
        self.Comment = ''  # Additional comments

    def configure_in_ipsa(self, obj):
        """
        Apply grid infeed settings to the IPSA COM object.
        """
        obj.SetIValue(ipsa.IscGridInfeed.Status, self.Status)
        obj.SetDValue(ipsa.IscGridInfeed.VoltPU, self.VoltPU)
        obj.SetDValue(ipsa.IscGridInfeed.GenMW, self.GenMW)
        obj.SetDValue(ipsa.IscGridInfeed.GenMVAr, self.GenMVAr)
        obj.SetSValue(ipsa.IscGridInfeed.Comment, self.Comment)


class IPSA_IscStaticVC:
    """Model for static var compensators"""
    def __init__(self):
        self.BusName = ''  # Connected busbar name
        self.Name = ''  # Name of the SVC
        self.Status = 0  # SVC status -1 for out
        self.QMinMVAr = 0.0
        self.QMaxMVAr = 0.0
        self.VminPU = 0.9
        self.VmaxPU = 1.1
        self.IsStatcom = False  # True if the SVC is a STATCOM
    def configure_in_ipsa(self, obj):
        """
        Apply StaticVC (SVC/STATCOM) settings to the IPSA COM object.
        """
        obj.SetIValue(ipsa.IscStaticVC.Status, self.Status)
        obj.SetDValue(ipsa.IscStaticVC.QMinMVAr, self.QMinMVAr)
        obj.SetDValue(ipsa.IscStaticVC.QMaxMVAr, self.QMaxMVAr)
        obj.SetDValue(ipsa.IscStaticVC.VminPU, self.VminPU)
        obj.SetDValue(ipsa.IscStaticVC.VmaxPU, self.VmaxPU)
        obj.SetBValue(ipsa.IscStaticVC.IsStatcom, self.IsStatcom)


class IPSA_IscMechSwCapacitor:
    """Model for mechanically switched capacitors and shunt reactors"""
    def __init__(self):
        self.BusName = ''  # Connected busbar name
        self.Name = ''  # Name
        self.Status = 0  # Capacitor status
        self.ControlMode = 0  # Control mode
        self.CapSteps = 0  # Capacitor steps
        self.IndSteps = 0  # Inductor steps
        self.CapStepSizeMVAr = 0.0  # Capacitor step size
        self.IndStepSizeMVAr = 0.0  # Inductor step size
        self.TargetVoltagePU = 1.0  # Target voltage
        self.BandwidthPC = 10.0  # 10% voltage bandwidth
        self.InitPosition = 0  # Initial position
        self.NominalPosition = 0  # Nominal position
        self.ControlActive = 1  # Voltage or power factor control is active
        # self.ControlledUID = 0
    def configure_in_ipsa(self, obj):
        """
        Apply MSC (shunt reactor) settings to the IPSA COM object.
        """
        obj.SetIValue(ipsa.IscMechSwCapacitor.Status, self.Status)
        obj.SetIValue(ipsa.IscMechSwCapacitor.ControlMode, self.ControlMode)
        obj.SetIValue(ipsa.IscMechSwCapacitor.CapSteps, self.CapSteps)
        obj.SetIValue(ipsa.IscMechSwCapacitor.IndSteps, self.IndSteps)
        obj.SetDValue(ipsa.IscMechSwCapacitor.CapStepSizeMVAr, self.CapStepSizeMVAr)
        obj.SetDValue(ipsa.IscMechSwCapacitor.IndStepSizeMVAr, self.IndStepSizeMVAr)
        obj.SetDValue(ipsa.IscMechSwCapacitor.TargetVoltagePU, self.TargetVoltagePU)
        obj.SetDValue(ipsa.IscMechSwCapacitor.BandwidthPC, self.BandwidthPC)
        obj.SetIValue(ipsa.IscMechSwCapacitor.InitPosition, self.InitPosition)
        obj.SetIValue(ipsa.IscMechSwCapacitor.NominalPosition, self.NominalPosition)
        obj.SetIValue(ipsa.IscMechSwCapacitor.ControlActive, self.ControlActive)


class IPSA_Network_Model:
    """Overall network model - combines all network component objects into a centralized object to be loaded onto the IPSA network"""

    def __init__(self):
        self.list_oBusbar: List[IPSA_IscBusbar] = []
        self.list_oLine: List[IPSA_IscBranch] = []
        self.list_o2WindingTx: List[IPSA_IscTransformer] = []
        self.list_o3WindingTx: List[IPSA_Isc3WTransformer] = []
        self.list_oLoad: List[IPSA_IscLoad] = []
        self.list_oShuntReactorMSC: List[IPSA_IscMechSwCapacitor] = []
        self.list_oSeriesDevices: List[IPSA_IscBranch] = []
        self.list_oSVC: List[IPSA_IscStaticVC] = []
        self.list_oGenerator: List[IPSA_IscSynMachine] = []
        self.list_oGridInfeed: List[IPSA_IscGridInfeed] = []

    @staticmethod
    def latlon_to_xy(lat: float, lon: float):
        """ Converts latitude and longitude to x and y coordinates for diagram plotting """
        lat_min, lat_max = 49.85, 58.7  # Geographic bounds to cover all of Great Britain
        lon_min, lon_max = -5.8, 1.64
        width, height = 12000, 14000  # Diagram dimensions
        x = (lon - lon_min) * (width / (lon_max - lon_min))
        y = (lat_max - lat) * (height / (lat_max - lat_min))
        return x, y

    def get_component_counts(self) -> dict:
        """Return count of each component type"""
        return {
            'busbars': len(self.list_oBusbar),
            'lines': len(self.list_oLine),
            '2w_transformers': len(self.list_o2WindingTx),
            '3w_transformers': len(self.list_o3WindingTx),
            'loads': len(self.list_oLoad),
            'shunt_reactors_msc': len(self.list_oShuntReactorMSC),
            'series_devices': len(self.list_oSeriesDevices),
            'svc_statcom': len(self.list_oSVC),
            'generators': len(self.list_oGenerator),
            'grid_infeeds': len(self.list_oGridInfeed)
        }

    def clear_all_components(self):
        """Clear all component lists"""
        self.list_oBusbar.clear()
        self.list_oLine.clear()
        self.list_o2WindingTx.clear()
        self.list_o3WindingTx.clear()
        self.list_oLoad.clear()
        self.list_oShuntReactorMSC.clear()
        self.list_oSeriesDevices.clear()
        self.list_oSVC.clear()
        self.list_oGenerator.clear()
        self.list_oGridInfeed.clear()