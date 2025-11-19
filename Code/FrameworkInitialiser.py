# Connector module that brings together all the initialisation code for the framework.
import os, sys
import string
import threading

from Code import GlobalEngineRegistry as gbl


class FrameworkInitialiser:
    """Framework initialization and management class"""

    def __init__(self):
        self.isinitialized = False
        self.webinitialized = False
        self.backendinitialized = False
        self.selected_engine = None
        self.bOK = False
        self.engine = None
        self._configureapplicationsettings()

    def initializeproduct(self, engine=None, webinterfaceonly=False):
        """Initialize all framework components"""
        if self.isinitialized:
            print("Framework already initialized!")
            return
        try:
            # Priority order: provided params > engine info > defaults

            # Create messaging instance first so it can be used globally
            self.bOK = self.initialise_messaging()
            if self.bOK:
                self.bOK = self.initialisestudysettings()
            if webinterfaceonly:
                #web interface only
                if self.bOK:
                    self.bOK = self.initialisewebinterface()
                if self.bOK:
                    self.bOK = self.startwebinterface()
                if self.bOK:
                    self.webinitialized = True
            else:
                if self.bOK:
                    self.bOK = self.initialize_backend(engine)
                if self.bOK:
                    self.bOK = self.initialisewebinterface()
                if self.bOK:
                    self.bOK = self.startwebinterface()
                if self.bOK:
                    self.isinitialized = True
        except Exception as e:
            print(f"Failed to initialize framework: {e}")
            raise

    def initialize_web_only(self):
        """Initialize only components needed for web interface"""
        self.bOK = self.initialise_messaging()
        if self.bOK:
            self.bOK = self.initialisestudysettings()
        if self.bOK:
            self.bOK = self.initialisewebinterface()
        if self.bOK:
            self.bOK = self.startwebinterface()
        return self.bOK

    def initialize_backend(self, engine_type=None):
        """Initialize only components needed for backend"""
        try:
            if self.backendinitialized:
                gbl.Msg.AddInfo("Backend already initialized!")
                return
            self.bOK = self.initialisestudyengine(engine_type)
            if not self.bOK:
                return False
            if self.bOK:
                self.bOK = self.initialisedatamodelinterface()
            if self.bOK:
                self.bOK = self.configurecomponenttemplates()
            if self.bOK:
                self.bOK = self.initialisedatafactory()
            if self.bOK:
                self.bOK = self.initialisedatamodelmanager()
            if self.bOK:
                self.bOK = self.initialise_network_data_manager()
            if self.bOK:
                self.bOK = self.initialise_data_source_interface()
            if self.bOK:
                self.backendinitialized = True
                self.selected_engine = engine_type
                gbl.Msg.AddInfo("Backend initialized with engine: " + engine_type)
            return self.bOK
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize backend: {e}")
            return False

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
            gbl.AppSettingsContainer.EnableAPI = True  #toggle this to enable enginepowerfactory
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
            EnableWebInterface = False
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
                print(f"DEBUG: About to start web thread")
                print(f"DEBUG: self.gbl.WebContainer = {gbl.WebContainer}")
                print(f"DEBUG: type(self.gbl.WebContainer) = {type(gbl.WebContainer)}")
                host = getattr(gbl.AppSettingsContainer, 'WebInterfaceHost', 'localhost')
                port = getattr(gbl.AppSettingsContainer, 'WebInterfacePort', 5000)
                print(f"DEBUG: host={host}, port={port}")
                web_thread = threading.Thread(target=gbl.WebContainer,
                                              args=(host, port),
                                              daemon=True)
                # print(f"DEBUG: Thread created: {web_thread}")
                web_thread.start()
                print(f"DEBUG: Thread started, is_alive: {web_thread.is_alive()}")
                # Wait a moment and check if thread is still alive
                import time
                time.sleep(1)
                print(f"DEBUG: After 1 second, thread is_alive: {web_thread.is_alive()}")
                gbl.Msg.AddInfo(f"Web interface started at http://{host}:{port}")
            return True
        except Exception as e:
            print(f"DEBUG: Exception in startwebinterface: {e}")
            gbl.Msg.AddError(f"Failed to start web interface: {e}")
            return False

    def initialisestudyengine(self, engine=None, engine_type="ipsa", **kwargs):
        """Initialize study engine. Defaults to PowerFactory if not defined"""
        try:
            if engine is None:
                if gbl.StudySettingsContainer.powerfactory:
                    from Code.Framework.PowerFactory.EnginePowerFactory import EnginePowerFactory
                    engine = EnginePowerFactory(preferred_version=2024)
                elif gbl.StudySettingsContainer.ipsa:
                    from Code.Framework.IPSA.EngineIPSA import EngineIPSA
                    engine = EngineIPSA()
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

    def initialisedatamodelinterface(self, engine=None, engine_type="powerfactory"):
        """Initialize data model interface"""
        try:
            if gbl.StudySettingsContainer.powerfactory:
                from Code.Framework.PowerFactory.EnginePowerFactoryDataModelInterface import EnginePowerFactoryDataModelInterface as PowerFactoryDataModelInterface
                gbl.DataModelInterfaceContainer = PowerFactoryDataModelInterface()
                return True
            if gbl.StudySettingsContainer.ipsa:
                from Code.Framework.IPSA.EngineIPSADataModelInterface import EngineIPSADataModelInterface as EngineIPSADataModelInterface
                gbl.DataModelInterfaceContainer = EngineIPSADataModelInterface()
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
    def initialise_data_source_interface(self):
        """Initialize data source interface"""
        try:
            from Code.DataSources.ETYS.ETYSDataModelInterface import ETYSDataModelInterface
            gbl.DataSourceInterfaceContainer = ETYSDataModelInterface()
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize data source interface: {e}")
            return False
    def initialise_network_data_manager(self):
        """Initialize network data management"""
        try:
            from Code.NetworkDataManager import NetworkDataManager
            gbl.NetworkDataManager = NetworkDataManager()
            gbl.Msg.AddInfo("Network data manager initialized successfully")
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to initialize network data manager: {e}")
            return False

    def _initialise_engine_modules(self, engine_type):
        if engine_type == "powerfactory":
            return self._powerfactorymodules()
        if engine_type == "ipsa":
            return self._ipsamodules()
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

    def _ipsamodules(self):
        """Initialize PowerFactory modules"""
        try:
            # Initialize Load Flow Container
            from Code.Framework.IPSA.EngineIPSALoadFlow import EngineIPSALoadFlow
            gbl.EngineLoadFlowContainer = EngineIPSALoadFlow()
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

    def can_initialize_backend(self):
        """Check if backend can be initialized"""
        return self.webinitialized and not self.backendinitialized

    def is_backend_ready(self):
        """Check if backend is ready for operations"""
        return self.backendinitialized and self.selected_engine is not None

    def get_available_engines(self):
        """Get list of available engines"""
        engines = []
        try:
            # Check PowerFactory availability
            if gbl.StudySettingsContainer.powerfactory:
                engines.append({"name": "PowerFactory", "type": "powerfactory", "available": True})
            else:
                engines.append({"name": "PowerFactory", "type": "powerfactory", "available": False})
            # Check IPSA availability
            if gbl.StudySettingsContainer.ipsa:
                engines.append({"name": "IPSA", "type": "ipsa", "available": True})
            else:
                engines.append({"name": "IPSA", "type": "ipsa", "available": False})
        except Exception as e:
            gbl.Msg.AddError(f"Error checking engine availability: {e}")
        return engines

    def get_framework_status(self):
        """Get detailed framework status"""
        return {
            'web_initialized': self.webinitialized,
            'backend_initialized': self.backendinitialized,
            'selected_engine': self.selected_engine,
            'available_engines': self.get_available_engines(),
            'can_initialize_backend': self.can_initialize_backend(),
            'is_ready': self.is_backend_ready()
        }

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
