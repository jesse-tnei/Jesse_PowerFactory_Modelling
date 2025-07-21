# This module retrives data from PowerFactory engine, creates a data model, and manages the transfer of data between the network and the data model.

from Framework import GlobalRegistry as gbl
from Framework.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
class EnginePowerFactoryDataModelInterface(EngineDataModelInterfaceContainer):
    def __init__(self, gbl):
        EngineDataModelInterfaceContainer.__init__(self)
        self.terminal_dictionary = {}  # Dictionary to hold terminal IDs and their corresponding bus IDs
        self.load_dictionary = {}  # Dictionary to hold load IDs and their corresponding bus IDs
        
        self.generator_dictionary = {}  # Dictionary to hold generator IDs and their corresponding bus IDs
        self.branch_dictionary = {}  # Dictionary to hold branch IDs and their corresponding bus IDs
        
        
     
     
     #____________________BUSBAR METHODS________________________#   
    def getbusbarsfromnetwork(self):
        """Retrieves busbars from the PowerFactory network."""
        bOK = True
        if bOK:
            terminals = gbl.Engine.m_pFApp.GetCalcRelevantObjects("ElmTerm")   
        if terminals:
            gbl.Msg.AddRawMessage(f"Total busbars retrieved successfully from the network: {len(terminals)}")
            for terminal in terminals:
                terminal_id = self._standardize_terminal_id(terminal)
                self.terminal_dictionary[terminal_id] = terminal
            
                busbar = gbl.DataFactory.createbusbar(terminal_id)
                if busbar is None:
                    self.m_oMsg.AddError(f"Failed to create busbar for terminal {terminal_id}.")
                    continue
                if not self.getbusbarvaluesfromnetwork(busbar):
                    self.m_oMsg.AddError(f"Failed to retrieve values for busbar {busbar.BusID}.")
                    continue
                if not gbl.DataModelManager.addbusbartotab(busbar):
                    self.m_oMsg.AddError(f"Failed to add busbar {busbar.BusID} to DataModel.")
                    continue
        gbl.Msg.AddRawMessage(f"Total busbars added to DataModel: {len(self.terminal_dictionary)}")  
        return bOK
    
    def _standardize_terminal_id(self, terminal: object) -> str:
        """Standardizes the bus ID to a consistent format."""
        current = terminal
        while current and current.GetClassName() != "ElmTerm":
            current = current.GetParent()
            
        if current:
            terminal_id = f"{current.cpSubstat.GetAttribute('loc_name')}_{current.GetAttribute('loc_name')}_{current.GetAttribute('uknom')}"
            return terminal_id
        
    def getbusbarvaluesfromnetwork(self, busbar):
        """Retrieves busbar values from the PowerFactory network."""
        bOK = True
        if bOK:
            terminal = self.terminal_dictionary.get(busbar.BusID)
            if terminal:
                name = terminal.GetAttribute("loc_name")
                VMagkV = terminal.GetAttribute("uknom")
                ON = not(bool(terminal.GetAttribute("outserv"))) # returns 0 if busbar is on, 1 if busbar is off
            else:
                name = VMagkV = ON = None
            if name is None or VMagkV is None or ON is None:
                gbl.Msg.AddError(f"Failed to retrieve values for busbar {busbar.BusID}.")
                bOK = False
            else:
                busbar.name = name
                busbar.kV = VMagkV
                busbar.Disconnected = not ON             
        return bOK
        
#____________________BRANCH METHODS________________________#
    def getbranchesfromnetwork(self):
            """Retrieves branches from the PowerFactory network."""
            bOK = True
            if bOK:
                bOK = self.get_linesfromnetwork()
            if bOK:
                bOK = self.get_transformersfromnetwork()
            return bOK

    def get_linesfromnetwork(self):
        """Retrieves lines from the PowerFactory network."""
        bOK = True
        if bOK:
            lines = gbl.Engine.m_pFApp.GetCalcRelevantObjects("ElmLne")
            gbl.Msg.AddRawMessage(f"Total lines retrieved successfully from the network: {len(lines)}")
            for line in lines:
                line_id = line.GetAttribute("loc_name")
                self.branch_dictionary[line_id] = line
                terminal1 = line.GetAttribute("bus1")
                terminal2 = line.GetAttribute("bus2")
                if terminal1 and terminal2:
                    bus1_id = self._standardize_terminal_id(terminal1)
                    bus2_id = self._standardize_terminal_id(terminal2)
                    if bus1_id and bus2_id and bus1_id in self.terminal_dictionary and bus2_id in self.terminal_dictionary:
                        line_datamodel = gbl.DataFactory.createbranch(bus1_id, bus2_id, 0, line_id)
                        if line_datamodel is None:
                            gbl.Msg.AddError(f"Failed to create line for terminals {bus1_id} and {bus2_id}.")
                            continue
                        if not self.getlinevaluesfromnetwork(line_datamodel):
                            gbl.Msg.AddError(f"Failed to retrieve values for line {line_datamodel.BranchID}.")
                            continue
                        gbl.DataModelManager.Branch_TAB.append(line_datamodel)
        gbl.Msg.AddRawMessage(f"Total lines added to DataModel: {len(gbl.DataModelManager.Branch_TAB)}")
        return bOK

    def getlinevaluesfromnetwork(self, line_datamodel):
        """Retrieves line values from the PowerFactory network."""
        bOK = True
        if bOK:
            line_obj = self.branch_dictionary.get(line_datamodel.BranchID)
            if line_obj:
                name = line_obj.GetAttribute("loc_name")
                ON = not(bool(line_obj.GetAttribute("outserv")))

                if name is None or ON is None:
                    gbl.Msg.AddError(f"Failed to retrieve values for line {line_datamodel.BranchID}.")
                    bOK = False
                else:
                    line_datamodel.name = name
                    line_datamodel.ON = ON

        return bOK
    
    def get_transformersfromnetwork(self):
        pass

