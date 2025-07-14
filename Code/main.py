from FrameworkInitialiser import FrameworkInitialiser
# from Framework.Engine import EngineContainer
from Framework import GlobalRegistry as gbl

if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.OutputSplash()
    gbl.Engine.activatePfNetwork(r"Personal_Learning\Load Flow")
    gbl.Engine.activateStudyCase("Study Case")
    print("Framework initialized and ready to use!")