from FrameworkInitialiser import FrameworkInitialiser
from Framework import GlobalRegistry as gbl

if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.DisplayWelcomeMessage()
    gbl.Engine.activatePowerFactoryNetwork(r"Personal_Learning\Load Flow")
    gbl.Engine.activatePowerFactoryStudyCase("Study Case")
    gbl.Engine.GetAuthor()
    print("Framework initialized and ready to use!")