import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "Framework"))  #add Framework directory to path
from Code import FrameworkInitialiser as f_init
from Code import GlobalEngineRegistry as gbl


if __name__ == "__main__":
    fw = f_init.FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.DisplayWelcomeMessage()
    gbl.EngineContainer.activatepowerfactorynetwork(r"Personal_Learning\Load Flow [Again]")
    gbl.EngineContainer.activatepowerfactorystudycase("Study Case")
    gbl.DataModelInterfaceContainer.passelementsfromnetworktodatamodelmanager()
    gbl.EngineLoadFlowContainer.runloadflow()

    
    print("Framework initialized and ready to use!")