#____________________LOAD METHODS________________________#

    def getloadsfromnetwork(self):
        """Retrieves loads from the PowerFactory network."""
        bOK = True
        if bOK:
            loads = gbl.Engine.m_pFApp.GetCalcRelevantObjects("ElmLod")
            gbl.Msg.AddRawMessage(f"Total loads retrieved successfully from the network: {len(loads)}")
            for load in loads:
                load_id = load.GetAttribute("loc_name")
                self.load_dictionary[load_id] = load
                terminal = load.GetAttribute("bus1")
                if terminal:
                    bus_id = self._standardize_terminal_id(terminal)
                    if bus_id and bus_id in self.terminal_dictionary:
                        load_item = gbl.DataFactory.createload(bus_id, load_id)
                        if load_item is None:
                            gbl.Msg.AddError(f"Failed to create load for terminal {bus_id}.")
                            continue
                        if not self.getloadvaluesfromnetwork(load_item):
                            gbl.Msg.AddError(f"Failed to retrieve values for load {load_item.LoadID}.")
                            continue
                        if not gbl.DataModelManager.addloadtotab(load_item):
                            gbl.Msg.AddError(f"Failed to add load {load_item.LoadID} to DataModel.")
                            continue
        gbl.Msg.AddRawMessage(f"Total loads added to DataModel: {len(gbl.DataModelManager.Load_TAB)}")
        return bOK
    
    def getloadvaluesfromnetwork(self, load_item):
        """Retrieves load values from the PowerFactory network."""
        bOK = True
        if bOK:
            load_obj = self.load_dictionary.get(load_item.LoadID)
            if load_obj:
                name = load_obj.GetAttribute("loc_name")
                P = load_obj.GetAttribute("plini")
                Q = load_obj.GetAttribute("qlini")
                ON = not(bool(load_obj.GetAttribute("outserv")))
                
                if name is None or P is None or Q is None or ON is None:
                    gbl.Msg.AddError(f"Failed to retrieve values for load {load_item.LoadID}.")
                    bOK = False
                else:
                    load_item.name = name
                    load_item.MW = P
                    load_item.MVar = Q
                    load_item.ON = ON
        return bOK
    
    
#____________________GENERATOR METHODS________________________#
    def getgeneratorsfromnetwork(self):
        """Retrieves generators from the PowerFactory network."""
        bOK = True
        if bOK:
            generators = gbl.Engine.m_pFApp.GetCalcRelevantObjects("*.ElmGen, *.ElmGenstat, *.ElmSym")
            gbl.Msg.AddRawMessage(f"Total generators retrieved successfully from the network: {len(generators)}")
            for generator in generators:
                gen_id = generator.GetAttribute("loc_name")
                self.generator_dictionary[gen_id] = generator
                terminal = generator.GetAttribute("bus1")
                if terminal:
                    bus_id = self._standardize_terminal_id(terminal)
                    if bus_id and bus_id in self.terminal_dictionary:
                        gen_item = gbl.DataFactory.creategenerator(bus_id, gen_id)
                        if gen_item is None:
                            gbl.Msg.AddError(f"Failed to create generator for terminal {bus_id}.")
                            continue
                        if not self.getgeneratorvaluesfromnetwork(gen_item):
                            gbl.Msg.AddError(f"Failed to retrieve values for generator {gen_item.GenID}.")
                            continue
                        if not gbl.DataModelManager.addgentotab(gen_item):
                            gbl.Msg.AddError(f"Failed to add generator {gen_item.GenID} to DataModel.")
                            continue
        gbl.Msg.AddRawMessage(f"Total generators added to DataModel: {len(gbl.DataModelManager.Gen_TAB)}")
        return bOK
    
    def getgeneratorvaluesfromnetwork(self, gen_item):
        """Retrieves generator values from the PowerFactory network."""
        bOK = True
        if bOK:
            gen_obj = self.generator_dictionary.get(gen_item.GenID)
            if gen_obj:
                name = gen_obj.GetAttribute("loc_name")
                P = gen_obj.GetAttribute("pgini")
                Q = gen_obj.GetAttribute("qgini")
                ON = not(bool(gen_obj.GetAttribute("outserv")))
                pf = gen_obj.GetAttribute("cosgini")
                Pnom = gen_obj.GetAttribute("Pnom")
                Qmax = gen_obj.GetAttribute("cQ_max")
                Qmin = gen_obj.GetAttribute("cQ_min")
                
                if any(x is None for x in [name, P, Q, ON, pf, Pnom, Qmax, Qmin]):
                    gbl.Msg.AddError(f"Failed to retrieve values for generator {gen_item.GenID}.")
                    bOK = False
                else:
                    gen_item.name = name
                    gen_item.MW = P
                    gen_item.MVar = Q
                    gen_item.ON = ON
                    gen_item.pf = pf
                    gen_item.MWCapacity = Pnom
                    gen_item.Qmax = Qmax
                    gen_item.Qmin = Qmin
        return bOK
                