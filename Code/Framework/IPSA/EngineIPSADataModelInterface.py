# EngineIPSADataModelInterface.py
# IPSA Data Model Interface: extracts network elements & attributes from the active IPSA network
# and populates your framework's DataModelManager tables, mirroring the PowerFactory DMI pattern.

from Code import GlobalEngineRegistry as gbl
from Code.Framework.BaseTemplates.EngineDataModelInterfaceContainer import EngineDataModelInterfaceContainer
import ipsa

class EngineIPSADataModelInterface(EngineDataModelInterfaceContainer):
    """
    Mirrors EnginePowerFactoryDataModelInterface:
      - Traverse active IPSA network (model under study)
      - Collect busbars, lines (branches), transformers, loads, generators
      - Create rows in DataModelManager using DataFactory
      - Copy across key attributes consistent with your IPSA builder & PowerFactory DMI
    """

    def __init__(self):
        super().__init__()
        self.terminal_dictionary = {}
        self.line_dictionary = {}
        self.transformer_dictionary = {}
        self.load_dictionary = {}

    # ─────────Overall orchestration ────────────────── #
    def passelementsfromnetworktodatamodelmanager(self) -> bool:
        """
        Entry point (same role as PF): gather all supported elements and push into DataModelManager.
        """
        if not gbl.EngineContainer.m_network:
            gbl.Msg.AddError("No active IPSA network.")
            return False
        # Clear/prepare caches
        self.terminal_dictionary.clear()
        self.line_dictionary.clear()
        self.transformer_dictionary.clear()
        self.load_dictionary.clear()

        bOK = True
        bOK = bOK and self.get_busbarsfromnetwork()
        bOK = bOK and self.get_linesfromnetwork()
        bOK = bOK and self.get_transformersfromnetwork()
        bOK = bOK and self.get_loadsfromnetwork()
        bOK = bOK and self.get_generatorsfromnetwork()

        return bOK

    # ───────────────── Busbars ───────────────────────── #
    def get_busbarsfromnetwork(self) -> bool:
        """
        Discover busbars; copy basic attributes into Busbar_TAB.
        Uses IscNetwork.GetBusbarCount() / GetBusbar(i), then per-bus Get*Value calls. 
        """
        try:
            self.terminal_dictionary = gbl.EngineContainer.m_network.GetBusbars()
            if not self.terminal_dictionary:
                gbl.Msg.AddWarning("No busbars discovered.")
                return False
            gbl.Msg.AddRawMessage(f"Total busbars discovered: {len(self.terminal_dictionary)}")

            for terminal_key, terminal_obj in self.terminal_dictionary.items():
                if not terminal_key or not terminal_obj:
                    continue
                terminal_id = terminal_key               # Cache for cross-reference 
                busbar = gbl.DataFactory.createbusbar(terminal_id)
                if busbar is None:
                    gbl.Msg.AddWarning(f"Failed to create DataModel row for busbar '{terminal_id}'.")
                    continue
                # Attributes aligned to your model & IPSA enums you set during build
                if not self.getbusbarvaluesfromnetwork(busbar):
                    gbl.Msg.AddWarning(f"Failed to retrieve values for busbar '{terminal_id}'.")
                    continue
                if not gbl.DataModelManager.addbusbartotab(busbar):
                    gbl.Msg.AddWarning(f"Failed to add busbar '{terminal_id}' to DataModel.")
                    continue
            gbl.Msg.AddRawMessage(f"Total busbars added to DataModel: {len(gbl.DataModelManager.Busbar_TAB)}")
            return True

        except Exception as e:
            gbl.Msg.AddError(f"Failed to retrieve busbars from IPSA: {e}")
            return False
    def getbusbarvaluesfromnetwork(self, busbar):
        """Retrieves busbar values from the PowerFactory network."""
        bOK = True
        if bOK:
            terminal = self.terminal_dictionary.get(busbar.BusID)
            if terminal:
                name = busbar.BusID
                VMagkV = terminal.GetDValue(ipsa.IscBusbar.NomVoltkV)
                #TODO: ON = terminal.GetDValue(ipsa.IscBusbar.On). Compare with PF

            else:
                name = VMagkV = ON = None
            if name is None or VMagkV is None:
                gbl.Msg.AddError(f"Failed to retrieve values for busbar {busbar.BusID}.")
                bOK = False
            else:
                busbar.name = name
                busbar.kV = VMagkV
        return bOK
    # ──────────────────── Lines / Branches ────────────────────── #
    def get_linesfromnetwork(self) -> bool:
        """
        Discover AC lines/cables (IscBranch) and copy attributes to Branch_TAB.
        Uses IscNetwork.GetBranchCount() / GetBranch(i), then from/to bus via GetFromBusbar()/GetToBusbar().
        """
        try:
            self.line_dictionary = gbl.EngineContainer.m_network.GetBranches()
            if not self.line_dictionary:
                gbl.Msg.AddWarning("No lines discovered.")
                return True
            gbl.Msg.AddRawMessage(f"Total lines discovered: {len(self.line_dictionary)}")
            for br_key, br_obj in self.line_dictionary.items():
                if not br_key or not br_obj:
                    continue
                line_id = br_key
                terminal1 = br_obj.GetSValue(ipsa.IscBranch.FromBusName)
                terminal2 = br_obj.GetSValue(ipsa.IscBranch.ToBusName)
                if terminal1 and terminal2:
                    if terminal1 not in self.terminal_dictionary or terminal2 not in self.terminal_dictionary:
                        gbl.Msg.AddWarning(f"Branch '{line_id}': missing end bus references.")
                        continue
                    line_datamodel = gbl.DataFactory.createbranch(terminal1, terminal2, 0, line_id)
                    if line_datamodel is None:
                        gbl.Msg.AddWarning(f"Failed to create DataModel row for branch '{line_id}'.")
                        continue
                    if not self.getlinevaluesfromnetwork(line_datamodel):
                        gbl.Msg.AddWarning(f"Failed to retrieve values for branch '{line_id}'.")
                        continue
                    gbl.DataModelManager.Branch_TAB.append(line_datamodel)
            gbl.Msg.AddRawMessage(f"Total lines added to DataModel: {len(gbl.DataModelManager.Branch_TAB)}")
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to retrieve lines from IPSA: {e}")
            return False
    def getlinevaluesfromnetwork(self, line_datamodel):
        """Retrieves branch values from the PowerFactory network."""
        bOK = True
        if bOK:
            br = self.line_dictionary.get(line_datamodel.BranchID)
            if br:
                try:
                    line_datamodel.Type = br.GetIValue(ipsa.IscBranch.Type)
                    line_datamodel.Status = br.GetIValue(ipsa.IscBranch.Status)
                    line_datamodel.ResistancePU  = br.GetDValue(ipsa.IscBranch.ResistancePU)
                    line_datamodel.ReactancePU   = br.GetDValue(ipsa.IscBranch.ReactancePU)
                    line_datamodel.SusceptancePU = br.GetDValue(ipsa.IscBranch.SusceptancePU)
                    line_datamodel.ZSResistancePU = br.GetDValue(ipsa.IscBranch.ZSResistancePU)
                    line_datamodel.ZSReactancePU  = br.GetDValue(ipsa.IscBranch.ZSReactancePU)
                    line_datamodel.LengthKm = br.GetDValue(ipsa.IscBranch.LengthKm)
                    line_datamodel.Comment  = br.GetSValue(ipsa.IscBranch.Comment)
                except Exception as e:
                    gbl.Msg.AddWarning(f"Branch attribute copy failed for '{line_datamodel.BranchID}': {e}")
        return True
    # ────────────────── Transformers (2-winding) ───────────────────────────────────────────── #
    def get_transformersfromnetwork(self) -> bool:
        """
        Discover 2-winding transformers (IscTransformer) and copy attributes to Tx_TAB.
        If your IPSA version exposes GetTransformerCount/GetTransformer(i), use that; otherwise,
        you can detect by enumeration helpers if available.
        """
        try:
            self.transformer_dictionary = gbl.EngineContainer.m_network.GetTransformers()
            if not self.transformer_dictionary:
                gbl.Msg.AddWarning("No 2-winding transformers discovered.")
                return False
            gbl.Msg.AddRawMessage(f"Total 2-winding transformers discovered: {len(self.transformer_dictionary)}")
            initialbranchtablength = len(gbl.DataModelManager.Branch_TAB)
            for tr_key, tr_obj in self.transformer_dictionary.items():
                if not tr_key or not tr_obj:
                    continue
                transformer_id = tr_key
                terminal1 = tr_obj.GetSValue(ipsa.IscTransformer.FromBusName)
                terminal2 = tr_obj.GetSValue(ipsa.IscTransformer.ToBusName)
                if terminal1 and terminal2:
                    if terminal1 not in self.terminal_dictionary or terminal2 not in self.terminal_dictionary:
                        gbl.Msg.AddWarning(f"Transformer '{transformer_id}': missing end bus references.")
                        continue
                    transformer_datamodel = gbl.DataFactory.createbranch(terminal1, terminal2, 0, transformer_id)
                    if transformer_datamodel is None:
                        gbl.Msg.AddWarning(f"Failed to create DataModel row for transformer '{transformer_id}'.")
                        continue
                    if not self.gettransformervaluesfromnetwork(transformer_datamodel):
                        gbl.Msg.AddWarning(f"Failed to retrieve values for transformer '{transformer_id}'.")
                        continue
                    transformer_datamodel.IsTransformer = True
                    gbl.DataModelManager.Branch_TAB.append(transformer_datamodel)
            gbl.Msg.AddRawMessage(f"Total transformers added to DataModel: {len(gbl.DataModelManager.Branch_TAB) - initialbranchtablength}")
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to retrieve transformers from IPSA: {e}")
            return False
    def gettransformervaluesfromnetwork(self, transformer_datamodel):
        """Retrieves transformer values from the PowerFactory network."""
        bOK = True
        if bOK:
            tx = self.transformer_dictionary.get(transformer_datamodel.BranchID)
            if tx:
                try:
                    transformer_datamodel.Type   = tx.GetIValue(ipsa.IscTransformer.Type)
                    transformer_datamodel.TapStartPC     = tx.GetDValue(ipsa.IscTransformer.TapStartPC)
                    transformer_datamodel.TapNominalPC   = tx.GetDValue(ipsa.IscTransformer.TapNominalPC)
                    transformer_datamodel.TapStepPC      = tx.GetDValue(ipsa.IscTransformer.TapStepPC)
                    transformer_datamodel.MinTapPC       = tx.GetDValue(ipsa.IscTransformer.MinTapPC)
                    transformer_datamodel.MaxTapPC       = tx.GetDValue(ipsa.IscTransformer.MaxTapPC)
                    transformer_datamodel.LockTap        = tx.GetBValue(ipsa.IscTransformer.LockTap)
                    transformer_datamodel.SpecVPU        = tx.GetDValue(ipsa.IscTransformer.SpecVPU)
                    transformer_datamodel.RBWidthPC      = tx.GetDValue(ipsa.IscTransformer.RBWidthPC)
                    transformer_datamodel.RatingMVA      = tx.GetDValue(ipsa.IscTransformer.RatingMVA)
                    transformer_datamodel.Comment        = tx.GetSValue(ipsa.IscTransformer.Comment)
                    try:
                        transformer_datamodel.PhShiftDeg     = tx.GetDValue(ipsa.IscTransformer.PhShiftDeg)
                        transformer_datamodel.MinPhShiftDeg  = tx.GetDValue(ipsa.IscTransformer.MinPhShiftDeg)
                        transformer_datamodel.MaxPhShiftDeg  = tx.GetDValue(ipsa.IscTransformer.MaxPhShiftDeg)
                        transformer_datamodel.PhShiftStepDeg = tx.GetDValue(ipsa.IscTransformer.PhShiftStepDeg)
                        transformer_datamodel.SpecPowerMW    = tx.GetDValue(ipsa.IscTransformer.SpecPowerMW)
                        transformer_datamodel.SpecPowerAtSend= tx.GetBValue(ipsa.IscTransformer.SpecPowerAtSend)
                    except Exception:
                        pass
                except Exception as e:
                    gbl.Msg.AddWarning(f"Transformer attribute copy failed for '{transformer_datamodel.BranchID}': {e}")
        return True


    # ────────────────── Loads ───────────────────────────────────────────── #
    def get_loadsfromnetwork(self) -> bool:
        """
        Discover loads (IscLoad) and copy attributes to Load_TAB.
        Pattern mirrors your builder’s Set*Value usage. 
        """
        try:
            self.load_dictionary = gbl.EngineContainer.m_network.GetLoads()
            if not self.load_dictionary:
                gbl.Msg.AddWarning("No loads discovered.")
                return False
            gbl.Msg.AddRawMessage(f"Total loads discovered: {len(self.load_dictionary)}")
            for ld_key, ld_obj in self.load_dictionary.items():
                if not ld_key or not ld_obj:
                    continue
                load_id = ld_key
                terminal = ld_obj.GetSValue(ipsa.IscLoad.BusName)
                if terminal:
                    if terminal not in self.terminal_dictionary:
                        gbl.Msg.AddWarning(f"Load '{load_id}': missing bus reference.")
                        continue
                    load_datamodel = gbl.DataFactory.createload(terminal, load_id)
                    if load_datamodel is None:
                        gbl.Msg.AddWarning(f"Failed to create DataModel row for load '{load_id}'.")
                        continue
                    if not self.getloadvaluesfromnetwork(load_datamodel):
                        gbl.Msg.AddWarning(f"Failed to retrieve values for load '{load_id}'.")
                        continue
                    gbl.DataModelManager.addloadtotab(load_datamodel)
            gbl.Msg.AddRawMessage(f"Total loads added to DataModel: {len(gbl.DataModelManager.Load_TAB)}")
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to retrieve loads from IPSA: {e}")
            return False
    def getloadvaluesfromnetwork(self, load_datamodel):
        """Retrieves load values from the PowerFactory network."""
        bOK = True
        if bOK:
            ld = self.load_dictionary.get(load_datamodel.LoadID)
            if ld:
                try:
                    load_datamodel.LoadMW   = ld.GetDValue(ipsa.IscLoad.RealMW)
                    load_datamodel.LoadMVAR = ld.GetDValue(ipsa.IscLoad.ReactiveMVAr)
                except Exception as e:
                    gbl.Msg.AddWarning(f"Load attribute copy failed for '{load_datamodel.LoadID}': {e}")
        return True


    # ──────────────────── Generators ───────────────────────────────────────────── #
    def get_generatorsfromnetwork(self) -> bool:
        """
        Discover synchronous generators (IscSynMachine) and copy attributes to Gen_TAB.
        Mirrors your builder’s Set*Value calls (GenMW/MVAr/ratings/voltage setpoint, etc.). 
        """
        try:
            self.generator_dictionary = gbl.EngineContainer.m_network.GetSynMachines()
            if not self.generator_dictionary:
                gbl.Msg.AddWarning("No generators discovered.")
                return False
            gbl.Msg.AddRawMessage(f"Total generators discovered: {len(self.generator_dictionary)}")
            for gen_key, gen_obj in self.generator_dictionary.items():
                if not gen_key or not gen_obj:
                    continue
                gen_id = gen_key
                terminal = gen_obj.GetSValue(ipsa.IscSynMachine.BusName)
                if terminal:
                    if terminal not in self.terminal_dictionary:
                        gbl.Msg.AddWarning(f"Generator '{gen_id}': missing bus reference.")
                        continue
                    gen_datamodel = gbl.DataFactory.creategenerator(terminal, gen_id)
                    if gen_datamodel is None:
                        gbl.Msg.AddWarning(f"Failed to create DataModel row for generator '{gen_id}'.")
                        continue
                    if not self.getgeneratorvaluesfromnetwork(gen_datamodel):
                        gbl.Msg.AddWarning(f"Failed to retrieve values for generator '{gen_id}'.")
                        continue
                    gbl.DataModelManager.addgentotab(gen_datamodel)
            gbl.Msg.AddRawMessage(f"Total generators added to DataModel: {len(gbl.DataModelManager.Gen_TAB)}")
            return True
        except Exception as e:
            gbl.Msg.AddError(f"Failed to retrieve generators from IPSA: {e}")
            return False
    def getgeneratorvaluesfromnetwork(self, gen_datamodel):
        """Retrieves generator values from the PowerFactory network."""
        bOK = True
        if bOK:
            gen = self.generator_dictionary.get(gen_datamodel.GenID)
            if gen:
                try:
                    gen_datamodel.GenMW   = gen.GetDValue(ipsa.IscSynMachine.GenMW)
                    gen_datamodel.GenMVAR = gen.GetDValue(ipsa.IscSynMachine.GenMVAr)
                    return True
                except Exception as e:
                    gbl.Msg.AddWarning(f"Generator attribute copy failed for '{gen_datamodel.GenID}': {e}")
                    return False