# This module retrives data from PowerFactory engine, creates a data model, and manages the transfer of data between the network and the data model.

from Framework import GlobalRegistry as gbl
from Framework.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
class EnginePowerFactoryDataModelInterface(EngineDataModelInterfaceContainer):
    def __init__(self, gbl):
        EngineDataModelInterfaceContainer.__init__(self)
        self.terminal_dictionary = {}  # Dictionary to hold terminal IDs and their corresponding bus IDs
        
        
        
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
        
        