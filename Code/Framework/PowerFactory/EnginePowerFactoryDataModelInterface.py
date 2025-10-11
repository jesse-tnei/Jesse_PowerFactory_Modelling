# This module retrives data from PowerFactory engine, creates a data model, and manages the transfer of data between the network and the data model.

from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
class EnginePowerFactoryDataModelInterface(EngineDataModelInterfaceContainer):
    def __init__(self):
        EngineDataModelInterfaceContainer.__init__(self)
        self.terminal_dictionary = {}  # Dictionary to hold terminal IDs and their corresponding bus IDs
        self.load_dictionary = {}  # Dictionary to hold load IDs and their corresponding bus IDs
        
        self.generator_dictionary = {}  # Dictionary to hold generator IDs and their corresponding bus IDs
        self.branch_dictionary = {}  # Dictionary to hold branch IDs and their corresponding bus IDs
        
        
        
    
    
    #____________________OVERALL DATAMODELMANAGER LOADING METHODS________________________#  
    # def passelementsfromnetworktodatamodelmanager(self):
    #     """This method retrieves elements from the network and passes them to the DataModelManager."""
    #     bOK = True
    #     if bOK:
    #         bOK = self.getbusbarsfromnetwork()
    #     if bOK:
    #         bOK = self.getbranchesfromnetwork()
    #     if bOK:
    #         bOK = self.getgeneratorsfromnetwork()
    #     if bOK:
    #         bOK = self.getloadsfromnetwork()
    #     if bOK:
    #         bOK = self.getexternalgridsfromnetwork()
    #     return bOK

    #____________________BUSBAR METHODS________________________#


    def getbusbarsfromnetwork(self):
        """Retrieves busbars from the PowerFactory network."""
        bOK = True
        if bOK:
            terminals = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("ElmTerm")   
        if terminals:
            gbl.Msg.AddRawMessage(f"Total busbars retrieved successfully from the network: {len(terminals)}")
            for terminal in terminals:
                terminal_id = self.standardize_terminal_id(terminal)
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
    
    def standardize_terminal_id(self, terminal: object) -> str:
        """Standardizes the bus ID to a consistent format."""
        current = terminal
        while current and current.GetClassName() != "ElmTerm":
            current = current.GetParent()
            
        if current:
            terminal_id = f"{current.GetAttribute('loc_name')}_{current.GetAttribute('loc_name')}_{current.GetAttribute('uknom')}"
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
            lines = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("ElmLne")
            gbl.Msg.AddRawMessage(f"Total lines retrieved successfully from the network: {len(lines)}")
            for line in lines:
                line_id = line.GetAttribute("loc_name")
                self.branch_dictionary[line_id] = line
                terminal1 = line.GetAttribute("bus1")
                terminal2 = line.GetAttribute("bus2")
                if terminal1 and terminal2:
                    bus1_id = self.standardize_terminal_id(terminal1)
                    bus2_id = self.standardize_terminal_id(terminal2)
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
        """Retrieves transformers from the PowerFactory network."""
        bOK = True
        initialbranchtablength = len(gbl.DataModelManager.Branch_TAB)
        if bOK:
            transformers = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmTr2,")
            gbl.Msg.AddRawMessage(f"Total transformers retrieved successfully from the network: {len(transformers)}")
            for transformer in transformers:
                transformer_id = transformer.GetAttribute("loc_name")
                self.branch_dictionary[transformer_id] = transformer
                terminal1 = transformer.GetAttribute("bushv")
                terminal2 = transformer.GetAttribute("buslv")
                terminal3 = transformer.GetAttribute("busmv") if hasattr(transformer, 'busmv') else None
                if terminal1 and terminal2 and not terminal3:
                    bus1_id = self.standardize_terminal_id(terminal1)
                    bus2_id = self.standardize_terminal_id(terminal2)
                    if bus1_id and bus2_id and bus1_id in self.terminal_dictionary and bus2_id in self.terminal_dictionary:
                        transformer_datamodel = gbl.DataFactory.createbranch(bus1_id, bus2_id, 0, transformer_id)
                        if transformer_datamodel is None:
                            gbl.Msg.AddError(f"Failed to create transformer for terminals {bus1_id} and {bus2_id}.")
                            continue
                        transformer_datamodel.IsTransformer = True
                        if not self.gettransformervvaluesfromnetwork(transformer_datamodel):
                            gbl.Msg.AddError(f"Failed to retrieve values for transformer {transformer_datamodel.BranchID}.")
                            continue
                        gbl.DataModelManager.Branch_TAB.append(transformer_datamodel)
                        
                if terminal1 and terminal2 and terminal3:
                    bus1_id = self.standardize_terminal_id(terminal1)
                    bus2_id = self.standardize_terminal_id(terminal2)
                    bus3_id = self.standardize_terminal_id(terminal3)
                    if bus1_id and bus2_id and bus3_id and bus1_id in self.terminal_dictionary and bus2_id in self.terminal_dictionary and bus3_id in self.terminal_dictionary:
                        transformer_datamodel = gbl.DataFactory.createbranch(bus1_id, bus2_id, bus3_id, transformer_id)
                        if transformer_datamodel is None:
                            gbl.Msg.AddError(f"Failed to create transformer for terminals {bus1_id}, {bus2_id}, and {bus3_id}.")
                            continue
                        transformer_datamodel.IsTransformer = True
                        transformer_datamodel.Is3WTransformer = True
                        if not self.gettransformervvaluesfromnetwork(transformer_datamodel):
                            gbl.Msg.AddError(f"Failed to retrieve values for transformer {transformer_datamodel.BranchID}.")
                            continue
                        gbl.DataModelManager.Branch_TAB.append(transformer_datamodel)
        gbl.Msg.AddRawMessage(f"Total transformers added to DataModel: {len(gbl.DataModelManager.Branch_TAB) - initialbranchtablength}")
        return bOK
    
    def gettransformervvaluesfromnetwork(self, transformer_datamodel):
        """Retrieves transformer values from the PowerFactory network."""
        bOK = True
        if bOK:
            transformer_obj = self.branch_dictionary.get(transformer_datamodel.BranchID)
            if transformer_obj:
                name = transformer_obj.GetAttribute("loc_name")
                ON = not(bool(transformer_obj.GetAttribute("outserv")))

                if name is None or ON is None:
                    gbl.Msg.AddError(f"Failed to retrieve values for transformer {transformer_datamodel.BranchID}.")
                    bOK = False
                else:
                    transformer_datamodel.Txname = name
                    transformer_datamodel.ON = ON

        return bOK







