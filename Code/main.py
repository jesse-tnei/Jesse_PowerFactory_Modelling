from FrameworkInitialiser import FrameworkInitialiser
from Framework.Engine import EngineContainer

if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
    engine = EngineContainer()
    engine.msg.OutputSplash()