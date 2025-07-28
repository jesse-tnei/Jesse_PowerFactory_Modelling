from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineShortCircuitContainer import EngineShortCircuitContainer

class EnginePowerFactoryShortCircuit(EngineShortCircuitContainer):
    def __init__(self):
        super().__init__()
        self.powerfactoryshortcircuitobject = gbl.EngineContainer.m_pFApp.GetFromStudyCase("ComShc")
        self.busbarshortcircuitresultsdata = []

    def runshortcircuitanalysisforallbusbars(self):
        """This method runs the short circuit analysis."""
        if gbl.VERSION_TESTING:
            self.msg.add_information("Running short circuit analysis for all network busbars...")
        if self.powerfactoryshortcircuitobject is None:
            self.msg.adderror("Short circuit object not found in PowerFactory study case.")
            return False
        try:
            self.powerfactoryshortcircuitobject.Execute()
            self.msg.add_information("Short circuit analysis executed successfully.")
            return True
        except Exception as e:
            self.msg.add_error(f"Error running short circuit analysis: {e}")
            return False
        
    # def runshortcircuitanalysisforspecificbusbar(self, busbar):
    #     """This method runs the short circuit analysis for a specific busbar."""
    #     if gbl.VERSION_TESTING:
    #         self.msg.add_information(f"Running short circuit analysis for busbar: {busbar}")
    #     if self.powerfactoryshortcircuitobject is None:
    #         self.msg.adderror("Short circuit object not found in PowerFactory study case.")
    #         return False
    #     try:
    #         # Assuming 'busbar' is a valid busbar object in PowerFactory
    #         self.powerfactoryshortcircuitobject.Execute(busbar)
    #         self.msg.add_information(f"Short circuit analysis for busbar {busbar} executed successfully.")
    #         return True
    #     except Exception as e:
    #         self.msg.add_error(f"Error running short circuit analysis for busbar {busbar}: {e}")
    #         return False
    
    #___________________________BUSBAR SHORT CIRCUIT RESULTS METHODS________________________

    def getandupdateshortcircuitresults(self):
        """This method retrieves the short circuit results and updates the data tab."""
        bOK = True
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Retrieving busbar short circuit results...")
            bOK = self.getbusbarshortcircuitresultsdatafromnetwork()
        if not bOK:
            gbl.Msg.add_error("Failed to retrieve busbar short circuit results data from the network.")
            return False
        if gbl.VERSION_TESTING:
            gbl.Msg.add_information("Updating busbar short circuit results data tab...")
        bOK = self.setbusbarshortcircuitresultsdatatab()
        if gbl.VERSION_TESTING:
            if bOK:
                gbl.Msg.add_information("Busbar short circuit results data tab updated successfully.")
            else:
                gbl.Msg.add_error("Failed to update busbar short circuit results data tab.")
                return False
        return True
    
    def getbusbarshortcircuitresultsdatafromnetwork(self):
        busbars = gbl.EngineContainer.m_pFApp.GetCalcRelevantObjects("*.ElmTerm")
        for bus in busbars:
            name = gbl.DataModelInterfaceContainer.standardize_terminal_id(bus)
            if name not in gbl.DataModelInterfaceContainer.terminal_dictionary:
                continue
            initialshortcircuitcurrent = bus.GetAttribute("m:Ikss")
            initialshortcircuitmva = bus.GetAttribute("m:Skss")
            
            peakshortcircuitcurrent = bus.GetAttribute("m:Ip")
            
            breakingshortcircuitcurrent = bus.GetAttribute("m:Ib")
            breakingshortcircuitmva = bus.GetAttribute("m:Sb")
            
            steadystateshortcircuitcurrent = bus.GetAttribute("m:Ik")
            
            realshortcircuitimpedance = bus.GetAttribute("m:R")
            imaginaryshortcircuitimpedance = bus.GetAttribute("m:X")
            

            self.busbarshortcircuitresultsdata.append({
                "name": name,
                "initialshortcircuitcurrent": initialshortcircuitcurrent,
                "initialshortcircuitmva": initialshortcircuitmva,
                "peakshortcircuitcurrent": peakshortcircuitcurrent,
                "breakingshortcircuitcurrent": breakingshortcircuitcurrent,
                "breakingshortcircuitmva": breakingshortcircuitmva,
                "steadystateshortcircuitcurrent": steadystateshortcircuitcurrent,
                "realshortcircuitimpedance": realshortcircuitimpedance,
                "imaginaryshortcircuitimpedance": imaginaryshortcircuitimpedance
            })
        return self.busbarshortcircuitresultsdata
    
    def setbusbarshortcircuitresultsdatatab(self):
        """This method sets the busbar short circuit results data."""
        if not self.busbarshortcircuitresultsdata:
            gbl.Msg.add_warning("No busbar short circuit results data available to update the tab.")
            return False
        for bus in self.busbarshortcircuitresultsdata:
            busbar, _ = gbl.DataModelManager.findbusbar(bus["name"])
            if busbar is None:
                gbl.Msg.add_warning(f"Busbar {bus['name']} not found in the tab.")
                continue
            busbar.initialshortcircuitcurrent = bus["initialshortcircuitcurrent"]
            busbar.initialshortcircuitmva = bus["initialshortcircuitmva"]
            busbar.peakshortcircuitcurrent = bus["peakshortcircuitcurrent"]
            busbar.breakingshortcircuitcurrent = bus["breakingshortcircuitcurrent"]
            busbar.breakingshortcircuitmva = bus["breakingshortcircuitmva"]
            busbar.steadystateshortcircuitcurrent = bus["steadystateshortcircuitcurrent"]
            busbar.realshortcircuitimpedance = bus["realshortcircuitimpedance"]
            busbar.imaginaryshortcircuitimpedance = bus["imaginaryshortcircuitimpedance"]
            busbar.shortcircuitresults = True
        return True
