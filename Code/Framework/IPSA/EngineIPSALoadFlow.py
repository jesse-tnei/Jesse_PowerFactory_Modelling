from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineLoadFlowContainer import EngineLoadFlowContainer as BaseEngineLoadFlowContainer

import ipsa


class EngineIPSALoadFlow(BaseEngineLoadFlowContainer):

    def __init__(self):
        super().__init__()
        self.network = None
        self.ipsaloadflowobject = None
        self.busbar_results = {}  # Dictionary to hold busbar results
        self.busbarloadflowresultsdata = []  # List to hold busbar load flow results data
        self.lineloadflowresultsdata = []  # List to hold line load flow results data
        self.transformerloadflowresultsdata = []  # List to hold transformer load flow results data
        self.generatorloadflowresultsdata = []  # List to hold generator load flow results data
        self.loadflowresultsdata = []  # List to hold load flow results data

    def _initialize_loadflow_object(self):
        """Initialize the IPSA load flow analysis object"""
        try:
            if gbl.EngineContainer and gbl.EngineContainer.m_network:
                self.network = gbl.EngineContainer.m_network
                self.ipsaloadflowobject = gbl.EngineContainer.m_network.GetAnalysisLF()
            else:
                gbl.Msg.add_warning("No active IPSA network available for load flow analysis.")
        except Exception as e:
            gbl.Msg.add_error(f"Failed to initialize IPSA load flow object: {e}")

    #__________________________IPSA LOAD FLOW METHODS________________________
    def runloadflow(self, **kwargs) -> bool:
        """
            Run IPSA load flow with optional settings.
            Keyword options (subset; extend as needed):
            - calculation_method: "ac" | "dc"                (default "ac")
            - convergence: float                             (IscAnalysisLF.Convergence)
            - max_iterations: int                            (IscAnalysisLF.MaxIterations)
            - no_phase_shift: bool                           (IscAnalysisLF.NoPhaseShift)
            - lock_taps: int                                 (IscAnalysisLF.LockTaps: 0,1,2)
            - single_tap_per_iter: bool                      (IscAnalysisLF.SingleTapMovement)
            - slow_tap_changes: bool                         (IscAnalysisLF.SlowTapMovement)
            - use_load_scaling: bool                         (IscAnalysisLF.UseLoadScaling)
            - real_load_scale: float                         (IscAnalysisLF.RealLoadScale)
            - reactive_load_scale: float                     (IscAnalysisLF.ReactiveLoadScale)
            - which_impedance: int                           (IscAnalysisLF.WhichImpedance: 0 normal, 1 min)
            - island_method: int                             (IscAnalysisLF.IslandMethod: 0,1)
            - dont_update_data: bool                         (keep UI/model values unchanged)
            - no_engine_load: bool                           (reuse current engine state)
            Returns:
            True if converged; False otherwise.
            """
        self._initialize_loadflow_object()
        # Map simple kwargs to IscAnalysisLF fields
        setI = self.ipsaloadflowobject.SetIValue
        setD = self.ipsaloadflowobject.SetDValue
        setB = self.ipsaloadflowobject.SetBValue
        A = ipsa.IscAnalysisLF  # enum holder for field indices

        if "convergence" in kwargs:
            setD(A.Convergence, float(kwargs["convergence"]))
        if "max_iterations" in kwargs:
            setI(A.MaxIterations, int(kwargs["max_iterations"]))
        if "no_phase_shift" in kwargs:
            setB(A.NoPhaseShift, bool(kwargs["no_phase_shift"]))
        if "lock_taps" in kwargs:
            # 0=do not lock, 1=lock during outages only, 2=lock taps
            setI(A.LockTaps, int(kwargs["lock_taps"]))
        if "single_tap_per_iter" in kwargs:
            setB(A.SingleTapMovement, bool(kwargs["single_tap_per_iter"]))
        if "slow_tap_changes" in kwargs:
            setB(A.SlowTapMovement, bool(kwargs["slow_tap_changes"]))
        if "use_load_scaling" in kwargs:
            setB(A.UseLoadScaling, bool(kwargs["use_load_scaling"]))
        if "real_load_scale" in kwargs:
            setD(A.RealLoadScale, float(kwargs["real_load_scale"]))
        if "reactive_load_scale" in kwargs:
            setD(A.ReactiveLoadScale, float(kwargs["reactive_load_scale"]))
        if "which_impedance" in kwargs:
            # 0 = normal (default), 1 = minimum branch resistance
            setI(A.WhichImpedance, int(kwargs["which_impedance"]))
        if "island_method" in kwargs:
            # 0 = slack-only islands get LF; 1 = slack + V-controlled gen required
            setI(A.IslandMethod, int(kwargs["island_method"]))

        # Decide AC vs DC run
        use_dc = (kwargs.get("calculation_method", "ac").lower() == "dc")

        # Execute
        ierr = gbl.EngineContainer.m_network.DoLoadFlow(
            bool(kwargs.get("no_engine_load", False)),
            bool(kwargs.get("dont_update_data", False)),
            bool(use_dc),
        )
        #self.results = self.network.GetLoadFlowResults()
        return bool(ierr)

    def _configure_loadflow_settings(self, settings):
        """Configure IPSA load flow analysis settings"""
        try:
            if self.ipsaloadflowobject:
                # Set convergence and iteration settings
                if 'Convergence' in settings:
                    self.ipsaloadflowobject.Convergence = settings['Convergence']
                if 'MaxIterations' in settings:
                    self.ipsaloadflowobject.MaxIterations = settings['MaxIterations']
                return True
            else:
                gbl.Msg.add_error("IPSA load flow object not initialized.")
                return False
        except Exception as e:
            gbl.Msg.add_error(f"Failed to configure IPSA load flow settings: {e}")
            return False

    def getallloadflowresults(self):
        """This method retrieves all results of the IPSA load flow analysis."""
        bOK = False
        bOK = self.getandupdatebusbarloadflowresults()
        if bOK:
            bOK = self.getandupdatelineloadflowresults()
        if bOK:
            bOK = self.getandupdatetransformerflowresults()
        if bOK:
            bOK = self.getandupdateloadflowgeneratorresults()
        if bOK:
            bOK = self.getandupdateloadsloadflowresults()
        return bOK

    #__________________________BUSBAR LOAD FLOW RESULTS METHODS________________________
    def getandupdatebusbarloadflowresults(self):
        """This method retrieves the results of the IPSA load flow analysis for busbars."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving IPSA busbar load flow results...")
            bOK = self.getbusbarloadflowresultsdatafromnetwork()
        if not bOK:
            gbl.Msg.add_error(
                "Failed to retrieve IPSA busbar load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating busbar load flow results data tab...")
        bOK = self.setbusbarloadflowresultsdatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information(
                    "IPSA busbar load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update IPSA busbar load flow results data tab.")
                return False
        return True

    def getbusbarloadflowresultsdatafromnetwork(self):
        """This method retrieves the busbar data from the IPSA load flow analysis."""
        try:
            if not gbl.EngineContainer.m_network:
                gbl.Msg.add_error("No active IPSA network.")
                return False
            # Get all busbars from IPSA network
            self.terminal_dictionary = self.network.GetBusbars()
            if not self.terminal_dictionary:
                gbl.Msg.add_warning("No busbars found in the network.")
                return False
            self.busbarloadflowresultsdata = []
            for terminal_key, terminal_obj in self.terminal_dictionary.items():
                # if terminal_key not in gbl.DataModelInterface.terminal_dictionary:
                #     continue
                busbar = self.terminal_dictionary[terminal_key]
                if busbar is None:
                    continue
                # Attributes aligned to your model & IPSA enums you set during buil
                self.busbarloadflowresultsdata.append({
                    "name": terminal_key,
                    "voltage": busbar.GetVoltageMagnitudePU(),
                    "angle": busbar.GetVoltageAngleDeg(),
                    'loadflowresults': True
                })
            return self.busbarloadflowresultsdata
        except Exception as e:
            gbl.Msg.add_error(
                f"Failed to retrieve busbar load flow results data from the network: {e}")
            return False

    def setbusbarloadflowresultsdatatab(self):
        """This method updates the busbar load flow results data tab in the data model."""
        if not self.busbarloadflowresultsdata:
            gbl.Msg.add_warning(
                "No IPSA busbar load flow results data available to update the tab.")
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
        """This method retrieves the IPSA line load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving IPSA line load flow results...")
            bOK = self.getlineloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error(
                "Failed to retrieve IPSA line load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating IPSA line load flow results data tab...")
        bOK = self.setlineloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information(
                    "IPSA line load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update IPSA line load flow results data tab.")
                return False
        return True

    def getlineloadflowresultsfromnetwork(self):
        """This method retrieves the line load flow results from the IPSA network."""
        try:
            if not gbl.EngineContainer.m_network:
                gbl.Msg.add_error("No active IPSA network.")
                return False
            self.line_dictionary = self.network.GetBranches()
            if not self.line_dictionary:
                gbl.Msg.add_warning("No lines found in the network.")
                return False
            for line_key, line_obj in self.line_dictionary.items():
                if line_obj is None:
                    continue
                # Attributes aligned to your model & IPSA enums you set during build
                try:
                    name = line_key
                    bus1 = line_obj.GetSValue(ipsa.IscBranch.FromBusName)
                    bus2 = line_obj.GetSValue(ipsa.IscBranch.ToBusName)
                    fromMW = line_obj.GetSendRealPowerMW()
                    fromMvar = line_obj.GetSendReactivePowerMVAr()
                    toMW = line_obj.GetReceiveRealPowerMW()
                    toMvar = line_obj.GetReceiveReactivePowerMVAr()
                    lossMW = line_obj.GetLossesMW()
                    lossMVAr = line_obj.GetLossesMVAr()
                    headroompercentage = line_obj.GetCapacityHeadroomPC()
                    self.lineloadflowresultsdata.append({
                        "name": name,
                        "bus1": bus1,
                        "bus2": bus2,
                        "headroom": headroompercentage,
                        "fromMW": fromMW,
                        "toMW": toMW,
                        "fromMvar": fromMvar,
                        "toMvar": toMvar,
                        "lossMW": lossMW,
                        "lossMVAr": lossMVAr
                    })
                except Exception as e:
                    gbl.Msg.add_warning(f"Line attribute copy failed for '{line_key}': {e}")
            return self.lineloadflowresultsdata
        except Exception as e:
            gbl.Msg.add_error(f"Failed to retrieve IPSA line results: {e}")
            return False

    def setlineloadflowresultstodatatab(self):
        """This method updates the line load flow results data tab."""
        if not self.lineloadflowresultsdata:
            gbl.Msg.add_warning("No IPSA line load flow results data available to update the tab.")
            return False
        for line in self.lineloadflowresultsdata:
            branch, _ = gbl.DataModelManager.findbranch(line["bus1"], line["bus2"], None,
                                                        line["name"])
            if branch is None:
                gbl.Msg.add_warning(f"Branch {line['name']} not found in the tab.")
                continue
            branch.headroom = line["headroom"]
            branch.lossMW = line["lossMW"]
            branch.lossMVAr = line["lossMVAr"]
            branch.oBus1.MW = line["fromMW"]
            branch.oBus2.MW = line["toMW"]
            branch.oBus1.MVAr = line["fromMvar"]
            branch.oBus2.MVAr = line["toMvar"]
            branch.oBus1.LoadFlowResults = branch.oBus2.LoadFlowResults = branch.Results = True
        return True

    #___________________GENERATOR LOAD FLOW RESULTS METHODS - NEEDS FIX________________________
    def getandupdateloadflowgeneratorresults(self):
        """This method retrieves the IPSA generator load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving IPSA generator load flow results...")
            bOK = self.getgeneratorloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve IPSA generator load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating IPSA generator load flow results data tab...")
        bOK = self.setgeneratorloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("IPSA generator load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update IPSA generator load flow results data tab.")
                return False
        return True

    def getgeneratorloadflowresultsfromnetwork(self):
        """This method retrieves the generator load flow results from the IPSA network."""
        try:
            if not gbl.EngineContainer.m_network:
                gbl.Msg.add_error("No active IPSA network.")
                return False
            self.generator_dictionary = self.network.GetSynMachines()
            if not self.generator_dictionary:
                gbl.Msg.add_warning("No generators found in the network.")
                return False
            self.generatorloadflowresultsdata = []
            for gen_key, gen_obj in self.generator_dictionary.items():
                if gen_obj is None:
                    continue
                # Get busbar reference for the generator
                bus_id = gen_obj.GetSValue(ipsa.IscSynMachine.BusName)
                try:
                    name = gen_key
                    # Use specific getter methods consistent with other components
                    mw = gen_obj.GetRealPowerMW()
                    mvar = gen_obj.GetReactivePowerMVAr()

                    self.generatorloadflowresultsdata.append({
                        "name": name,
                        "bus": bus_id,
                        "MW": mw,
                        "MVAR": mvar
                    })
                except Exception as e:
                    gbl.Msg.add_warning(f"Generator attribute copy failed for '{gen_key}': {e}")

            return self.generatorloadflowresultsdata
        except Exception as e:
            gbl.Msg.add_error(f"Failed to retrieve IPSA generator results: {e}")
            return False

    def setgeneratorloadflowresultstodatatab(self):
        """This method updates the generator load flow results data tab."""
        if not self.generatorloadflowresultsdata:
            gbl.Msg.add_warning("No IPSA generator load flow results data available to update the tab.")
            return False

        for generator in self.generatorloadflowresultsdata:
            gen_obj, _ = gbl.DataModelManager.findgen(generator['bus'], generator["name"])
            if gen_obj is None:
                gbl.Msg.add_warning(f"Generator {generator['name']} not found in the tab.")
                continue

            gen_obj.MWLoadFlow = generator["MW"]
            gen_obj.MVarLoadFlow = generator["MVAR"]
            gen_obj.LoadFlowResults = True
        return True

    #__________________________LOAD LOAD FLOW RESULTS METHODS________________________
    def getandupdateloadsloadflowresults(self):
        """This method retrieves the IPSA load flow results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving IPSA loads load flow results...")
            bOK = self.getloadloadflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error(
                "Failed to retrieve IPSA loads load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating IPSA loads load flow results data tab...")
        bOK = self.setloadflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information(
                    "IPSA loads load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update IPSA loads load flow results data tab.")
                return False
        return True

    def getloadloadflowresultsfromnetwork(self):
        """This method retrieves the load flow results from the IPSA network."""
        try:
            if not gbl.EngineContainer.m_network:
                gbl.Msg.add_error("No active IPSA network.")
                return False
            self.load_dictionary = self.network.GetLoads()
            if not self.load_dictionary:
                gbl.Msg.add_warning("No loads found in the network.")
                return False
            self.loadflowresultsdata = []
            for load_key, load_obj in self.load_dictionary.items():
                if load_obj is None:
                    continue
                # Get busbar reference for the load
                bus_id = load_obj.GetSValue(ipsa.IscLoad.BusName)
                try:
                    name = load_key
                    # Use specific getter methods consistent with other components
                    mw = load_obj.GetRealPowerMW()
                    mvar = load_obj.GetReactivePowerMVAr()

                    self.loadflowresultsdata.append({
                        "name": name,
                        "bus": bus_id,
                        "MW": mw,
                        "MVAR": mvar
                    })
                except Exception as e:
                    gbl.Msg.add_warning(f"Load attribute copy failed for '{load_key}': {e}")

            return self.loadflowresultsdata
        except Exception as e:
            gbl.Msg.add_error(f"Failed to retrieve IPSA load results: {e}")
            return False

    def setloadflowresultstodatatab(self):
        """This method updates the load flow results data tab."""
        if not self.loadflowresultsdata:
            gbl.Msg.add_warning("No IPSA load flow results data available to update the tab.")
            return False

        for load in self.loadflowresultsdata:
            load_obj, _ = gbl.DataModelManager.findload(load['bus'], load["name"])
            if load_obj is None:
                gbl.Msg.add_warning(f"Load {load['name']} not found in the tab.")
                continue

            load_obj.MWLoadFlow = load["MW"]
            load_obj.MVarLoadFlow = load["MVAR"]
            load_obj.LoadFlowResults = True
        return True

    #__________________________TRANSFORMER LOAD FLOW RESULTS METHODS________________________
    def getandupdatetransformerflowresults(self):
        """This method retrieves the IPSA transformer load flow results and updates the data tab."""
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving transformer load flow results")
        bOK = self.gettransformerflowresultsfromnetwork()
        if not bOK:
            gbl.Msg.add_error(
                "Failed to retrieve transformer load flow results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating transformer load flow results data tab...")
        bOK = self.settransformerflowresultstodatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information(
                    "Transformer load flow results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update transformer load flow results data tab.")
                return False
        return True

    def gettransformerflowresultsfromnetwork(self):
        """This method retrieves the transformer load flow results from the IPSA network."""
        try:
            if not gbl.EngineContainer.m_network:
                gbl.Msg.add_error("No active IPSA network.")
                return False
            self.transformer_dictionary = self.network.GetTransformers()
            if not self.transformer_dictionary:
                gbl.Msg.add_error("No transformers found in the network.")
                return False
            for tx_key, tx_obj in self.transformer_dictionary.items():
                if tx_obj is None:
                    continue
                try:
                    name = tx_key
                    bus1 = tx_obj.GetSValue(ipsa.IscTransformer.FromBusName)
                    bus2 = tx_obj.GetSValue(ipsa.IscTransformer.ToBusName)
                    fromMW = tx_obj.GetSendRealPowerMW()
                    fromMvar = tx_obj.GetSendReactivePowerMVAr()
                    toMW = tx_obj.GetReceiveRealPowerMW()
                    toMvar = tx_obj.GetReceiveReactivePowerMVAr()
                    lossMW = tx_obj.GetLossesMW()
                    lossMVAr = tx_obj.GetLossesMVAr()
                    self.transformerloadflowresultsdata.append({
                        "name": name,
                        "bus1": bus1,
                        "bus2": bus2,
                        "lossMW": lossMW,
                        "lossMVAr": lossMVAr,
                        "fromMW": fromMW,
                        "fromMvar": fromMvar,
                        "toMW": toMW,
                        "toMvar": toMvar
                    })
                except Exception as e:
                    gbl.Msg.add_error(
                        f"Failed to retrieve transformer {name} load flow results: {e}")
                return self.transformerloadflowresultsdata
        except Exception as e:
            gbl.Msg.add_error(f"Failed to retrieve transformer load flow results: {e}")
            return False

    def settransformerflowresultstodatatab(self):
        """This method updates the transformer load flow results to the data tab"""
        if not self.transformerloadflowresultsdata:
            gbl.Msg.add_warning(
                "No transformer load flow results data available to update the tab.")
            return False
        for tx in self.transformerloadflowresultsdata:
            branch, _ = gbl.DataModelManager.findbranch(tx["bus1"], tx["bus2"], None, tx["name"])
            if branch is None:
                gbl.Msg.add_warning(f"Branch {tx['name']} not found in the tab.")
                continue
            branch.lossMW = tx["lossMW"]
            branch.lossMVAr = tx["lossMVAr"]
            branch.oBus1.MW = tx["fromMW"]
            branch.oBus2.MW = tx["toMW"]
            branch.oBus1.MVAr = tx["fromMvar"]
            branch.oBus2.MVAr = tx["toMvar"]
            branch.oBus1.LoadFlowResults = branch.oBus2.LoadFlowResults = branch.Results = True
        return True
