class StudySettings:

    def __init__(self):
        self.DoLoadFlow = True
        self.DoShortCircuit = False
        self.DoHarmonics = False
        self.DoContingencyAnalysis = False
        self.DoVoltageStability = False
        self.DoTransientStability = False
        self.settings = {}

        # Web interface settings
        self.EnableWebInterface = True
        self.WebInterfacePort = 5000
        self.WebInterfaceHost = 'localhost'

    def set_setting(self, key, value):
        """Set a setting value"""
        self.settings[key] = value

    def get_setting(self, key):
        """Get a setting value"""
        return self.settings.get(key, None)

    def remove_setting(self, key):
        """Remove a setting"""
        if key in self.settings:
            del self.settings[key]
