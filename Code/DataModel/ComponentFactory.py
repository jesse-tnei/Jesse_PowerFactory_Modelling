
from Code import GlobalEngineRegistry as gbl
#from ComponentManager import Busbar, Generator, Load, Branch
from Code.DataModel.ComponentManager import Busbar, Generator, Load, Branch

class ComponentFactory():
    def __init__(self):
        self.o_Msg = gbl.Msg
    def createbusbar(self, BusID):
        """Creates a busbar component with the given BusID"""
        return Busbar(BusID)
    def creategenerator(self, BusID, GenID):
        """Creates a generator component with the given BusID and GenID"""
        generator_item = Generator(BusID, GenID)
        if generator_item:
            self.associateradialwithbus(generator_item)
        return generator_item
    def createload(self, BusID, LoadID):
        """Creates a load component with the given BusID and LoadID`"""
        load_item = Load(BusID, LoadID)
        if load_item:
            self.associateradialwithbus(load_item)
        return load_item
    def createbranch(self, BusID1, BusID2, BusID3, BranchID):
        """Creates a branch component with the given BusID1, BusID2 and BranchID"""
        branch_item = Branch(BusID1, BusID2, BusID3, BranchID)
        if branch_item:
            self.associatebranchwithbus(branch_item)
        return branch_item
    def associateradialwithbus(self, radial):
        """Associates a radial (generator, load, branch) with a busbar"""
        nBusIndex = -1
        oBus, nBusIndex = gbl.DataModelManager.findbusbar(radial.BusID)
        if nBusIndex == -1:
            self.o_Msg.AddError(f"Busbar with ID {radial.BusID} not found in DataModel.")
            return False
        radial.oBus1 = oBus
        radial.BusIndex = nBusIndex
        radial.BusName = oBus.name
        return True
    def associatebranchwithbus(self, branch):
        """Associates a branch with its busbars"""
        nBusIndex1 = -1
        nBusIndex2 = -1
        nBusIndex3 = -1
        oBus1, nBusIndex1 = gbl.DataModelManager.findbusbar(branch.BusID1)
        oBus2, nBusIndex2 = gbl.DataModelManager.findbusbar(branch.BusID2)
        oBus3, nBusIndex3 = gbl.DataModelManager.findbusbar(branch.BusID3) if hasattr(branch, 'BusID3') else (None, -1)

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