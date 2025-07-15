# This class represents a component definition in a system.
# It includes methods to get the component's name and type.
# Additionally, it defines the attributes that each component should have

class ComponentBaseTemplate:
    def __init__(self):
        self.ON = True
        self.Results = True
        
        
    def SetDataModelComponentStatus(self, status, bUpdateEngine=True):
        self.ON = bool(status)
        if bUpdateEngine:
            return self.StatusToEngine()
        
    def SwitchDataModelComponentOff(self):
        self.ON = False
        
    def SwitchDataModelComponentOn(self):
        self.ON = True
        
    def SwitchDataModelComponentStatus(self):
        self.ON = not self.ON
        
    def GetDataModelComponentReadableName(self):
        return ""
    
    def GetDataModelComponentType(self):
        return self.__class__.__name__
    
    def ListDataModelComponentProperties(self):
        lAttributes = self.__dict__
        return lAttributes
    
    def PassDataModelComponentStatusToEngine(self):
        # This method should be overridden in subclasses to update the engine status
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def GetDataModelComponentStatusFromEngine(self):
        # This method should be overridden in subclasses to retrieve the status from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def GetDataModelComponentFromEngine(self):
        # This method should be overridden in subclasses to extract data from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def SetDataModelComponentToEngine(self):
        # This method should be overridden in subclasses to load data to the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    
    class Busbar(ComponentBaseTemplate):
        def __init__(self, BusID):
            ComponentBaseTemplate.__init__(self)
            try:
                BusID = int(BusID)
            except:
                BusID = str(BusID)
            self.BusID = BusID
            self.name = ''
            self.kV = 0.0
            self.Branches = []
            self.Generators = []
            self.Loads = []
            self.Type = 0
            self.Area = 0
            self.Owner = ''
            self.Disconnected = False
            self.Slack = False
            
            # post load flow attributes
            self.puVoltage = 1.0
            self.busbarAngle = 0.0
            
            # Engine model updater
            self.BasicEngineModelUpdater = None
            self.LoadFlowEngineModelUpdater = None
            self.HarmonicEngineModelUpdater = None
            self.ContingencyAnalysisEngineModelUpdater = None
            
            
            
        def GetDataModelComponentReadableName(self):
            if str(self.BusID) != str(self.name):
                return f"{self.name}-({self.BusID})"
            else:
                return str(self.BusID)
         
        def StatusToEngine(self):
            # Logic to update the engine with the busbar status
            bOK = False
            if self.BasicEngineModelUpdater:
                bOK = self.BasicEngineModelUpdater.UpdateBusbarStatus(self)
            return bOK
        
        def GetDataModelComponentStatusFromEngine(self):
            bOK = False
            if self.BasicEngineModelUpdater:
                bOK = self.BasicEngineModelUpdater.GetBusbarStatusFromEngine(self)
            return bOK
        
        def GetDataModelComponentFromEngine(self):
            bOK = False
            if self.BasicEngineModelUpdater:
                bOK = self.BasicEngineModelUpdater.GetBusbarFromEngine(self)
            return bOK
        
        def SetDataModelComponentToEngine(self):
            bOK = False
            if self.BasicEngineModelUpdater:
                bOK = self.BasicEngineModelUpdater.SetBusbarToEngine(self)
            return bOK
        
        def GetLoadFlowResuts(self):
            bOK = False
            if self.LoadFlowEngineModelUpdater:
                bOK = self.LoadFlowEngineModelUpdater.GetLoadFlowResults(self)
            return bOK
        def GetHarmonicResults(self):
            bOK = False
            if self.HarmonicEngineModelUpdater:
                bOK = self.HarmonicEngineModelUpdater.GetHarmonicResults(self)
            return bOK
        def GetContingencyAnalysisResults(self):
            bOK = False
            if self.ContingencyAnalysisEngineModelUpdater:
                bOK = self.ContingencyAnalysisEngineModelUpdater.GetContingencyAnalysisResults(self)
            return bOK
    
    
    
    
    
    
    
    
    
    
    
    
        