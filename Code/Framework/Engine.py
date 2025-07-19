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
        def isipsa():
            """initialises IPSA to false such that when inherited, the engine can set it to true if it is an IPSA engine"""
            return False

        def ispowerfactory():
            """initialises PowerFactory to false such that when inherited, the engine can set it to true if it is a PowerFactory engine"""
            return False

        def isopendss():
            """initialises OpenDSS to false such that when inherited, the engine can set it to true if it is an OpenDSS engine"""
            return False

        #__________________________ENGINE VERSION INFORMATION________________________
        def getversion(self):
            """Returns the version of the engine"""
            return self.m_strVersion

        def getauthor(self):
            """Returns the author of the engine"""
            return self.m_strAuthor

        def gettypeofengine(self):
            """Returns the type of engine"""
            return self.m_strTypeOfEngine

        #__________________________GENERIC ENGINE INTERFACE METHODS________________________
        def importnetworkmodel(self, strFileName):
            """Imports the network model from the specified file"""
            self.msg.adderror("ImportNetworkModel not implemented in base class")
            return False

        def exportnetworkmodel(self, strFileName):
            """Exports the network model to the specified file"""
            self.msg.adderror("ExportNetworkModel not implemented in base class")
            return False

        def opennetwork(self, strNetworkName):
            """Opens the specified network"""
            self.msg.adderror("OpenNetwork not implemented in base class")
            return False

        def closenetwork(self):
            """Closes the currently open network"""
            self.msg.adderror("CloseNetwork not implemented in base class")
            return False

        #__________________________GENERIC ENGINE STUDY TYPE METHODS________________________
        def runloadflow(self, strNetworkName):
            """Runs a load flow analysis on the specified network"""
            self.msg.adderror("RunLoadFlow not implemented in base class")
            return False

        def runharmonics(self, strNetworkName):
            """Runs a harmonics analysis on the specified network"""
            self.msg.adderror("RunHarmonics not implemented in base class")
            return False

        def runshortcircuit(self, strNetworkName):
            """Runs a short circuit analysis on the specified network"""
            self.msg.adderror("RunShortCircuit not implemented in base class")
            return False

        def runfaultanalysis(self, strNetworkName):
            """Runs a fault analysis on the specified network"""
            self.msg.adderror("RunFaultAnalysis not implemented in base class")
            return False

        #__________________________GENERIC ENGINE DATA MODEL METHODS________________________
        def checknetworkopen(self):
            """Checks if a network is currently open"""
            if self.m_active_network is None:
                self.msg.adderror("No network is currently open")
                return False
            return True

        def transferdatafromnetworktodatamodel(self):
            """Transfers data from the active network to the data model"""
            bOK = self.checknetworkopen()
            if bOK:
                bOK = self.m_NetworkToDataModelInterface.transferdatafromnetworktodatamodel()

            return bOK

        def transferdatafromdatamodeltonetwork(self):
            """Transfers data from the data model to the active network"""
            bOK = self.checknetworkopen()
            if bOK:
                bOK = self.m_NetworkToDataModelInterface.transferdatafromdatamodeltonetwork()
            return bOK

        def getbusbarsfromnetwork(self):
            """Retrieves busbars from the engine"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.getbusbarsfromnetwork()
            return bOK

        def getbranchesfromnetwork(self):
            """Retrieves branches from the engine"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.getbranchesfromnetwork()
            return bOK

        def getgeneratorsfromnetwork(self):
            """Retrieves generators from the engine"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.getgeneratorsfromnetwork()
            return bOK

        def getloadsfromnetwork(self):
            """Retrieves loads from the engine"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.getloadsfromnetwork()
            return bOK

        def addgeneratortonetwork(self, generator_data):
            """Adds a generator to the network"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.addgeneratortonetwork(generator_data)
            return bOK

        def addloadtonetwork(self, load_data):
            """Adds a load to the network"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.addloadtonetwork(load_data)
            return bOK

        def setnetworkbusbarvalues(self, dmBusbar):
            """Sets busbar values in the network"""
            bOK = self.checknetworkopen()
            if bOK:
                return self.m_oNetworkToDataModelInterface.setnetworkbusbarvalues(dmBusbar)
            return bOK

        #__________________________ANALYSIS RESULTS METHODS________________________
        def getloadflowresults(self):
            """Retrieves load flow results from the engine"""
            bOK = self.checknetworkopen() and self.m_oNetworkLoadFlowRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.getloadflowresults()
            self.msg.adderror("Load flow results not available")
            return bOK

        def getharmonicsresults(self):
            """Retrieves harmonics results from the engine"""
            bOK = self.checknetworkopen() and self.m_oNetworkHarmonicsRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.getharmonicsresults()
            self.msg.adderror("Harmonics results not available")
            return bOK

        def getshortcircuitresults(self):
            """Retrieves short circuit results from the engine"""
            bOK = self.checknetworkopen() and self.m_oNetworkShortCircuitRunInstanceInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.getshortcircuitresults()
            self.msg.adderror("Short circuit results not available")
            return bOK

        def getfaultanalysisresults(self):
            """Retrieves fault analysis results from the engine"""
            bOK = self.checknetworkopen() and self.m_oNetworkFaultAnalysisRunInstance
            if bOK:
                return self.m_oNetworkToDataModelInterface.getfaultanalysisresults()
            self.msg.adderror("Fault analysis results not available")
            return bOK


# if __name__ == "__main__":
#     fw = FrameworkInitialiser()
#     fw.initialize()
#     enginebasetemplateinstance = EngineContainer()
#     enginebasetemplateinstance.msg.OutputSplash()
