# This class represents a component definition in a system.
# It includes methods to get the component's name and type.
# Additionally, it defines the attributes that each component should have

class ComponentBaseTemplate:
    def __init__(self):
        self.ON = True
        self.Results = True
        
        
    def SetStatus(self, status, bUpdateEngine=True):
        self.ON = bool(status)
        if bUpdateEngine:
            return self.StatusToEngine()
        
    def SwitchOff(self):
        self.ON = False
        
    def SwitchOn(self):
        self.ON = True
        
    def SwitchStatus(self):
        self.ON = not self.ON
        
    def GetReadableName(self):
        return ""
    
    def GetClassName(self):
        return self.__class__.__name__
    
    def ListComponentAttributes(self):
        lAttributes = self.__dict__
        return lAttributes
    
    def StatusToEngine(self):
        # This method should be overridden in subclasses to update the engine status
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def StatusFromEngine(self):
        # This method should be overridden in subclasses to retrieve the status from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def ExtractFromEngine(self):
        # This method should be overridden in subclasses to extract data from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def LoadToEngine(self):
        # This method should be overridden in subclasses to load data to the engine
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    
    
    
    
    
    
    
    
    
        