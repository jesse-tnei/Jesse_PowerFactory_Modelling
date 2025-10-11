class StudySettings:

    def __init__(self):
        self.DoLoadFlow = False
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
        self.settings[key] = value

    def get_setting(self, key):
        return self.settings.get(key, None)

    def remove_setting(self, key):
        if key in self.settings:
            del self.settings[key]
