# This serves as the global engine container for the application.
# The user gets to choose what engine they want to use through the studysettings file
# Depending on their choice, this will be the interface to that engine.

import string
from Framework import GlobalRegistry as gbl
#from FrameworkInitialiser import FrameworkInitialiser

class EngineContainer:
    def __init__(self):
        self.msg = gbl.Msg
        self.m_active_network = None
        self.m_strTypeOfEngine = "NoEngine"
        self.m_strVersion = "1.0.0"
        self.m_strAuthor = "Unknown"
        
        self.m_NetworkToDataModelInterface = None
        self.m_oNetworkStudySettings = None
        self.m_oNetworkLoadFlowRunInstanceInstance = None
        self.m_oNetworkHarmonicsRunInstanceInstance = None
        self.m_oNetworkShortCircuitRunInstance = None
        self.m_oNetworkFaultAnalysisRunInstance = None
        
        #__________________________ENGINE INITIALIZATION________________________
        def IsIPSA():
            """initialises IPSA to false such that when inherited, the engine can set it to true if it is an IPSA engine"""
            return False
        def IsPowerFactory():
            """initialises PowerFactory to false such that when inherited, the engine can set it to true if it is a PowerFactory engine"""
            return False
        def IsOpenDSS():
            """initialises OpenDSS to false such that when inherited, the engine can set it to true if it is an OpenDSS engine"""
            return False
        
        
        #__________________________ENGINE VERSION INFORMATION________________________
        def GetVersion(self):
            """Returns the version of the engine"""
            return self.m_strVersion
        def GetAuthor(self):
            """Returns the author of the engine"""
            return self.m_strAuthor
        def GetTypeOfEngine(self):
            """Returns the type of engine"""
            return self.m_strTypeOfEngine
        
        
        #__________________________GENERIC ENGINE INTERFACE METHODS________________________
        def ImportNetworkModel(self, strFileName):
            """Imports the network model from the specified file"""
            self.msg.AddError("ImportNetworkModel not implemented in base class")
            return False
        
        def ExportNetworkModel(self, strFileName):
            """Exports the network model to the specified file"""
            self.msg.AddError("ExportNetworkModel not implemented in base class")
            return False
        
        def OpenNetwork(self, strNetworkName):
            """Opens the specified network"""
            self.msg.AddError("OpenNetwork not implemented in base class")
            return False
        
        def CloseNetwork(self):
            """Closes the currently open network"""
            self.msg.AddError("CloseNetwork not implemented in base class")
            return False
        
        
        #__________________________GENERIC ENGINE STUDY TYPE METHODS________________________
        def RunLoadFlow(self, strNetworkName):
            """Runs a load flow analysis on the specified network"""
            self.msg.AddError("RunLoadFlow not implemented in base class")
            return False
        
        def RunHarmonics(self, strNetworkName):
            """Runs a harmonics analysis on the specified network"""
            self.msg.AddError("RunHarmonics not implemented in base class")
            return False
        
        def RunShortCircuit(self, strNetworkName):
            """Runs a short circuit analysis on the specified network"""
            self.msg.AddError("RunShortCircuit not implemented in base class")
            return False
        def RunFaultAnalysis(self, strNetworkName):
            """Runs a fault analysis on the specified network"""
            self.msg.AddError("RunFaultAnalysis not implemented in base class")
            return False
        
        
        #__________________________GENERIC ENGINE DATA MODEL METHODS________________________
        def CheckNetworkOpen(self):
            """Checks if a network is currently open"""
            if self.m_active_network is None:
                self.msg.AddError("No network is currently open")
                return False
            return True
        
        def TransferDataFromNetworkToDataModel(self):
            """Transfers data from the active network to the data model"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                bOK = self.m_NetworkToDataModelInterface.TransferDataFromNetworkToDataModel()
            
            return bOK
        
        def TransferDataFromDataModelToNetwork(self):
            """Transfers data from the data model to the active network"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                bOK = self.m_NetworkToDataModelInterface.TransferDataFromDataModelToNetwork()
            return bOK
        
        def GetBusbarsFromNetwork(self):
            """Retrieves busbars from the engine"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetBusbarsFromNetwork()
            return bOK
        
        def GetBranchesFromNetwork(self):
            """Retrieves branches from the engine"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetBranchesFromNetwork()
            return bOK
        
        def GetGeneratorsFromNetwork(self):
            """Retrieves generators from the engine"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetGeneratorsFromNetwork()
            return bOK
        
        def GetLoadsFromNetwork(self):
            """Retrieves loads from the engine"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetLoadsFromNetwork()
            return bOK
        
        def AddGeneratorToNetwork(self, generator_data):
            """Adds a generator to the network"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.AddGeneratorToNetwork(generator_data)
            return bOK
        
        def AddLoadToNetwork(self, load_data):
            """Adds a load to the network"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.AddLoadToNetwork(load_data)
            return bOK
        
        def SetNetworkBusbarValues(self, dmBusbar):
            """Sets busbar values in the network"""
            bOK = self.CheckNetworkOpen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.SetNetworkBusbarValues(dmBusbar)
            return bOK
        
        
        
        #__________________________ANALYSIS RESULTS METHODS________________________
        def GetLoadFlowResults(self):
            """Retrieves load flow results from the engine"""
            bOK = self.CheckNetworkOpen() and self.m_oNetworkLoadFlowRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetLoadFlowResults()
            self.msg.AddError("Load flow results not available")
            return bOK
        
        def GetHarmonicsResults(self):
            """Retrieves harmonics results from the engine"""
            bOK = self.CheckNetworkOpen() and self.m_oNetworkHarmonicsRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetHarmonicsResults()
            self.msg.AddError("Harmonics results not available")
            return bOK
        
        def GetShortCircuitResults(self):
            """Retrieves short circuit results from the engine"""
            bOK = self.CheckNetworkOpen() and self.m_oNetworkShortCircuitRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetShortCircuitResults()
            self.msg.AddError("Short circuit results not available")
            return bOK
        
        def GetFaultAnalysisResults(self):
            """Retrieves fault analysis results from the engine"""
            bOK = self.CheckNetworkOpen() and self.m_oNetworkFaultAnalysisRunInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.GetFaultAnalysisResults()
            self.msg.AddError("Fault analysis results not available")
            return bOK
        
# if __name__ == "__main__":
#     fw = FrameworkInitialiser()
#     fw.initialize()
#     enginebasetemplateinstance = EngineContainer()
#     enginebasetemplateinstance.msg.OutputSplash()
    