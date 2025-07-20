# Connector module that brings together all the initialisation code for the framework.

import os, sys
import string

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  #add Code directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "Framework"))  #add Framework directory to path

from Framework import GlobalRegistry as gbl
from Framework import Messaging as Msg
from DataModelManager import DataModelManager
from Framework import EngineDataModelInterfaceContainer
from Framework.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
from ComponentManager import ComponentBaseTemplate


class FrameworkInitialiser:
    """Framework initialization and management class"""

    def __init__(self):
        self.isinitialized = False
        self.engine = None  # Future: Will hold Engine instance
        self.datamodelinterface = None  # Future: Will hold DataModelInterface instance

    def initialize(self, engine=None):
        """Initialize all framework components"""
        if self.isinitialized:
            print("Framework already initialized!")
            return

        try:
            # Priority order: provided params > engine info > defaults
            
            # Create messaging instance first so it can be used globally
            gbl.Msg = Msg.Messaging()
            
            # Import here to avoid circular dependency since killing PowerFactory processes requires Messaging
            from Framework.EnginePowerFactory import EnginePowerFactory  
            
            # Initialize engine
            self.engine = EnginePowerFactory(preferred_version=2023) if engine is None else engine
            
            # Set global registry values
            gbl.gbl_sAppName = getattr(self.engine, 'm_strTypeOfEngine', "PowerFactory Modelling Framework")
            gbl.gbl_sVersion = getattr(self.engine, 'm_strVersion', "Not Specified")
            gbl.gbl_sAuthor = getattr(self.engine, 'm_strAuthor', "Not Specified")
            gbl.Engine = self.engine
            
            from Framework.EnginePowerFactoryDataModelInterface import EnginePowerFactoryDataModelInterface as PowerFactoryDataModelInterface
            self.datamodelinterface = PowerFactoryDataModelInterface(gbl)
            
            gbl.DataModelInterface = self.datamodelinterface
            
            
            ComponentBaseTemplate.m_oEngineDataModelInterface = gbl.DataModelInterface
            gbl.DataModelManager = DataModelManager() 

            self.is_initialized = True

        except Exception as e:
            print(f"Failed to initialize framework: {e}")
            raise

    def cleanup(self):
        """Clean up framework resources"""
        if not self.is_initialized:
            return

        try:
            if gbl.Msg:
                gbl.Msg.close_log_files()
                gbl.Msg = None

            self.is_initialized = False
            print("Framework cleaned up successfully!")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def isready(self):
        """Check if framework is initialized and ready"""
        return self.is_initialized

    def getstatus(self):
        """Get framework status information"""
        return {
            'initialized': self.is_initialized,
            'app_name': gbl.gbl_sAppName if self.is_initialized else None,
            'app_version': gbl.gbl_sVersion if self.is_initialized else None,
            'messaging_active': gbl.Msg is not None if self.is_initialized else False
        }


# # For backwards compatibility - if run directly
# if __name__ == "__main__":
#     fw = FrameworkInitialiser()
#     fw.initialize()
