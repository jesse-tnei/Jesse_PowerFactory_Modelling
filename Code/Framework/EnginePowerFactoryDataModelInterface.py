# This module retrives data from PowerFactory engine, creates a data model, and manages the transfer of data between the network and the data model.

from Framework import GlobalRegistry as gbl
from Framework.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
class EnginePowerFactoryDataModelInterface(EngineDataModelInterfaceContainer):
    def __init__(self, gbl):
        EngineDataModelInterfaceContainer.__init__(self)
        self.terminal_dictionary = {}  # Dictionary to hold terminal IDs and their corresponding bus IDs
        self.load_dictionary = {}  # Dictionary to hold load IDs and their corresponding bus IDs
        
        
     
     
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
            terminal_id = f"{current.GetAttribute('loc_name')}_{current.GetAttribute('uknom')}"
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
                        load_data = gbl.DataFactory.createload(bus_id, load_id)
                        if load_data is None:
                            gbl.Msg.AddError(f"Failed to create load for terminal {bus_id}.")
                            continue
                        if not self.getloadvaluesfromnetwork(load_data):
                            gbl.Msg.AddError(f"Failed to retrieve values for load {load_data.LoadID}.")
                            continue
                        if not gbl.DataModelManager.addloadtotab(load_data):
                            gbl.Msg.AddError(f"Failed to add load {load_data.LoadID} to DataModel.")
                            continue
        gbl.Msg.AddRawMessage(f"Total loads added to DataModel: {len(self.load_dictionary)}")
        return bOK
    
    def getloadvaluesfromnetwork(self, load):
        """Retrieves load values from the PowerFactory network."""
        bOK = True
        if bOK:
            load_obj = self.load_dictionary.get(load.LoadID)
            if load_obj:
                name = load_obj.GetAttribute("loc_name")
                P = load_obj.GetAttribute("plini")
                Q = load_obj.GetAttribute("qlini")
                ON = not(bool(load_obj.GetAttribute("outserv")))
                
                if name is None or P is None or Q is None or ON is None:
                    gbl.Msg.AddError(f"Failed to retrieve values for load {load.LoadID}.")
                    bOK = False
                else:
                    load.name = name
                    load.MW = P
                    load.MVar = Q
                    load.ON = ON
        return bOK
                