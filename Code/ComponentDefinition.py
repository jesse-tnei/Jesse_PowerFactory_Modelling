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
    
    def ExtractDataModelComponentFromEngine(self):
        # This method should be overridden in subclasses to extract data from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def LoadDataModelComponentToEngine(self):
        # This method should be overridden in subclasses to load data to the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    
    
    
    
    
    
    
    
    
    
    
        