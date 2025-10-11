# Connector module that brings together all the initialisation code for the framework.
import os, sys
import string
import threading

from Code import GlobalEngineRegistry as gbl

class FrameworkInitialiser:
    """Framework initialization and management class"""

    def __init__(self):
        self.isinitialized = False
        self.engine = None
        self._configureapplicationsettings()

    def initializefullproduct(self, engine=None, bOK=False):
        """Initialize all framework components"""
        if self.isinitialized:
            print("Framework already initialized!")
            return
        try:
            # Priority order: provided params > engine info > defaults

            # Create messaging instance first so it can be used globally
            bOK = self.initialise_messaging()
            if bOK:
                bOK = self.initialisestudyengine(engine)
            if bOK:
                bOK = self.initialisedatamodelinterface()
            if bOK:
                bOK = self.configurecomponenttemplates()
            if bOK:
                bOK = self.initialisedatafactory()
            if bOK:
                bOK = self.initialisedatamodelmanager()
            if bOK:
                bOK = self.initialisestudysettings()
            if bOK:
                bOK = self.initialisewebinterface()
            if bOK:
                bOK = self.startwebinterface()
            if bOK:
                self.isinitialized = True
        except Exception as e:
            print(f"Failed to initialize framework: {e}")
            raise

    def initialize_web_only(self, bOK=False):
        """Initialize only components needed for web interface"""
        bOK = self.initialise_messaging()
        if bOK:
            bOK = self.initialisestudysettings()
        if bOK:
            bOK = self.initialisewebinterface()
        if bOK:
            bOK = self.startwebinterface()
        return bOK

    def initialise_messaging(self):
        """Initialize messaging"""
        try:
            from Code import Messaging as Msg
            gbl.Msg = Msg.Messaging()
            return True
        except Exception as e:
            print(f"Failed to initialize messaging: {e}")
            return False

    def _configureapplicationsettings(self):
        """Configure application settings from environment variables"""
        try:
            from Code import AppSettings as AppSettings
            gbl.AppSettingsContainer = AppSettings.AppSettings()
            gbl.AppSettingsContainer.EnableWebInterface = True
            gbl.AppSettingsContainer.EnableAPI = True
            gbl.AppSettingsContainer.EnableUI = True
            gbl.AppSettingsContainer.WebOnlyMode = False
            gbl.AppSettingsContainer.DebugMode = False
        except Exception as e:
            self._set_safe_defaults()

    def _set_safe_defaults(self):
        """Set safe defaults if AppSettings initialization fails"""

        class SafeDefaults:
            EnableUI = True
            EnableAPI = True
            EnableWebInterface = True
            WebOnlyMode = False
            DebugMode = False
            WebInterfaceHost = 'localhost'
            WebInterfacePort = 5000

        gbl.AppSettingsContainer = SafeDefaults()

    def initialisewebinterface(self):
        """Initialize web interface"""
        try:
            from Code.WebInterface.FlaskApp import start_web_server
            gbl.WebContainer = start_web_server
            return True
        except ImportError as e:
            gbl.Msg.AddError(f"Web interface not available: {e}")
            return False

    def startwebinterface(self):
        """Start web interface"""
        try:
            if gbl.StudySettingsContainer.EnableWebInterface and gbl.WebContainer:
                # print(f"DEBUG: About to start web thread")
                # print(f"DEBUG: self.gbl.WebContainer = {gbl.WebContainer}")
                # print(f"DEBUG: type(self.gbl.WebContainer) = {type(gbl.WebContainer)}")
                
                host = getattr(gbl.AppSettingsContainer, 'WebInterfaceHost', 'localhost')
                port = getattr(gbl.AppSettingsContainer, 'WebInterfacePort', 5000)
                # print(f"DEBUG: host={host}, port={port}")
                
                web_thread = threading.Thread(target=gbl.WebContainer, args=(host, port), daemon=True)
                # print(f"DEBUG: Thread created: {web_thread}")
                web_thread.start()
                # print(f"DEBUG: Thread started, is_alive: {web_thread.is_alive()}")
                
                # Wait a moment and check if thread is still alive
                import time
                time.sleep(1)
                # print(f"DEBUG: After 1 second, thread is_alive: {web_thread.is_alive()}")
                
                gbl.Msg.AddInfo(f"Web interface started at http://{host}:{port}")
            return True
        except Exception as e:
            print(f"DEBUG: Exception in startwebinterface: {e}")
            gbl.Msg.AddError(f"Failed to start web interface: {e}")
            return False
    def initialisestudyengine(self, engine=None, engine_type="powerfactory", bOK=False, **kwargs):
        """Initialize study engine. Defaults to PowerFactory if not defined"""
        try:
            if engine is None:
                if engine_type == "powerfactory":
                    from Code.Framework.PowerFactory.EnginePowerFactory import EnginePowerFactory
                    engine = EnginePowerFactory(preferred_version=2024)
                elif engine_type == "psse":
                    gbl.Msg.AddError("PSS/E engine not yet implemented")
                    return False
                else:
                    gbl.Msg.AddError(f"Unsupported engine type: {engine_type}")
                    return False
            self.engine = engine
            gbl.gbl_sAppName = getattr(engine, "m_strTypeOfEngine", "PowerFactory")
            gbl.gbl_sVersion = getattr(engine, "m_strVersion", "0.0.0.xxx")
            gbl.gbl_sDescription = getattr(engine, "m_strDescription", "")
            gbl.gbl_sFrameworkVersion = gbl.gbl_sVersion
            gbl.gbl_sAuthor = getattr(engine, "m_strAuthor", "Jesse Solomon")
            gbl.EngineContainer = engine
            #Initialise engine modules
            if not self._initialise_engine_modules(engine_type):
                return False
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize study engine: {e}")
            return False

    def initialisedatamodelinterface(self):
        """Initialize data model interface"""
        try:
            from Code.Framework.PowerFactory.EnginePowerFactoryDataModelInterface import EnginePowerFactoryDataModelInterface as PowerFactoryDataModelInterface
            gbl.DataModelInterfaceContainer = PowerFactoryDataModelInterface()
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize data model interface: {e}")
            return False

    def configurecomponenttemplates(self):
        try:
            from Code.DataModel.ComponentManager import ComponentBaseTemplate
            ComponentBaseTemplate.m_oEngineDataModelInterface = gbl.DataModelInterfaceContainer
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize component templates: {e}")
            return False

    def initialisedatafactory(self):
        """Initialize data factory"""
        try:
            from Code.DataModel.ComponentFactory import ComponentFactory
            gbl.DataFactory = ComponentFactory()
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize data factory: {e}")
            return False

    def _initialise_engine_modules(self, engine_type):
        if engine_type == "powerfactory":
            return self._powerfactorymodules()
        else:
            gbl.Msg.AddError(f"Unsupported engine type: {engine_type}")
            return False

    def _powerfactorymodules(self):
        """Initialize PowerFactory modules"""
        try:
            # Initialize Load Flow Container
            from Code.Framework.PowerFactory.EnginePowerFactoryLoadFlow import EnginePowerFactoryLoadFlow
            gbl.EngineLoadFlowContainer = EnginePowerFactoryLoadFlow()
            # Initialize Short Circuit Container
            from Code.Framework.PowerFactory.EnginePowerFactoryShortCircuit import EnginePowerFactoryShortCircuit
            gbl.EngineShortCircuitContainer = EnginePowerFactoryShortCircuit()
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize PowerFactory modules: {e}")
            return False

    def initialisedatamodelmanager(self):
        try:
            from Code.DataModel.DataModelManager import DataModelManager
            gbl.DataModelManager = DataModelManager()
            gbl.DataModelManager.BasicEngineModelupdater = gbl.DataModelInterfaceContainer
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize data model manager: {e}")
            return False

    def cleanup(self):
        """Clean up framework resources"""
        if not self.isinitialized:
            return

        try:
            if gbl.Msg:
                gbl.Msg.close_log_files()
                gbl.Msg = None

            self.isinitialized = False
            print("Framework cleaned up successfully!")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def initialisestudysettings(self):
        try:
            from Code import StudySettings as StudySettings
            gbl.StudySettingsContainer = StudySettings.StudySettings()
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize study settings: {e}")
            return False

    def isready(self):
        """Check if framework is initialized and ready"""
        return self.isinitialized

    def getstatus(self):
        """Get framework status information"""
        return {
            'initialized': self.isinitialized,
            'app_name': gbl.gbl_sAppName if self.isinitialized else None,
            'app_version': gbl.gbl_sVersion if self.isinitialized else None,
            'messaging_active': gbl.Msg is not None if self.isinitialized else False
        }


# # For backwards compatibility - if run directly
# if __name__ == "__main__":
#     fw = FrameworkInitialiser()
#     fw.initialize()
