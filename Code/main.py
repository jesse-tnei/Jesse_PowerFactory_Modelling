#python imports
import os, sys

# Ensure the parent directory is in the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))
#framework imports
from Code import FrameworkInitialiser as f_init
from Code import GlobalEngineRegistry as gbl

#main driver function to initialize the framework and run the load flow
if __name__ == "__main__":
    fw = f_init.FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.DisplayWelcomeMessage()
    gbl.EngineContainer.activatepowerfactorynetwork(r"Personal_Learning\Load Flow [Again]")
    gbl.EngineContainer.activatepowerfactorystudycase("Study Case")
    gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()

    if gbl.StudySettingsContainer.DoLoadFlow:
        gbl.EngineLoadFlowContainer.runloadflow()
        gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
        gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
        gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
        gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
        gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()
        #gbl.EngineLoadFlowContainer.getloadflowresultsdiagramfromnetwork()
        
    if gbl.StudySettingsContainer.DoShortCircuit:
        gbl.EngineShortCircuitContainer.runshortcircuitanalysisforallbusbars()
        gbl.EngineShortCircuitContainer.getandupdateshortcircuitresults()
        print("Short circuit analysis completed.")
