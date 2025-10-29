# Engine wrapper for IPSA / PyIPSA
import os
from typing import Optional

import ipsa

from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineContainer import EngineContainer as EngineContainer


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
        self._initialise_ipsa_interface()

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
