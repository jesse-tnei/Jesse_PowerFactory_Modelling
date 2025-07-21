# This class represents a component definition in a system.
# It includes methods to get the component's name and type.
# Additionally, it defines the attributes that each component should have


class ComponentBaseTemplate:
    
    m_oEngineDataModelInterface = None
    

    def __init__(self):
        self.ON = True
        self.Results = True
        

    def setdatamodelcomponentstatus(self, status, bUpdateEngine=True):
        "By default, sets the datamodel component status to ON or OFF based on the status parameter. If bUpdateEngine is True, it will also update the engine status."
        self.ON = bool(status)
        if bUpdateEngine:
            return self.setdatamodelcomponentstatustoengine()

    def switchdatamodelcomponentoff(self):
        "Switches the data model component off."
        self.ON = False

    def switchdatamodelcomponenton(self):
        "Switches the data model component on."
        self.ON = True

    def switchdatamodelcomponentstatus(self):
        "Toggles the data model component status."
        self.ON = not self.ON

    def getdatamodelcomponentreadablename(self) -> str:
        "Returns a readable name for the data model component. This should be overridden in subclasses to provide a meaningful name."
        return ""

    def getdatamodelcomponenttype(self):
        "Returns the type of the data model component. This should be overridden in subclasses to provide a meaningful type."
        return self.__class__.__name__

    def listdatamodelcomponentproperties(self):
        "Returns a list of attributes of the data model component. This can be overridden in subclasses to provide specific attributes."
        lAttributes = self.__dict__
        return lAttributes

    def setdatamodelcomponentstatustoengine(self):
        # This method should be overridden in subclasses to update the engine status
        raise NotImplementedError("This method should be implemented in subclasses.")

    def getdatamodelcomponentstatusfromengine(self):
        # This method should be overridden in subclasses to retrieve the status from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")

    def getdatamodelcomponentfromengine(self):
        # This method should be overridden in subclasses to extract data from the engine
        raise NotImplementedError("This method should be implemented in subclasses.")

    def setdatamodelcomponenttoengine(self):
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
        self.VMagPu = 1.0
        self.VMagkV = 0.0
        self.VangDeg = 0.0
        self.VangRad = 0.0

        #Harmonic attributes
        self.THD = 0.0
        self.VoltSum = 0.0
        self.HarmVolts = {}
        self.Distortions = {}

        # Engine model updater based on the type of analysis
        self.BasicEngineModelUpdater = None
        self.LoadFlowEngineModelUpdater = None
        self.HarmonicEngineModelUpdater = None
        self.ContingencyAnalysisEngineModelUpdater = None

    def getdatamodelcomponentreadablename(self) -> str:
        if str(self.BusID) != str(self.name):
            return f"{self.name}-({self.BusID})"
        else:
            return str(self.BusID)

    def setdatamodelcomponentstatustoengine(self):
        # Logic to update the engine with the busbar status
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.updatebusbarstatus(self)
        return bOK

    def getdatamodelcomponentstatusfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getbusbarstatusfromengine(self)
        return bOK

    def getdatamodelcomponentfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getbusbarfromengine(self)
        return bOK

    def setdatamodelcomponenttoengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.setbusbartoengine(self)
        return bOK

    def getloadflowresuts(self):
        bOK = False
        if self.LoadFlowEngineModelUpdater:
            bOK = self.LoadFlowEngineModelUpdater.getloadflowresults(self)
        return bOK

    def getharmonicresults(self):
        bOK = False
        if self.HarmonicEngineModelUpdater:
            bOK = self.HarmonicEngineModelUpdater.getharmonicresults(self)
        return bOK

    def getcontingencyanalysisresults(self):
        bOK = False
        if self.ContingencyAnalysisEngineModelUpdater:
            bOK = self.ContingencyAnalysisEngineModelUpdater.getcontingencyanalysisresults(self)
        return bOK


class Generator(ComponentBaseTemplate):

    def __init__(self, BusID, GenID):
        ComponentBaseTemplate.__init__(self)
        try:
            BusID = int(BusID)
        except:
            BusID = str(BusID)

        # gen unique identifier/ network mapping properties
        self.BusID = BusID
        self.GenID = str(GenID)
        self.BusIndex = 0
        self.BusName = ''
        self.oBus = None

        #gen operational attributes
        self.MW = 0.0
        self.MVar = 0.0
        self.MWCapacity = 0.0
        self.MSG = 0.0
        self.Qmax = 99999
        self.Qmin = -99999

        # Engine model updater based on the type of analysis
        self.BasicEngineModelUpdater = None
        self.LoadFlowEngineModelUpdater = None
        self.HarmonicEngineModelUpdater = None
        self.ContingencyAnalysisEngineModelUpdater = None

    def getdatamodelcomponentreadablename(self) -> str:
        return f"{self.BusName}-{self.GenID})"

    def getdatamodelcomponentfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getgeneratorfromengine(self)
        return bOK

    def setdatamodelcomponenttoengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.setgeneratortoengine(self)
        return bOK

    def setdatamodelcomponentstatustoengine(self):
        # Logic to update the engine with the generator status
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.updategeneratorstatus(self)
        return bOK

    def getdatamodelcomponentstatusfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getgeneratorstatusfromengine(self)
        return bOK
    
