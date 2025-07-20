# Class to serve as template for BaseDataModelManager
# This class is used to manage the data models in the application.
# Such operations include:
# - Creating a new data model
# - Deleting a data model

# - Getting a data model by name
# - Listing all data models

#Bear in mind that this is a template and should be extended with actual logic for managing data models.

# Additiionally, remember that the purpose of the class is to provide a centralised point where the non-engine related proceses can be done. For example, this class will allow the deposit of all the generator objects created in the DataFactory once sourced from the engine.

# It is also in here that such generators can be retrieved, turned off and loaded back onto the engine

#The class also outlines the paths for different input files ranging from network files to actual input data files in excel format.
import os
import sys


class DataModelManager:

    def __init__(self):
        self.Busbar_TAB = []
        self.Branch_TAB = []
        self.Gen_TAB = []
        self.Load_TAB = []

        self.BusbarIdToIndex = {}
        self.b_UsebusbarMap = False

    def addbusbartotab(self, oBusbar):
        """Add a busbar to the Busbar_TAB list."""
        self.b_UsebusbarMap = True
        busID = oBusbar.__getattribute__("BusID")
        if busID is not None:
            # assign stringID (busID) to index (current length of Busbar_TAB) to use list for faster lookups
            self.BusbarIdToIndex[busID] = len(self.Busbar_TAB)
            self.Busbar_TAB.append(oBusbar)
            return True
        else:
            # If busID is None, we cannot add the busbar
            return False

    def findbusbar(self, BusID):
        """
        Finds a bus object and its index in the busbar table given a busID
        Syntax:
        oBus, nBusIndex = FindBusbar(busID)
        If not found returns None, -1
        """
        if self.b_UsebusbarMap:
            # Use fast dictionary lookup
            if BusID in self.BusbarIdToIndex:
                nIndex = self.BusbarIdToIndex[BusID]
                oObj = self.Busbar_TAB[nIndex]
                return oObj, nIndex
        else:
            # Fall back to linear search
            for nIndex, bus in enumerate(self.Busbar_TAB):
                if bus.getattribute("BusID") == BusID:
                    return bus, nIndex

        # Not found
        nIndex = -1
        return None, nIndex

    def findbranch(self, Bus1ID, Bus2ID, Bus3ID, BranchID, bAllowTransposedSearch=True):
        """
        Finds a branch object and its index in the branch table given bus IDs and branch ID.
        Syntax:
        oBranch, nBranchIndex = FindBranch(Bus1ID, Bus2ID, Bus3ID, BranchID)
        If not found returns None, -1
        """
        oBranch = None
        nIndex = -1

        if Bus3ID is None:
            Bus3ID = 0
        try:
            Bus1ID = int(Bus1ID)
        except ValueError:
            BusID = str(Bus1ID)
        try:
            Bus2ID = int(Bus2ID)
        except ValueError:
            Bus2ID = str(Bus2ID)
        try:
            Bus3ID = int(Bus3ID)
        except ValueError:
            Bus3ID = str(Bus3ID)

        BranchID = str.strip(BranchID)

        if self.b_UsebusbarMap:
            oBus1, nBus1Index = self.findbusbar(Bus1ID)
            if oBus1:
                for nBranchIdx in oBus1.Branches:
                    branch = self.Branch_TAB[nBranchIdx]
                    if branch.getattribute("BranchID") == BranchID:
                        if branch.getattribute("Bus1ID") == Bus1ID and \
                           branch.getattribute("Bus2ID") == Bus2ID and \
                           branch.getattribute("Bus3ID") == Bus3ID:
                            oBranch = branch
                            nIndex = nBranchIdx
                            break
                        if bAllowTransposedSearch:
                            if branch.getattribute("Bus1ID") == Bus2ID and \
                               branch.getattribute("Bus2ID") == Bus1ID and \
                               branch.getattribute("Bus3ID") == Bus3ID:
                                oBranch = branch
                                nIndex = nBranchIdx
                                break
                            else:
                                if branch.getattribute("Bus1ID") == Bus3ID and \
                                   branch.getattribute("Bus2ID") == Bus2ID and \
                                   branch.getattribute("Bus3ID") == Bus1ID:
                                    oBranch = branch
                                    nIndex = nBranchIdx
                                    break

        # if not found in busbar map, do linear search
        if oBranch is None:
            for nBranchIdx, branch in enumerate(self.Branch_TAB):
                if branch.getattribute("BranchID") == BranchID:
                    if branch.getattribute("Bus1ID") == Bus1ID and \
                       branch.getattribute("Bus2ID") == Bus2ID and \
                       branch.getattribute("Bus3ID") == Bus3ID:
                        oBranch = branch
                        nIndex = nBranchIdx
                        break
                    if bAllowTransposedSearch:
                        if branch.getattribute("Bus1ID") == Bus2ID and \
                           branch.getattribute("Bus2ID") == Bus1ID and \
                           branch.getattribute("Bus3ID") == Bus3ID:
                            oBranch = branch
                            nIndex = nBranchIdx
                            break
                        else:
                            if branch.getattribute("Bus1ID") == Bus3ID and \
                               branch.getattribute("Bus2ID") == Bus2ID and \
                               branch.getattribute("Bus3ID") == Bus1ID:
                                oBranch = branch
                                nIndex = nBranchIdx
                                break
        # Not found
        if oBranch is None:
            nIndex = -1
        return oBranch, nIndex

    def addgentotab(self, oGenerator):
        """Add a generator to the Gen_TAB list and update busbar mapping."""
        bOK = True
        if oGenerator is None:
            bOK = False
            return bOK
        gen_index = len(self.Gen_TAB)
        self.Gen_TAB.append(oGenerator)

        # If using busbar map, add generator index to the busbar's generator list
        if self.b_UsebusbarMap:
            busID = oGenerator.__getattribute__("BusID")
            if busID is not None:
                oBus, _ = self.findbusbar(busID)
                if oBus is not None:
                    # Ensure the busbar has a Generators list
                    if not hasattr(oBus, 'Generators'):
                        oBus.Generators = []
                    bOK = oBus.Generators.append(gen_index)
                    bOK = True
        return bOK

    def findgen(self, BusID, GenID):
        """
        Finds a generator object and its index given a busID and gen ID
        If not found returns None, -1
        """
        oObj = None
        nIndex = -1
        GenID = str(GenID).strip()

        if self.b_UsebusbarMap:
            # Use fast busbar map lookup
            oBus, _ = self.findbusbar(BusID)
            if oBus is not None and hasattr(oBus, 'Generators'):
                for nGenIdx in oBus.Generators:
                    gen = self.Gen_TAB[nGenIdx]
                    strGenID = str(gen.getattribute("GenID")).strip()
                    if strGenID == GenID:
                        return gen, nGenIdx
        else:
            # Fall back to linear search
            for nGenIdx, gen in enumerate(self.Gen_TAB):
                gen_bus_id = gen.getattribute("BusID")
                strGenID = str(gen.getattribute("GenID")).strip()
                if gen_bus_id == BusID and strGenID == GenID:
                    return gen, nGenIdx

        # Not found
        return None, -1

    def addloadtotab(self, oLoad):
        """Add a load to the Load_TAB list and update busbar mapping."""
        bOK = True
        if oLoad is None:
            bOK = False
            return bOK
        load_index = len(self.Load_TAB)
        self.Load_TAB.append(oLoad)

        # If using busbar map, add load index to the busbar's load list
        if self.b_UsebusbarMap:
            busID = oLoad.__getattribute__("BusID")
            if busID is not None:
                oBus, _ = self.findbusbar(busID)
                if oBus is not None:
                    # Ensure the busbar has a Loads list
                    if not hasattr(oBus, 'Loads'):
                        oBus.Loads = []
                    bOK = oBus.Loads.append(load_index)
                    bOK = True
        return bOK

    def findload(self, BusID, LoadID):
        """
        Finds a load object and its index given a busID and load ID
        If not found returns None, -1
        """
        LoadID = str(LoadID).strip()

        if self.b_UsebusbarMap:
            # Use fast busbar map lookup
            oBus, _ = self.findbusbar(BusID)
            if oBus is not None and hasattr(oBus, 'Loads'):
                for nLoadIdx in oBus.Loads:
                    load = self.Load_TAB[nLoadIdx]
                    strLoadID = str(load.getattribute("LoadID")).strip()
                    if strLoadID == LoadID:
                        return load, nLoadIdx
        else:
            # Fall back to linear search
            for nLoadIdx, load in enumerate(self.Load_TAB):
                load_bus_id = load.getattribute("BusID")
                strLoadID = str(load.getattribute("LoadID")).strip()
                if load_bus_id == BusID and strLoadID == LoadID:
                    return load, nLoadIdx

        # Not found
        return None, -1

    def getallloadsonbus(self, BusID):
        """
        Get all loads connected to a specific bus
        Returns list of (load_object, index) tuples
        """
        loads = []

        if self.b_UsebusbarMap:
            # Use fast busbar map lookup
            oBus, _ = self.findbusbar(BusID)
            if oBus is not None and hasattr(oBus, 'Loads'):
                for nLoadIdx in oBus.Loads:
                    load = self.Load_TAB[nLoadIdx]
                    loads.append((load, nLoadIdx))
        else:
            # Fall back to linear search
            for nLoadIdx, load in enumerate(self.Load_TAB):
                load_bus_id = load.getattribute("BusID")
                if load_bus_id == BusID:
                    loads.append((load, nLoadIdx))

        return loads

    def getallgensonbus(self, BusID):
        """
        Get all generators connected to a specific bus
        Returns list of (generator_object, index) tuples
        """
        generators = []

        if self.b_UsebusbarMap:
            # Use fast busbar map lookup
            oBus, _ = self.findbusbar(BusID)
            if oBus is not None and hasattr(oBus, 'Generators'):
                for nGenIdx in oBus.Generators:
                    gen = self.Gen_TAB[nGenIdx]
                    generators.append((gen, nGenIdx))
        else:
            # Fall back to linear search
            for nGenIdx, gen in enumerate(self.Gen_TAB):
                gen_bus_id = gen.getattribute("BusID")
                if gen_bus_id == BusID:
                    generators.append((gen, nGenIdx))

        return generators
