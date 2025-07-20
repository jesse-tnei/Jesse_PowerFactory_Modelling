# This module retrives data from PowerFactory engine, creates a data model, and manages the transfer of data between the network and the data model.

from Framework import GlobalRegistry as gbl
from Framework.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
class EnginePowerFactoryDataModelInterface(EngineDataModelInterfaceContainer):
    def __init__(self, gbl):
        EngineDataModelInterfaceContainer.__init__(self)
        self.m_oEngine = gbl.Engine
        self.m_oMsg = gbl.Msg
        self.powerfactoryobject = gbl.Engine.m_pFApp
        self.terminal_dictionary = {}  # Dictionary to hold terminal IDs and their corresponding bus IDs
        
        
    def getbusbarsfromnetwork(self):
        """Retrieves busbars from the PowerFactory network."""
        bOK = True
        if bOK:
            terminals = self.powerfactoryobject.GetCalcRelevantObjects("ElmTerm")   
        if terminals:
            self.m_oMsg.AddRawMessage(f"{len(terminals)} busbars retrieved successfully from the network.")
            for terminal in terminals:
                terminal_id = self._standardize_terminal_id(terminal)
                self.terminal_dictionary[terminal_id] = terminal
            
                busbar = self.gbl.DataModelManager.getbusbarfromterminal(terminal_id)
            return busbar
                
                
            
        return bOK
    
    def _standardize_terminal_id(self, terminal: object) -> str:
        """Standardizes the bus ID to a consistent format."""
        current = terminal
        while current and current.GetClassName() != "ElmTerm":
            current = current.GetParent()
            
        if current:
            terminal_id = f"{current.GetAttribute('loc_name')}_{current.GetAttribute('uknom')}"
            return terminal_id
        