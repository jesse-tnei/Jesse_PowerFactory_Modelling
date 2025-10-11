#CLASS TO CONFIGURE THE APPLICATION MODE
import os

class AppSettings:
    """Configuration settings for the application."""
    def __init__(self):
        #modes in which the application operates
        self.WebOnlyMode = os.getenv('WEB_ONLY_MODE', '0') == '1'
        self.DevelopmentMode = os.getenv('DEVELOPMENTMODE', '0') == '1'
        self.ProductionMode = os.getenv('PRODUCTIONMODE', '0') == '1'
        self.DebugMode = os.getenv('DEBUGMODE', '0') == '1'
        #flags for feature activation
        self.EnableUI = os.getenv('ENABLEUI', '1') == '1' #enabled by default
        self.EnableAPI = os.getenv('ENABLEAPI', '0') == '1' #disabled by default
        # Environment configuration
        self.Environment = os.getenv('ENVIRONMENT', 'development')
        self.LogLevel = os.getenv('LOG_LEVEL', 'INFO')
        # Web interface settings
        self.WebInterfaceHost = os.getenv('WEB_HOST', 'localhost')
        self.WebInterfacePort = int(os.getenv('WEB_PORT', '5000'))
        self.EnableWebInterface = os.getenv('ENABLE_WEB', '1') == '1'
        self.validate_settings()
    def validate_settings(self):
        """Validate the settings and raise an exception if any are invalid."""
        valid_environments = ['development', 'testing','production']
        if self.Environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self.Environment}. Valid environments are: {valid_environments}")
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LogLevel not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.LogLevel}. Valid log levels are: {valid_log_levels}")
        if self.WebInterfacePort < 1 or self.WebInterfacePort > 65535:
            raise ValueError(f"Invalid web interface port: {self.WebInterfacePort}. Port number must be between 1 and 65535.")
        if self.DevelopmentMode and self.ProductionMode:
            raise ValueError("Both development mode and production mode are enabled. Please choose one or the other.")
        if self.DevelopmentMode and not self.DebugMode:
            self.DebugMode = True
            