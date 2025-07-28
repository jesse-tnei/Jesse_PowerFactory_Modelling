from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineLoadFlowContainer import EngineLoadFlowContainer as BaseEngineLoadFlowContainer


class EnginePowerFactoryLoadFlow(BaseEngineLoadFlowContainer):
    def __init__(self):
        super().__init__()
        self.powerfactoryloadflowobject = gbl.EngineContainer.m_pFApp.GetFromStudyCase("ComLdf")
        self.busbar_results = {}  # Dictionary to hold busbar results
        self.busbarloadflowresultsdata = []  # List to hold busbar load flow results data
        self.lineloadflowresultsdata = []  # List to hold line load flow results data
        self.txloadflowresultsdata = []  # List to hold transformer load flow results data
        self.generatorloadflowresultsdata = []  # List to hold generator load flow results data
        self.loadflowresultsdata = []  # List to hold load flow results data

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
    
    #__________________________BUSBAR LOAD FLOW RESULTS METHODS________________________
    def getandupdatebusbarloadflowresults(self):
        """This method retrieves the results of the load flow analysis. It functions as an aggregator for the busbar load flow results."""
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
        """This method retrieves the busbar data from the load flow analysis and saves it in a temporary list."""
        busbars = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmTerm")
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
        """This method takes in the loaded busbar load flow results data and updates the busbar load flow results data tab inside the datamodelmanager."""
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
            busbar.LoadFlowResults = True
        return True
    
    #__________________________LINE LOAD FLOW METHODS________________________
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
    
    #__________________________TRANSFORMER LOAD FLOW RESULTS METHODS________________________
    def gettransformerflowresultsfromnetwork(self):
        """This method retrieves the transformer load flow results."""
        transformers = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmTr2")
        for transformer in transformers:
            name = transformer.GetAttribute("loc_name")
            terminal1 = transformer.GetAttribute("bushv")
            terminal2 = transformer.GetAttribute("buslv")
            bus1_id = bus2_id = None
            if terminal1 and terminal2:
                bus1_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal1)
                bus2_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal2)
            if name not in gbl.DataModelInterfaceContainer.branch_dictionary or bus1_id not in gbl.DataModelInterfaceContainer.terminal_dictionary or bus2_id not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            bus1_pu_voltage = transformer.GetAttribute("n:u:bushv")
            bus2_pu_voltage = transformer.GetAttribute("n:u:buslv")
            loading = transformer.GetAttribute("c:loading")
            tap_position = transformer.GetAttribute("c:nntap")
            self.txloadflowresultsdata.append({
                "name": name,
                "bushv": bus1_id,
                "buslv": bus2_id,
                "loading": loading,
                "tap_position": tap_position,
                "bus1_pu_voltage": bus1_pu_voltage,
                "bus2_pu_voltage": bus2_pu_voltage
            })
            
        return True
    
    def settransformerflowresultstodatatab(self):
        """This method updates the transformer load flow results data tab."""
        if not self.txloadflowresultsdata:
            gbl.Msg.add_warning("No transformer load flow results data available to update the tab.")
            return False
        for transformer in self.txloadflowresultsdata:
            branch, _ = gbl.DataModelManager.findbranch(transformer["bushv"], transformer["buslv"], None, transformer["name"])
            if branch is None:
                gbl.Msg.add_warning(f"Transformer {transformer['name']} not found in the tab.")
                continue
            branch.loading = transformer["loading"]
            branch.tap_position = transformer["tap_position"]
            # Update the busbar load flow results - only update if not already set from when collecting line results
            if branch.oBus1.LoadFlowResults is None:
                branch.oBus1.voltage = transformer["bus1_pu_voltage"]
                branch.oBus1.LoadFlowResults = True
            if branch.oBus2.LoadFlowResults is None:
                branch.oBus2.voltage = transformer["bus2_pu_voltage"]
                branch.oBus2.LoadFlowResults = branch.Results = True
                
        return True
    
    def getandupdatetransformerflowresults(self):
        """This method retrieves the transformer load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving transformer load flow results...")
            bOK = self.gettransformerflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve transformer load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating transformer load flow results data tab...")
        bOK = self.settransformerflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Transformer load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update transformer load flow results data tab.")
                return False
        return True
    
    #__________________________GENERATOR LOAD FLOW RESULTS METHODS________________________
    def getgeneratorloadflowresultsfromnetwork(self):
        """This method retrieves the generator load flow results from the network."""
        generators = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmGen, *.ElmGenstat, *.ElmSym")
        for generator in generators:
            name = generator.GetAttribute("loc_name")
            terminal = generator.GetAttribute("bus1")
            bus_id = None
            if terminal:
                bus_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal)
            if name not in gbl.DataModelInterfaceContainer.generator_dictionary or bus_id not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            MW = generator.GetAttribute("m:P:bus1")
            MVAR = generator.GetAttribute("m:Q:bus1")
            MVA = generator.GetAttribute("m:S:bus1")
            parallel_machines = generator.GetAttribute("e:ngnum")
            Rated_MVA = generator.GetAttribute("t:sgn")
            pu_voltage = generator.GetAttribute("n:u:bus1")
            powerfactor = generator.GetAttribute("m:cosphi:bus1")
            self.generatorloadflowresultsdata.append({
                "name": name,
                "bus": bus_id,
                "MW": MW,
                "MVAR": MVAR,
                "MVA": MVA,
                "parallel_machines": parallel_machines,
                "Rated_MVA": Rated_MVA,
                "pu_voltage": pu_voltage,
                "powerfactor": powerfactor
            })
        return self.generatorloadflowresultsdata
    
    def setgeneratorloadflowresultstodatatab(self):
        """This method updates the generator load flow results data tab."""
        if not self.generatorloadflowresultsdata:
            gbl.Msg.add_warning("No generator load flow results data available to update the tab.")
            return False
        for generator in self.generatorloadflowresultsdata:
            gen, _ = gbl.DataModelManager.findgen(generator["bus"], generator["name"])
            if gen is None:
                gbl.Msg.add_warning(f"Generator {generator['name']} not found in the tab.")
                continue
            gen.MWLoadFlow = generator["MW"]
            gen.MVarLoadFlow = generator["MVAR"]
            gen.MVALoadFlow = generator["MVA"]
            gen.RatedMVA = generator["Rated_MVA"]
            gen.VMagPu = generator["pu_voltage"]
            gen.powerFactor = generator["powerfactor"]
            gen.parallelmachines = generator["parallel_machines"]
            gen.LoadFlowResults = True
        return True
    
    def getandupdateloadflowgeneratorresults(self):
        """This method retrieves the generator load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving generator load flow results...")
            bOK = self.getgeneratorloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve generator load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating generator load flow results data tab...")
        bOK = self.setgeneratorloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Generator load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update generator load flow results data tab.")
                return False
        return True
    
    #__________________________LOAD LOAD FLOW RESULTS METHODS________________________
    def getloadloadflowresultsfromnetwork(self):
        """This method retrieves the load load flow results from the network."""
        loads = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmLod")
        for load in loads:
            name = load.GetAttribute("loc_name")
            terminal = load.GetAttribute("bus1")
            bus_id = None
            if terminal:
                bus_id = gbl.DataModelInterfaceContainer.standardize_terminal_id(terminal)
            if name not in gbl.DataModelInterfaceContainer.load_dictionary or bus_id not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            MW = load.GetAttribute("m:P:bus1")
            MVAR = load.GetAttribute("m:Q:bus1")
            MVA = load.GetAttribute("m:S:bus1")
            pu_voltage = load.GetAttribute("n:u:bus1")
            powerfactor = load.GetAttribute("m:cosphi:bus1")
            self.loadflowresultsdata.append({
                "name": name,
                "bus": bus_id,
                "MW": MW,
                "MVAR": MVAR,
                "MVA": MVA,
                "pu_voltage": pu_voltage,
                "powerfactor": powerfactor
            })

        return self.loadflowresultsdata
    def setloadflowresultstodatatab(self):
        """This method updates the load flow results data tab."""
        if not self.loadflowresultsdata:
            gbl.Msg.add_warning("No load flow results data available to update the tab.")
            return False
        for load in self.loadflowresultsdata:
            load_obj, _ = gbl.DataModelManager.findload(load["bus"], load["name"])
            if load_obj is None:
                gbl.Msg.add_warning(f"Load {load['name']} not found in the tab.")
                continue
            load_obj.MWLoadFlow = load["MW"]
            load_obj.MVarLoadFlow = load["MVAR"]
            load_obj.MVALoadFlow = load["MVA"]
            load_obj.VMagPu = load["pu_voltage"]
            load_obj.powerFactor = load["powerfactor"]
            load_obj.LoadFlowResults = True
        return True
    
    def getandupdateloadsloadflowresults(self):
        """This method retrieves the load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving loads load flow results...")
            bOK = self.getloadloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve loads load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating loads load flow results data tab...")
        bOK = self.setloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Loads load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update loads load flow results data tab.")
                return False
        return True
    
    #__________________________LOAD FLOW REPORTS________________________
    def getloadflowresultsdiagramfromnetwork(self):

        report_cmd = gbl.EngineContainer.m_pFApp.GetFromStudyCase("ComReport")
        if report_cmd is not None:
            # Optionally set report options here, e.g.:
            # report_cmd.iopt_report = 1  # (if needed, check your version's API)
            ierr = report_cmd.Execute()
            if ierr == 0:
                gbl.Msg.add_information("Load flow report generated successfully.")
            else:
                gbl.Msg.add_error(f"Failed to generate load flow report. Error code: {ierr}")
        else:
            gbl.Msg.add_error("ComReport object not found in the study case.")
        # After running ComReport.Execute()
        report_obj = gbl.EngineContainer.m_pFApp.GetFromStudyCase("IntReportdoc")  # or use the specific report name
        if report_obj is not None:
            # Export as PDF
            report_obj.Export(r"C:\path\to\output\report.pdf", 0)  # 0 = export directly, 1 = show dialog
        else:
            gbl.Msg.add_error("Report object not found for export.")
    
        

