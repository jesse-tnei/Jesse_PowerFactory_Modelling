from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineLoadFlowContainer import EngineLoadFlowContainer as BaseEngineLoadFlowContainer


class EnginePowerFactoryLoadFlow(BaseEngineLoadFlowContainer):
    def __init__(self):
        super().__init__()
        self.powerfactoryloadflowobject = gbl.EngineContainer.m_pFApp.GetFromStudyCase("ComLdf")
    #__________________________ENGINE POWER FACTORY LOAD FLOW METHODS________________________
    def runloadflow(self):
        """This method runs the load flow analysis."""
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Running PowerFactory Load Flow Analysis...")
        ierr = self.powerfactoryloadflowobject.Execute()
        if ierr != 0:
            gbl.Msg.add_error("PowerFactory Load Flow Analysis failed with error code: {}".format(ierr))
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("PowerFactory Load Flow Analysis completed successfully.")
        return True
    def getloadflowresults(self):
        """This method retrieves the results of the load flow analysis."""
        pass