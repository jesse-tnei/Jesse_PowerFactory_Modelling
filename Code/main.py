from FrameworkInitialiser import FrameworkInitialiser
# from Framework.Engine import EngineContainer
from Framework import GlobalRegistry as gbl
# from Framework.EnginePowerFactory import EnginePowerFactory

if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
    gbl.Msg.OutputSplash()