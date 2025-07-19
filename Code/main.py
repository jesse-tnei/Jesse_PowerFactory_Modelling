from FrameworkInitialiser import FrameworkInitialiser
from Framework import GlobalRegistry as gbl

if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.DisplayWelcomeMessage()
    gbl.Engine.activatepowerfactorynetwork(r"Personal_Learning\Load Flow")
    gbl.Engine.activatepowerfactorystudycase("Study Case")
    gbl.Engine.getauthor()
    print("Framework initialized and ready to use!")