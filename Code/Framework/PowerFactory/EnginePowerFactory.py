import os, sys
import datetime
import string
from typing import Callable
import psutil
import wmi
import pythoncom

from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineContainer import EngineContainer as EngineContainer

# disable pylint warnings for this file
# pylint: disable=C0103

class EnginePowerFactory(EngineContainer):
    """Engine class for PowerFactory"""
    def __init__(self, preferred_version = 2023):
        EngineContainer.__init__(self)
        #get user input for preferred version
        self.m_ChosenVersion = preferred_version
        #Dependency injection for globalised messaging
        self.m_oMsg = gbl.Msg
        # PowerFactory version and type of engine - for display purposes
        self.m_pFApp = None # start by getting the PowerFactory application instance
        self.m_strTypeOfEngine = "Not Specified"
        self.m_strVersion = "Not Specified"
        self.m_strAuthor = "Not Specified"
        self.m_active_network = None
        # PowerFactory study types - initialised to None
        self.m_NetworkToDataModelInterface = None
        self.m_oNetworkStudySettings = None
        self.m_oNetworkLoadFlowRunInstance = None
        self.m_oNetworkHarmonicsRunInstance = None
        self.m_oNetworkShortCircuitRunInstance = None
        self.m_oNetworkFaultAnalysisRunInstance = None
        #allowed PowerFactory versions
        self.m_AllowableVersions = {
            2023: " PowerFactory 2023 V0.0.1",
            2024: "PowerFactory 2024 V0.0.1",
            2025: "PowerFactory 2025 V0.0.1"
        }
        # PowerFactory installation paths
        self.m_PowerFactoryInstallPath2023 = "C:\\Program Files\\DIgSILENT\\PowerFactory 2023 SP5\\Python\\3.11"
        self.m_PowerFactoryInstallPath2024 =r"C:\Program Files\DIgSILENT\PowerFactory 2024 SP4\Python\3.11"
        self.m_PowerFactoryInstallPath2025 = "C:\\Program Files\\DIgSILENT\\PowerFactory 2025"
        # check to destroy any running PowerFactory processes
        self._killrunningpowerfactoryprocesses("PowerFactory.exe")
        self.ShowLoadedApplication = False  # Show the loaded application
        self.loadpowerfactoryversion(self.m_ChosenVersion)

    def ispowerfactory(self):
        """Check if this is a PowerFactory engine"""
        return True
    def getversion(self):
        """Get the PowerFactory version"""
        return self.m_strVersion
    def _killrunningpowerfactoryprocesses(self, process_name:str) -> None:
        """Kill all running PowerFactory processes"""
        process_IDs = self._findpowerfactoryrunningprocessID(process_name)
        if process_IDs == -1:
            return
        for process_ID in process_IDs:
            try:
                parent_process = psutil.Process(process_ID)
                for child in parent_process.children(recursive=True):
                    child.kill()
                parent_process.kill()
                self.m_oMsg.AddInfo(f"Killed PowerFactory process with ID {process_ID}")
            except psutil.NoSuchProcess:
                self.m_oMsg.AddWarning(f"Process with ID {process_ID} no longer exists")
            except Exception as e:
                self.m_oMsg.AddError(f"Failed to kill process {process_ID}: {e}")

    def _findpowerfactoryrunningprocessID(self, process_name:str):
        "Helper function to find the PowerFactory process ID(s)"
        pythoncom.CoInitialize()
        c = wmi.WMI()
        process_IDs = []
        for process in c.Win32_Process():
            if process.Name == process_name:
                process_IDs.append(process.ProcessID)
        if len(process_IDs) == 0:
            self.m_oMsg.AddInfo(f"No running process found with name {process_name}")
            return -1
        elif len(process_IDs) > 1:
            self.m_oMsg.AddWarning(f"Multiple processes found with name {process_name}. Using the first one: {process_IDs[0]}")
        return process_IDs

    def loadpowerfactoryversion(self, version: int):
        """Load the specified PowerFactory version"""
        if version not in self.m_AllowableVersions:
            self.m_oMsg.AddError(f"Unsupported PowerFactory version: {version}")
            return False
        install_path = ""
        if version == 2023:
            install_path = self.m_PowerFactoryInstallPath2023
        elif version == 2024:
            install_path = self.m_PowerFactoryInstallPath2024
        elif version == 2025:
            install_path = self.m_PowerFactoryInstallPath2025
        if not os.path.exists(install_path):
            self.m_oMsg.AddError(f"PowerFactory installation path does not exist: {install_path}")
            return False
        self._loadpowerfactory(install_path, version)
        return True

    def _loadpowerfactory(self, install_path: str, version: int):
        """Load the PowerFactory Python environment"""
        sys.path.append(install_path)
        try:
            import powerfactory as pf
            self.m_pFApp = pf.GetApplicationExt()
            if not self.m_pFApp:
                raise ImportError("Failed to get PowerFactory application instance")
            if self.ShowLoadedApplication:
                self.m_pFApp.Show()
            self.m_strTypeOfEngine = "Automated PowerFactory Tool"
            self.m_strVersion = self.m_AllowableVersions[version]
            self.m_oMsg.AddInfo(f"PowerFactory {version} environment loaded successfully")
        except ImportError as e:
            self.m_oMsg.AddError(f"Failed to load PowerFactory environment: {e}")
    def opennetwork(self, **kwargs):
        """Open a PowerFactory network by name"""
        bOK = False
        strNetworkName = kwargs.get("projectname", None)
        strStudyCaseName = kwargs.get("studycasename", None)
        bOK = self.activatepowerfactorynetwork(strNetworkName)
        if bOK:
            bOK = self.activatepowerfactorystudycase(strStudyCaseName)
        return bOK
    def createnetwork(self, **kwargs):
        """Create a new PowerFactory network"""
        strNetworkName = kwargs.get("projectname", None)
        if not strNetworkName:
            self.m_oMsg.AddError("Project name is required for network creation")
            return False
        if not self.m_pFApp:
            self.m_oMsg.AddError("PowerFactory application is not initialized")
            return False
        try:
            self.m_pFApp.ClearOutputWindow()
            proj = self.m_pFApp.CreateProject(strNetworkName, 'Grid')
            if not proj:
                self.m_oMsg.AddError(f"Failed to create PowerFactory project: {strNetworkName}")
                return False
            return self.activatepowerfactorynetwork(strNetworkName)
        except Exception as e:
            self.m_oMsg.AddError(f"Exception while creating project '{strNetworkName}': {e}")
            return False
    def activatepowerfactorynetwork(self, network_name: str):
        """Activate a PowerFactory network by name"""
        if not self.m_pFApp:
            self.m_oMsg.AddError("PowerFactory application is not initialized")
            return False
        try:
            network = self.m_pFApp.ActivateProject(network_name) # returns 0 if activated successfully
            if network:
                self.m_oMsg.AddError(f"Network '{network_name}' not found")
                return False
            self.m_active_network = self.m_pFApp.GetActiveProject()
            self.m_oMsg.AddInfo(f"Activated PowerFactory network: {self.m_active_network.loc_name}")
            return True
        except Exception as e:
            self.m_oMsg.AddError(f"Failed to activate network '{network_name}': {e}")
            return False

    def activatepowerfactorystudycase(self, study_case_name: str):
        """Activate a PowerFactory study case by name"""
        activeStudyCase = self.checkactivestudycase()
        if activeStudyCase and activeStudyCase.loc_name == study_case_name:
            self.m_oMsg.AddInfo(f"Study case '{study_case_name}' is already active")
            return True
        return self.activatepowerfactoryitem("StudyCase", study_case_name, ".IntCase")

    def activatepowerfactoryitem(self, itemType:str, itemName:str, itemSuffix:str):
        """Activate a PowerFactory item by name"""
        if not self.m_active_network:
            self.m_oMsg.AddError("No active PowerFactory network")
            return False
        try:
            pfFolder = self._getpowerfactoryfolderbytype(itemType)
            if not pfFolder:
                self.m_oMsg.AddError(f"Failed to get PowerFactory folder for type '{itemType}'")
                return False
            pfItems = pfFolder.GetContents(f"{itemName}{itemSuffix}")
            if not pfItems:
                self.m_oMsg.AddError(f"Item '{itemName}{itemSuffix}' not found in folder '{pfFolder.loc_name}'")
                return False
            pfItem = None
            for item in pfItems:
                if item.loc_name == itemName:
                    pfItem = item
                    break
            if pfItem is None:
                self.m_oMsg.AddError(f"Item '{itemName}{itemSuffix}' not found after search")
                return False
            pfItemActivationFailFlag = pfItem.Activate()
            if pfItemActivationFailFlag:
                self.m_oMsg.AddError(f"Failed to activate item '{itemName}{itemSuffix}'")
                return False
            self.m_oMsg.AddInfo(f"Activated PowerFactory item: {pfItem.loc_name}")
            return True
        except Exception as e:
            self.m_oMsg.AddError(f"Failed to activate item '{itemName}{itemSuffix}': {e}")
            return False

    def _getpowerfactoryfolderbytype(self, itemType:str) -> object:
        folder_map = {
            'EquipmentType': 'equip',
            'NetworkModel': 'netmod',
            'OperationalLibrary': 'oplib',
            'OperationalScenario': 'scen',
            'ScriptLibrary': 'script',
            'StudyCase': 'study',
            'Template': 'templ',
            'NetworkData': 'netdat',
            'Diagram': 'dia',
            'Variation': 'scheme',
            'CBRating': 'cbrat',
            'ThermalRating': 'therm',
            'RunningArrangement': 'ra',
            'MVArLimitCurve': 'mvar',
            'Outage': 'outage',
            'Fault': 'fault',
            'Characteristics': 'chars'
        }
        if not self.m_active_network:
            self.m_oMsg.AddError("No active PowerFactory network")
            return None
        try:
            pfFolderName = folder_map.get(itemType, None)
            if pfFolderName:
                return self.m_pFApp.GetProjectFolder(pfFolderName)
            self.m_oMsg.AddError(f"Invalid item type: {itemType}")
            return None
        except Exception as e:
            self.m_oMsg.AddError(f"Failed to get PowerFactory folder for type '{itemType}': {e}")
            return None

    def checkactivestudycase(self) -> object:
        """Check if an active study case is available"""
        if not self.m_active_network:
            self.m_oMsg.AddError("No active PowerFactory network")
            return False
        return self.m_pFApp.GetActiveStudyCase()

# To run this as a standalone script, make sure your terminal points to the Code directory otherwise the imports will fail
if __name__ == "__main__":
    engine = EnginePowerFactory()
    engine.msg.OutputSplash()
