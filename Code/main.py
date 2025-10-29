#python imports
import os, sys
import time

# Ensure the parent directory is in the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))

#framework imports
from Code import FrameworkInitialiser as f_init
from Code import GlobalEngineRegistry as gbl
#from Studies.Implementation import TxCapacityAssessmentPowerFactory

#main driver function to initialize the framework and perform tests
if __name__ == "__main__":
    # __________________________STUDY PROCESS TESTS________________________________#
    # initialise powerfactory framework
    fw = f_init.FrameworkInitialiser()
    fw.initializeproduct(webinterfaceonly=True)
    gbl.Msg.DisplayWelcomeMessage()
    if gbl.StudySettingsContainer.ipsa:
        fw.initialize_backend("ipsa")
        gbl.EngineContainer.opennetwork(
            filepath= gbl.StudySettingsContainer.ipsafilename)
        gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
        print("Completed opening network.")
        if gbl.StudySettingsContainer.DoLoadFlow:
            gbl.EngineLoadFlowContainer.runloadflow(calculation_method = 'AC')
            gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
            gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
            gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
            gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()
            gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
            print("Completed running IPSA load flow.")

    if gbl.StudySettingsContainer.powerfactory:
        fw.initialize_backend("powerfactory")
        gbl.EngineContainer.opennetwork(projectname="0.  PM_Anderson_9_Bus_System",
                                        studycasename="01- Load Flow")
        gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
        if gbl.StudySettingsContainer.DoLoadFlow:
            for branch in gbl.DataModelManager.Branch_TAB:
                if branch.IsTransformer:
                    gbl.DataModelInterfaceContainer.switchtransformertapstatus(branch, 0, 0)
                    tapchangerattributes = {
                        'type': 0,  #0 ratio/asym
                        'controlside': 0,  #0HV
                        'additionvoltpertap': 1,  #percentage
                        'tapphase': 0,  #phase angle
                        'neutralposition': 0,
                        'mintapposition': -10,
                        'maxtapposition': 10
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
            print("Powerfactory load flow completed.")
    # #run capacity assessment
    # txca = TxCapacityAssessmentPowerFactory.TxCapacityAssessmentPowerFactory()
    # txca.runcapacityassessment()
    # print("Completed running PowerFactory capacity assessment.")



    # #_______________________IPSA PROCESSES________________________________#
    # fw = f_init.FrameworkInitialiser()
    # fw.initializeproduct(webinterfaceonly=True)
    # gbl.Msg.DisplayWelcomeMessage()
    # if gbl.StudySettingsContainer.ipsa:
    #     gbl.EngineContainer.opennetwork(
    #         filepath= gbl.StudySettingsContainer.ipsafilename)
    #     gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
    #     print("Completed opening network.")
    #     if gbl.StudySettingsContainer.DoLoadFlow:
    #         gbl.EngineLoadFlowContainer.runloadflow(calculation_method = 'AC')
    #         gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
    #         gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
    #         gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
    #         gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()
    #         gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
    #         print("Completed running load flow.")

#   #___________________POWERFACTORY TESTS_______________________________#
#     fw = f_init.FrameworkInitialiser()
#     fw.initializefullproduct()
#     gbl.Msg.DisplayWelcomeMessage()
#     if gbl.StudySettingsContainer.powerfactory:
#         gbl.EngineContainer.opennetwork(projectname="0.  PM_Anderson_9_Bus_System",
#                                         studycasename="01- Load Flow")
#         gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
#         if gbl.StudySettingsContainer.DoLoadFlow:
#             for branch in gbl.DataModelManager.Branch_TAB:
#                 if branch.IsTransformer:
#                     gbl.DataModelInterfaceContainer.switchtransformertapstatus(branch, 0, 0)
#                     tapchangerattributes = {
#                         'type': 0,  #0 ratio/asym
#                         'controlside': 0,  #0HV
#                         'additionvoltpertap': 1,  #percentage
#                         'tapphase': 0,  #phase angle
#                         'neutralposition': 0,
#                         'mintapposition': -10,
#                         'maxtapposition': 10
#                     }
#                     gbl.DataModelInterfaceContainer.settransformervaluestonetwork(
#                         branch, **tapchangerattributes)
#             loadflowsettings = {
#                 'CalculationMethod': 0,
#                 'AutomaticPhaseShifterTapAdjustment': 0,
#                 'AutomaticTapAdjustmentTransformer': 1,
#             }
#             gbl.EngineLoadFlowContainer.runloadflow(**loadflowsettings)
#             #gbl.EngineLoadFlowContainer.runloadflow()
#             gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
#             gbl.EngineLoadFlowContainer.getandupdatelineloadflowresults()
#             gbl.EngineLoadFlowContainer.getandupdatetransformerflowresults()
#             gbl.EngineLoadFlowContainer.getandupdateloadflowgeneratorresults()
#             gbl.EngineLoadFlowContainer.getandupdateloadsloadflowresults()
#             #gbl.EngineLoadFlowContainer.getloadflowresultsdiagramfromnetwork()
#         # if gbl.StudySettingsContainer.DoShortCircuit:
#         #     gbl.EngineShortCircuitContainer.runshortcircuitanalysisforallbusbars()
#         #     gbl.EngineShortCircuitContainer.getandupdateshortcircuitresults()
        #     gbl.EngineShortCircuitContainer.getgenshortcircuitcontribution()
        #     print("Short circuit analysis completed.")

    #_______________WEB-INTERFACE PROCESSES___________________________#
    # fw = f_init.FrameworkInitialiser()
    # fw.initializefullproduct()
    # gbl.Msg.DisplayWelcomeMessage()
    # if gbl.StudySettingsContainer.webinterface:
    #     fw.initialize_web_only()
    #     print("press Control+C to exit.")
    #     try:
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         print("Shutting down web interface...")


    #____________OVERALL TOOL INTEGRATION PROCESSES - NEEDS FIXING___________________________#

    # if gbl.AppSettingsContainer.EnableWebInterface and not gbl.AppSettingsContainer.EnableAPI:
    #     fw.initialize_web_only()
    #     print("press Control+C to exit.")
    #     try:
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         print("Shutting down web interface...")