class Load(ComponentBaseTemplate):
    def __init__(self, BusID, LoadID):
        ComponentBaseTemplate.__init__(self)
        try:
            BusID = int(BusID)
        except:
            BusID = str(BusID)

        # load unique identifier/ network mapping properties
        self.BusID = BusID
        self.LoadID = str(LoadID)
        self.BusIndex = 0
        self.BusName = ''
        self.oBus = None
        
        # load operational attributes
        self.MW = 0.0
        self.MVar = 0.0
        self.MWCapacity = 0.0
        self.MSG = 0.0
        self.Qmax = 99999
        self.Qmin = -99999
        
        # Engine model updater based on the type of analysis
        self.BasicEngineModelUpdater = None
        self.LoadFlowEngineModelUpdater = None
        self.HarmonicEngineModelUpdater = None
        self.ContingencyAnalysisEngineModelUpdater = None
        
        
    def getdatamodelcomponentreadablename(self) -> str:
        return f"{self.BusName}-{self.LoadID})"
    
    def getdatamodelcomponentfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getloadfromengine(self)
        return bOK
    
    def setdatamodelcomponenttoengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.setloadtoengine(self)
        return bOK
    
    def setdatamodelcomponentstatustoengine(self):
        # Logic to update the engine with the load status
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.updateloadstatus(self)
        return bOK
    def getdatamodelcomponentstatusfromengine(self):
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getloadstatusfromengine(self)
        return bOK
    
    
class Branch(ComponentBaseTemplate):
    def __init__(self, BusID1, BusID2, Bus3ID, BranchID):
        ComponentBaseTemplate.__init__(self)
        try:
            BusID1 = int(BusID1)
        except:
            BusID1 = str(BusID1)
        try:
            BusID2 = int(BusID2)
        except:
            BusID2 = str(BusID2)
        try:
            BusID3 = int(Bus3ID)
        except:
            BusID3 = str(Bus3ID)
        
        self.BusID1 = BusID1
        self.BusID2 = BusID2
        self.BusID3 = BusID3
        self.BranchID = str.strip(BranchID)
        
        self.TxName = ''
        self.BusIndex1 = -1
        self.BusIndex2 = -1
        self.BusIndex3 = -1
        self.Bus1Name = ''
        self.Bus2Name = ''
        self.Bus3Name = ''
        self.oBus1 = None
        self.oBus2 = None
        self.oBus3 = None
        
        self.RatingA = 0.0
        self.RatingB = 0.0
        self.RatingC = 0.0
        
        self.IsSwitch = False
        self.IsTransformer = False
        self.IsLine = False
        self.IsBreaker = False
        self.IsCoupler = False
        self.IsSeriesReactor = False
        
        self.Is3WindingTransformer = False
        self.IsShunt = False
        
        if Bus3ID:
            self.IsTransformer = True
            self.Is3WindingTransformer = True
            
        self.IsMultiSectionLine = False
    
    def setdatamodelbusname(self, name, side):
        """Sets the bus name for the branch based on the side (1, 2, or 3)."""
        if side == 1:
            self.Bus1Name = name
        elif side == 2:
            self.Bus2Name = name
        elif side == 3:
            self.Bus3Name = name
            
    def getdatamodelcomponentreadablename(self) -> str:
        """Returns a readable name for the branch component."""
        if self.Is3WindingTransformer:
            return f"{self.TxName} ({self.BusID1}, {self.BusID2}, {self.BusID3})"
        elif self.IsTransformer and not self.Is3WindingTransformer:
            return f"{self.TxName} ({self.BusID1}, {self.BusID2})"
        elif self.IsMultiSectionLine:
            return f"{self.BranchID} ({self.BusID1}, {self.BusID2}, {self.BusID3})"
        else:
            return f"{self.BranchID} ({self.BusID1}, {self.BusID2})"
        
        
    def getdatamodelcomponentfromengine(self):
        """Retrieves the branch component from the engine."""
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getbranchfromengine(self)
        return bOK
    
    def setdatamodelcomponenttoengine(self):
        """Sets the branch component to the engine."""
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.setbranchtoengine(self)
        return bOK
    
    def setdatamodelcomponentstatustoengine(self):
        """Updates the engine with the branch status."""
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.updatebranchstatus(self)
        return bOK
    
    def getdatamodelcomponentstatusfromengine(self):
        """Retrieves the branch status from the engine."""
        bOK = False
        if self.BasicEngineModelUpdater:
            bOK = self.BasicEngineModelUpdater.getbranchstatusfromengine(self)
        return bOK
    
    