#____________________LOAD METHODS________________________#

    def getloadsfromnetwork(self):
        """Retrieves loads from the PowerFactory network."""
        bOK = True
        if bOK:
            loads = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("ElmLod")
            gbl.Msg.AddRawMessage(f"Total loads retrieved successfully from the network: {len(loads)}")
            for load in loads:
                load_id = load.GetAttribute("loc_name")
                self.load_dictionary[load_id] = load
                terminal = load.GetAttribute("bus1")
                if terminal:
                    bus_id = self.standardize_terminal_id(terminal)
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
            generators = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmGen, *.ElmGenstat, *.ElmSym")
            gbl.Msg.AddRawMessage(f"Total generators retrieved successfully from the network: {len(generators)}")
            for generator in generators:
                gen_id = generator.GetAttribute("loc_name")
                self.generator_dictionary[gen_id] = generator
                terminal = generator.GetAttribute("bus1")
                if terminal:
                    bus_id = self.standardize_terminal_id(terminal)
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
    
    def getexternalgridsfromnetwork(self):
        """Retrieves external grids from the PowerFactory network."""
        bOK = True
        initialgentablength = len(gbl.DataModelManager.Gen_TAB)
        if bOK:
            external_grids = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("ElmXnet")
            gbl.Msg.AddRawMessage(f"Total external grids retrieved successfully from the network: {len(external_grids)}")
            for ext_grid in external_grids:
                ext_grid_id = ext_grid.GetAttribute("loc_name")
                terminal = ext_grid.GetAttribute("bus1")
                if terminal:
                    bus_id = self.standardize_terminal_id(terminal)
                    if bus_id and bus_id in self.terminal_dictionary:
                        self.generator_dictionary[ext_grid_id] = ext_grid
                        ext_grid_item = gbl.DataFactory.creategenerator(bus_id, ext_grid_id)
                        if ext_grid_item is None:
                            gbl.Msg.AddError(f"Failed to create external grid for terminal {bus_id}.")
                            continue
                        ext_grid_item.IsExternalGrid = True
                        if not self.getexternalgridvaluesfromnetwork(ext_grid_item):
                            gbl.Msg.AddError(f"Failed to retrieve values for external grid {ext_grid_item.GenID}.")
                            continue
                        if ext_grid_item.BusType == "SL":
                            ext_grid_item.oBus1.Slack = True
                        if not gbl.DataModelManager.addgentotab(ext_grid_item):
                            gbl.Msg.AddError(f"Failed to add external grid {ext_grid_item.GenID} to DataModel.")
                            continue
        gbl.Msg.AddRawMessage(f"Total external grids added to DataModel: {len(gbl.DataModelManager.Gen_TAB) - initialgentablength}")
        return bOK
        
    def getexternalgridvaluesfromnetwork(self, ext_grid_item):
        """Retrieves external grid values from the PowerFactory network."""
        bOK = True
        if bOK:
            ext_grid_obj = self.generator_dictionary.get(ext_grid_item.GenID)
            if ext_grid_obj:
                name = ext_grid_obj.GetAttribute("loc_name")
                bustype = ext_grid_obj.GetAttribute("bustp")
                apparent_power = ext_grid_obj.GetAttribute("sgini")
                ON = not(bool(ext_grid_obj.GetAttribute("outserv")))
                pf = ext_grid_obj.GetAttribute("cosgini")
                inductiveorcapacitive = ext_grid_obj.GetAttribute("pf_recap") if hasattr(ext_grid_obj, 'pf_recap') else None
                if inductiveorcapacitive == 0:
                    inductiveorcapacitive = "Inductive"
                elif inductiveorcapacitive == 1:
                    inductiveorcapacitive = "Capacitive"

                if any(x is None for x in [name, bustype, apparent_power, ON, pf, inductiveorcapacitive]):
                    gbl.Msg.AddError(f"Failed to retrieve values for external grid {ext_grid_item.ExtGridID}.")
                    bOK = False
                else:
                    ext_grid_item.name = name
                    ext_grid_item.MVA = apparent_power
                    ext_grid_item.inductiveorcapacitive = inductiveorcapacitive
                    ext_grid_item.ON = ON
                    ext_grid_item.pf = pf
                    ext_grid_item.BusType = bustype
        return bOK
                