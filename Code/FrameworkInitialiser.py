# Connector module that brings together all the initialisation code for the framework.

import os, sys
import string

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  #add Code directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "Framework"))  #add Framework directory to path

from Framework import GlobalRegistry as gbl
from Framework import Messaging as Msg


class FrameworkInitialiser:
    """Framework initialization and management class"""

    def __init__(self):
        self.is_initialized = False
        self.app_name = None
        self.app_version = None
        self.app_author = None
        self.engine = None  # Future: Will hold Engine instance

    def initialize(self, app_name=None, app_version=None, app_author=None, engine=None):
        """Initialize all framework components"""
        if self.is_initialized:
            print("Framework already initialized!")
            return

        try:
            # Priority order: provided params > engine info > defaults
            if engine:
                # Future: Get info from Engine instance
                self.app_name = app_name or getattr(engine, 'app_name', "PowerFactory Modelling Framework")
                self.app_version = app_version or getattr(engine, 'version', "1.0.0") 
                self.app_author = app_author or getattr(engine, 'author', "PowerFactory")
            else:
                # Current fallback defaults
                self.app_name = app_name or "PowerFactory Modelling Framework"
                self.app_version = app_version or "1.0.0"
                self.app_author = app_author or "PowerFactory"
            
            # Set global registry values
            gbl.gbl_sAppName = self.app_name
            gbl.gbl_sVersion = self.app_version
            gbl.gbl_sAuthor = self.app_author
            
            # Store engine reference
            self.engine = engine
            gbl.Engine = engine  # Future: Engine will be available globally

            # Create messaging instance
            gbl.Msg = Msg.Messaging()

            # Show splash screen
            gbl.Msg.OutputSplash()

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

    def is_ready(self):
        """Check if framework is initialized and ready"""
        return self.is_initialized

    def get_status(self):
        """Get framework status information"""
        return {
            'initialized': self.is_initialized,
            'app_name': gbl.gbl_sAppName if self.is_initialized else None,
            'app_version': gbl.gbl_sVersion if self.is_initialized else None,
            'messaging_active': gbl.Msg is not None if self.is_initialized else False
        }


# For backwards compatibility - if run directly
if __name__ == "__main__":
    fw = FrameworkInitialiser()
    fw.initialize()
