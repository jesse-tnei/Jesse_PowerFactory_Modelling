# Global Registry for the application"
# This file contains global variables and constants used throughout the application.
# It is intended to be imported by other modules to access these globals.
# This file is part of the Open Source project:

#Author: Jesse Solomon



gbl_sAppName = "<unknown application>"
gbl_sDescription = ""
gbl_sVersion = "0.0.0.xxx"
gbl_sFrameworkVersion = "0.0.0.xxx"
gbl_sAuthor = "Jesse Solomon"
VERSION_TESTING = True

WebContainer = None  # Web server container (Flask or other)
EngineContainer       = None   # Generic analysis engine interface
EngineLoadFlowContainer = None   # Load flow analysis engine interface
EngineShortCircuitContainer = None   # Short circuit analysis engine interface
DataModelInterfaceContainer    = None   # Stores data collected from the power systems network model via the engine
DataModelManager = None
StudySettingsContainer = None   # Stores study settings for the network model
AppSettingsContainer = None   # Stores application settings
DataFactory  = None   # Entry point for data model creation and management
Msg          = None   # messaging class
