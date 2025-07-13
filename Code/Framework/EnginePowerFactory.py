import os, sys
import datetime
import string
from typing import Callable
import psutil
import wmi
import pythoncom

from Framework import GlobalRegistry as gbl
from Framework.Engine import EngineContainer as EngineContainer

class EnginePowerFactory(EngineContainer):
    """Engine class for PowerFactory"""
    
    def __init__(self, preferred_version = 0):
        EngineContainer.__init__(self)
        self.m_oMsg = gbl.Msg
        self.m_active_network = None
        self.m_strTypeOfEngine = "PowerFactory"
        self.m_strVersion = "0.0.0"
        self.m_strAuthor = "Kamau Ngugi"
        
        self.m_NetworkToDataModelInterface = None
        self.m_oNetworkStudySettings = None
        self.m_oNetworkLoadFlowRunInstanceInstance = None
        self.m_oNetworkHarmonicsRunInstanceInstance = None
        self.m_oNetworkShortCircuitRunInstance = None
        self.m_oNetworkFaultAnalysisRunInstance = None
        
        self.m_ChosenVersion = preferred_version
        
        self.m_AllowableVersions = {
            0: "0.0.0 - PowerFactory Not Loaded",  # Default version
            2023: "1.0.0 - PowerFactory 2023",
            2024: "2.0.0 - PowerFactory 2024",
            2025: "3.0.0 - PowerFactory 2025"
        }
        
        # installation paths
        self.m_PowerFactoryInstallPath2023 = "C:\\Program Files\\DIgSILENT\\PowerFactory 2023 SP5\\Python\\3.11"
        self.m_PowerFactoryInstallPath2024 = "C:\\Program Files\\DIgSILENT\\PowerFactory 2024"
        self.m_PowerFactoryInstallPath2025 = "C:\\Program Files\\DIgSILENT\\PowerFactory 2025"
        
        
    def IsPowerFactory(self):
        """Check if this is a PowerFactory engine"""
        return True
    def GetVersion(self):
        pass
        
        
        
        
        
        

# To run this as a standalone script, make sure your terminal points to the Code directory otherwise the imports will fail        

if __name__ == "__main__":
    engine = EnginePowerFactory()
    engine.msg.OutputSplash()
