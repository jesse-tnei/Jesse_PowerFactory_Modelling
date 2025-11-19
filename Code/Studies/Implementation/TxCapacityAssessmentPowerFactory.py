from Code import GlobalEngineRegistry as gbl
from Code.Studies.BaseTemplates.TxCapacityAssessmentBase import TxCapacityAssessmentBase


class TxCapacityAssessmentPowerFactory(TxCapacityAssessmentBase):
    def __init__(self):
        TxCapacityAssessmentBase.__init__(self)
.        self.msg = gbl.Msg
    def initializestudy(self):
        if not gbl.EngineContainer:
            raise RuntimeError("The PowerFactory engine has not been initialized yet.")
        self.engine = gbl.EngineContainer
        self.datamodelinterface = gbl.DataModelInterfaceContainer
        self.loadflow = gbl.EngineLoadFlowContainer
        self.initialized = True
        return True
    def runcapacityassessment(self):
        """Activates the PowerFactory network and runs the capacity assessment."""
        bOK = False
        bOK = self.initializestudy()
        if bOK:
            strNetworkName = input("Enter the name of the PowerFactory project to activate: ")
            bOK = self.engine.activatepowerfactorynetwork(strNetworkName)
        if bOK:
            strStudyName = input("Enter the name of the study to run: ")
            bOK = self.engine.activatepowerfactorystudycase(strStudyName)
        if bOK:
            bOK = gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
        if bOK:
            offline = True
            online = not offline
            for branch in gbl.DataModelManager.Branch_TAB:
                if branch.ON:
                    bOK = gbl.DataModelInterfaceContainer.switchbranchstatus(branch, offline)
                    if bOK:
                        bOK = self.loadflow.runloadflow()
                    if bOK:
                        bOK = self.loadflow.getallloadflowresults()
                    if bOK:
                        bOK = gbl.DataModelInterfaceContainer.switchbranchstatus(branch, online)
        return bOK
