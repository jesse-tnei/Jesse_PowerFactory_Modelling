#python imports
import os, sys
import time

# Ensure the parent directory is in the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))

#framework imports
from Code import FrameworkInitialiser as f_init
from Code import GlobalEngineRegistry as gbl

#main driver function to initialize the framework and run the load flow
if __name__ == "__main__":
    fw = f_init.FrameworkInitialiser()
    if gbl.AppSettingsContainer.EnableAPI and gbl.AppSettingsContainer.EnableWebInterface:
        fw.initializefullproduct()
        gbl.Msg.DisplayWelcomeMessage()
        gbl.EngineContainer.activatepowerfactorynetwork(r"0.  PM_Anderson_9_Bus_System")
        gbl.EngineContainer.activatepowerfactorystudycase("Study Case")
        gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
        if gbl.StudySettingsContainer.DoLoadFlow:
            for branch in gbl.DataModelManager.Branch_TAB:
                if branch.IsTransformer:
                    gbl.DataModelInterfaceContainer.switchtransformertapstatus(branch, 1, 0)
                    tapchangerattributes = {
                        'type': 0,  #0 ratio/asym
                        'controlside': 0,  #0HV
                        'additionvoltpertap': 1,  #percentage
                        'tapphase': 0,  #phase angle
                        'neutralposition': 5,
                        'mintapposition': 10,
                        'maxtapposition': 0
                    }
                    gbl.DataModelInterfaceContainer.settransformervaluestonetwork(
                        branch, **tapchangerattributes)
            loadflowsettings = {
                'CalculationMethod': 0,
                'AutomaticPhaseShifterTapAdjustment': 0,
                'AutomaticTapAdjustmentTransformer': 1,
            }
            gbl.EngineLoadFlowContainer.runloadflow(**loadflowsettings)
            #gbl.EngineLoadFlowContainer.runloadflow()
            gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
            gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
            gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
            gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
            gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()
            #gbl.EngineLoadFlowContainer.getloadflowresultsdiagramfromnetwork()
        if gbl.StudySettingsContainer.DoShortCircuit:
            gbl.EngineShortCircuitContainer.runshortcircuitanalysisforallbusbars()
            gbl.EngineShortCircuitContainer.getandupdateshortcircuitresults()
            gbl.EngineShortCircuitContainer.getgenshortcircuitcontribution()
            print("Short circuit analysis completed.")

    if gbl.AppSettingsContainer.EnableWebInterface and not gbl.AppSettingsContainer.EnableAPI:
        fw.initialize_web_only()
        print("press Control+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down web interface...")
