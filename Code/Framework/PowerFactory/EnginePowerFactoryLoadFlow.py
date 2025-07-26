from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineLoadFlowContainer import EngineLoadFlowContainer as BaseEngineLoadFlowContainer


class EnginePowerFactoryLoadFlow(BaseEngineLoadFlowContainer):
    def __init__(self):
        super().__init__()
        self.powerfactoryloadflowobject = gbl.EngineContainer.m_pFApp.GetFromStudyCase("ComLdf")
        self.busbar_results = {}  # Dictionary to hold busbar results
        self.datamodel_busbar_tab = gbl.DataModelManager.Busbar_TAB
        self.datamodel_branch_tab = gbl.DataModelManager.Branch_TAB
        self.busbarloadflowresultsdata = []  # List to hold busbar load flow results data
        self.lineloadflowresultsdata = []  # List to hold line load flow results data

    #__________________________ENGINE POWER FACTORY LOAD FLOW METHODS________________________
    def runloadflow(self):
        """This method runs the load flow analysis."""
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Running PowerFactory Load Flow Analysis...")
        ierr = self.powerfactoryloadflowobject.Execute()
        if ierr != 0:
            gbl.Msg.add_error("PowerFactory Load Flow Analysis failed with error code: {}".format(ierr))
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("PowerFactory Load Flow Analysis completed successfully.")
        return True
    def getandupdatebusbarloadflowresults(self):
        """This method retrieves the results of the load flow analysis."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving busbar load flow results...")
            bOK = self.getbusbarloadflowresultsdatafromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve busbar load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating busbar load flow results data tab...")
        bOK = self.setbusbarloadflowresultsdatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Busbar load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update busbar load flow results data tab.")
                return False
        return True
    
    def getbusbarloadflowresultsdatafromnetwork(self):
        """This method retrieves the busbar data from the load flow analysis."""
        busbars = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmTerm")
        self.busbar_loadflow_results_data = []
        for bus in busbars:
            name = gbl.DataModelInterfaceContainer.standardize_terminal_id(bus)
            if name not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            voltage = bus.GetAttribute("m:u")
            angle = bus.GetAttribute("m:phiu")
            self.busbarloadflowresultsdata.append({
                "name": name,
                "voltage": voltage,
                "angle": angle
            })
        return self.busbarloadflowresultsdata
    
    def setbusbarloadflowresultsdatatab(self):
        """This method updates the busbar load flow results data tab."""
        if not self.busbarloadflowresultsdata:
            gbl.Msg.add_warning("No busbar load flow results data available to update the tab.")
            return False
        for bus in self.busbarloadflowresultsdata:
            busbar, _ = gbl.DataModelManager.findbusbar(bus["name"])
            if busbar is None:
                gbl.Msg.add_warning(f"Busbar {bus['name']} not found in the tab.")
                continue
            busbar.voltage = bus["voltage"]
            busbar.angle = bus["angle"]
        return True
    
    def getandupdatelineloadflowresults(self):
        """This method retrieves the line load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving line load flow results...")
            bOK = self.getlineloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve line load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating line load flow results data tab...")
        bOK = self.setlineloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Line load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update line load flow results data tab.")
                return False
        return True
    def getlineloadflowresultsfromnetwork(self):
        """This method retrieves the line load flow results from the network."""
        lines = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmLne")
        
        for line in lines:
            name = line.GetAttribute("loc_name")
            terminal1 = line.GetAttribute("bus1")
            terminal2 = line.GetAttribute("bus2")
            bus1_id = bus2_id = None
            if terminal1 and terminal2:
                bus1_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal1)
                bus2_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal2)
            if name not in gbl.DataModelInterfaceContainer.branch_dictionary or bus1_id not in gbl.DataModelInterfaceContainer.terminal_dictionary or bus2_id not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            bus1_pu_voltage = line.GetAttribute("n:u:bus1")
            bus2_pu_voltage = line.GetAttribute("n:u:bus2")
            bus1_MW = line.GetAttribute("m:P:bus1")
            bus2_MW = line.GetAttribute("m:P:bus2")
            bus1MVAr = line.GetAttribute("m:Q:bus1")
            bus2MVAr = line.GetAttribute("m:Q:bus2")
            bus1MVA = line.GetAttribute("m:S:bus1")
            bus2MVA = line.GetAttribute("m:S:bus2")
            loading = line.GetAttribute("c:loading")
            self.lineloadflowresultsdata.append({
                "name": name,
                "bus1": bus1_id,
                "bus2": bus2_id,
                "loading": loading,
                "bus1_pu_voltage": bus1_pu_voltage,
                "bus2_pu_voltage": bus2_pu_voltage,
                "bus1_MW": bus1_MW,
                "bus2_MW": bus2_MW,
                "bus1MVAr": bus1MVAr,
                "bus2MVAr": bus2MVAr,
                "bus1MVA": bus1MVA,
                "bus2MVA": bus2MVA,
            })
        return self.lineloadflowresultsdata
    def setlineloadflowresultstodatatab(self):
        """This method updates the line load flow results data tab."""
        if not self.lineloadflowresultsdata:
            gbl.Msg.add_warning("No line load flow results data available to update the tab.")
            return False
        for line in self.lineloadflowresultsdata:

            branch, _ = gbl.DataModelManager.findbranch( line["bus1"], line["bus2"], None, line["name"])
            if branch is None:
                gbl.Msg.add_warning(f"Branch {line['name']} not found in the tab.")
                continue
            branch.loading = line["loading"]
            branch.oBus1.voltage = line["bus1_pu_voltage"]
            branch.oBus2.voltage = line["bus2_pu_voltage"]
            branch.oBus1.MW = line["bus1_MW"]
            branch.oBus2.MW = line["bus2_MW"]
            branch.oBus1.MVAr = line["bus1MVAr"]
            branch.oBus2.MVAr = line["bus2MVAr"]
            branch.oBus1.MVA = line["bus1MVA"]
            branch.oBus2.MVA = line["bus2MVA"]
            branch.oBus1.LoadFlowResults = branch.oBus2.LoadFlowResults = branch.Results = True
        return True
        

