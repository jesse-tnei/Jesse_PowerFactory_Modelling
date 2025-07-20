
from Framework import GlobalRegistry as gbl
#from ComponentManager import Busbar, Generator, Load, Branch
from ComponentManager import Busbar, Generator, Load

class ComponentFactory():
    def __init__(self):
        self.o_Msg = gbl.Msg
    
    def createbusbar(self, BusID):
        """Creates a busbar component with the given BusID"""
        return Busbar(BusID)
    
    def creategenerator(self, BusID, GenID):
        """Creates a generator component with the given BusID and GenID"""
        return Generator(BusID, GenID)
    
    def createload(self, BusID, LoadID):
        """Creates a load component with the given BusID and LoadID"""
        return Load(BusID, LoadID)
    
    # def createbranch(self, BusID1, BusID2, BranchID):
    #     """Creates a branch component with the given BusID1, BusID2 and BranchID"""
    #     return Branch(BusID1, BusID2, BranchID)
    
    def associateradialwithbus(self, busbar, radial):
        """Associates a radial (generator, load, branch) with a busbar"""
        nBusIndex = -1
        oBus, nBusIndex = gbl.DataModelManager.getbusbarfromdatamodel(busbar.BusID)
        if nBusIndex == -1:
            self.o_Msg.AddError(f"Busbar with ID {busbar.BusID} not found in DataModel.")
            return False
        radial.oBus1 = oBus
        radial.BusIndex = nBusIndex
        radial.BusName = oBus.Name
        return True
    
    def associatebranchwithbus(self, branch):
        """Associates a branch with its busbars"""
        nBusIndex1 = -1
        nBusIndex2 = -1
        nBusIndex3 = -1
        oBus1, nBusIndex1 = gbl.DataModelManager.getbusbarfromdatamodel(branch.BusID1)
        oBus2, nBusIndex2 = gbl.DataModelManager.getbusbarfromdatamodel(branch.BusID2)
        oBus3, nBusIndex3 = gbl.DataModelManager.getbusbarfromdatamodel(branch.BusID3) if hasattr(branch, 'BusID3') else (None, -1)
        
        if nBusIndex1 == -1 or nBusIndex2 == -1:
            self.o_Msg.AddError(f"One or both busbars for Branch {branch.BranchID} not found in DataModel.")
            return False
        
        branch.oBus1 = oBus1
        branch.oBus2 = oBus2
        branch.BusIndex1 = nBusIndex1
        branch.BusIndex2 = nBusIndex2
        
        if oBus3 is not None and nBusIndex3 == -1:
            branch.oBus3 = oBus3
            branch.BusIndex3 = nBusIndex3
        return True

    
    
    
    
    
    