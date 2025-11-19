import pandas as pd
from Code import GlobalEngineRegistry as gbl
from Code.DataSources.BaseTemplates.DataSourceDataModelInterface import DataSourceDataModelInterface
class ETYSDataModelInterface(DataSourceDataModelInterface):

    def load_from_source_to_datamodel(self, etys_standardized_data):
        """Load ETYS data into framework DataModel"""
        gbl.Msg.AddRawMessage("Loading ETYS data into DataModel...")
        bOK = True
        # Process nodes first (busbars)
        if bOK and 'nodes' in etys_standardized_data:
            bOK = self._load_nodes_to_datamodel(etys_standardized_data['nodes'])
        # Process branches (lines, cables, transformers)
        if bOK:
            branch_sheets = ['overhead_lines', 'cables', 'composite_lines', 'zero_length_lines',
                            'transformers', 'quadboosters', 'series_compensation', 'sssc_devices',
                            'series_reactors', 'series_capacitors']
            for sheet_name in branch_sheets:
                if sheet_name in etys_standardized_data:
                    bOK = self._load_branches_to_datamodel(etys_standardized_data[sheet_name], sheet_name)
                    if not bOK:
                        break
        # Process loads
        if bOK and 'loads' in etys_standardized_data:
            bOK = self._load_loads_to_datamodel(etys_standardized_data['loads'])
        # Process shunt elements (as zero-impedance branches or special loads)
        if bOK:
            shunt_sheets = ['shunt_reactors', 'switched_capacitors', 'svc_devices',  'statcom_devices']
            for sheet_name in shunt_sheets:
                if sheet_name in etys_standardized_data:
                    bOK = self._load_shunt_elements_to_datamodel(etys_standardized_data[sheet_name], sheet_name)
                    if not bOK:
                        break
        # Process generators
        if bOK:
            # Update generator sheets
            gen_sheets = ['tec_generators', 'interconnectors', 'sync_compensators']
            for sheet_name in gen_sheets:
                if sheet_name in etys_standardized_data:
                    bOK = self._load_generators_to_datamodel(etys_standardized_data[sheet_name], sheet_name)
                    if not bOK:
                        break
        # Process HVDC links
        if bOK and 'hvdc_links' in etys_standardized_data:
            bOK = self._load_hvdc_links_to_datamodel(etys_standardized_data['hvdc_links'])
        if bOK:
            gbl.Msg.AddRawMessage("ETYS data successfully loaded into DataModel")
        else:
            gbl.Msg.AddError("Failed to load ETYS data into DataModel")
        return bOK

    def _load_nodes_to_datamodel(self, nodes_df):
        """Load nodes (busbars) into DataModel"""
        if nodes_df.empty:
            return True
        for _, row in nodes_df.iterrows():
            node_id = str(row['node_id']).strip() if 'node_id' in row else str(row['Node']).strip()
            if not node_id or node_id == 'nan':
                continue
            # Create busbar using DataFactory
            busbar = gbl.DataFactory.createbusbar(node_id)
            if busbar is None:
                gbl.Msg.AddError(f"Failed to create busbar for node {node_id}")
                continue
            # Set busbar properties from ETYS data
            busbar.name = str(row.get('Site Name', node_id))
            busbar.kV = float(row['voltage_kv']) if 'voltage_kv' in row and pd.notna(row['voltage_kv']) else float(row.get('Voltage (Derived)', 0))
            busbar.Disconnected = False  # Default to connected
            # Add to DataModel
            if not gbl.DataModelManager.addbusbartotab(busbar):
                gbl.Msg.AddError(f"Failed to add busbar {node_id} to DataModel")
                return False
        gbl.Msg.AddRawMessage(f"Loaded {len(nodes_df)} nodes into DataModel")
        return True

    def _load_branches_to_datamodel(self, branches_df, sheet_type):
        """Load branches (lines/transformers) into DataModel"""
        if branches_df.empty:
            return True
        for _, row in branches_df.iterrows():
            node1 = str(row['node_1']).strip() if 'node_1' in row else str(row.get('Node 1', '')).strip()
            node2 = str(row['node_2']).strip() if 'node_2' in row else str(row.get('Node 2', '')).strip()
            if not node1 or not node2 or node1 == 'nan' or node2 == 'nan':
                continue
            branch_id = f"{node1}_{node2}_{sheet_type}"
            # Create branch using DataFactory
            branch = gbl.DataFactory.createbranch(node1, node2, 0, branch_id)
            if branch is None:
                gbl.Msg.AddError(f"Failed to create branch {branch_id}")
                continue
            # Set branch properties
            branch.name = str(row.get('Name', branch_id))
            branch.ON = True  # Default to energized
            # Set transformer flag for transformer sheets
            if sheet_type in ['transformers', 'quadboosters']:
                branch.IsTransformer = True
            # Add to DataModel
            gbl.DataModelManager.Branch_TAB.append(branch)
        gbl.Msg.AddRawMessage(f"Loaded {len(branches_df)} {sheet_type} into DataModel")
        return True

    def _load_loads_to_datamodel(self, loads_df):
        """Load loads into DataModel"""
        if loads_df.empty:
            return True
        for _, row in loads_df.iterrows():
            node_id = str(row['node_id']).strip() if 'node_id' in row else str(row.get('ETYS_Node', '')).strip()
            if not node_id or node_id == 'nan':
                continue
            # Generate load ID
            load_id = f"Load_{node_id}_{len(gbl.DataModelManager.Load_TAB)}"
            # Create load using DataFactory
            load_item = gbl.DataFactory.createload(node_id, load_id)
            if load_item is None:
                gbl.Msg.AddError(f"Failed to create load {load_id}")
                continue
            # Set load properties
            load_item.name = str(row.get('Name', load_id))
            load_item.MW = float(row.get('MW', 0)) if 'MW' in row and pd.notna(row['MW']) else 0.0
            load_item.MVar = float(row.get('MVar', 0)) if 'MVar' in row and pd.notna(row['MVar']) else 0.0
            load_item.ON = True
            # Add to DataModel
            if not gbl.DataModelManager.addloadtotab(load_item):
                gbl.Msg.AddError(f"Failed to add load {load_id} to DataModel")
                return False
        gbl.Msg.AddRawMessage(f"Loaded {len(loads_df)} loads into DataModel")
        return True

    def _load_generators_to_datamodel(self, generators_df, sheet_type):
        """Load generators into DataModel"""
        if generators_df.empty:
            return True
        for _, row in generators_df.iterrows():
            node_id = str(row['node_id']).strip() if 'node_id' in row else str(row.get('ETYS_Node', '')).strip()
            if not node_id or node_id == 'nan':
                continue
            # Generate generator ID
            gen_id = f"Gen_{node_id}_{sheet_type}_{len(gbl.DataModelManager.Gen_TAB)}"
            # Create generator using DataFactory
            gen_item = gbl.DataFactory.creategenerator(node_id, gen_id)
            if gen_item is None:
                gbl.Msg.AddError(f"Failed to create generator {gen_id}")
                continue
            # Set generator properties based on sheet type
            gen_item.name = str(row.get('Plant Name', gen_id))
            gen_item.ON = True
            if sheet_type == 'tec_generators':
                gen_item.MW = float(row.get('MW_Capacity', 0)) if 'MW_Capacity' in row and pd.notna(row['MW_Capacity']) else 0.0
                gen_item.MWCapacity = gen_item.MW
            elif sheet_type == 'interconnectors':
                gen_item.MW = float(row.get('MW_Import_Capacity', 0)) if 'MW_Import_Capacity' in row and pd.notna(row['MW_Import_Capacity']) else 0.0
                gen_item.MWCapacity = gen_item.MW
            # Add to DataModel
            if not gbl.DataModelManager.addgentotab(gen_item):
                gbl.Msg.AddError(f"Failed to add generator {gen_id} to DataModel")
                return False
        gbl.Msg.AddRawMessage(f"Loaded {len(generators_df)} {sheet_type} into DataModel")
        return True
    def _load_shunt_elements_to_datamodel(self, shunt_df, sheet_type):
        """Load shunt elements (reactors, capacitors, SVC, STATCOM) into DataModel"""
        if shunt_df.empty:
            return True
        for _, row in shunt_df.iterrows():
            node_id = str(row.get('Node', '')).strip()
            if not node_id or node_id == 'nan':
                continue
            if sheet_type in ['shunt_reactors', 'switched_capacitors']:
                # Load reactive elements as special loads with reactive power only
                load_id = f"Shunt_{sheet_type}_{node_id}_{len(gbl.DataModelManager.Load_TAB)}"
                shunt_item = gbl.DataFactory.createload(node_id, load_id)
                if shunt_item is None:
                    gbl.Msg.AddError(f"Failed to create shunt element {load_id}")
                    continue
                shunt_item.name = str(row.get('Name', load_id))
                shunt_item.MW = 0.0  # Shunt elements don't consume real power
                shunt_item.MVar = float(row.get('MVar', 0)) if 'MVar' in row and pd.notna(row['MVar']) else 0.0
                shunt_item.ON = True
                if not gbl.DataModelManager.addloadtotab(shunt_item):
                    gbl.Msg.AddError(f"Failed to add shunt element {load_id} to DataModel")
                    return False
            elif sheet_type in ['svc_devices', 'statcom_devices']:
                # Load dynamic compensation as generators with reactive capability
                gen_id = f"DynComp_{sheet_type}_{node_id}_{len(gbl.DataModelManager.Gen_TAB)}"
                comp_item = gbl.DataFactory.creategenerator(node_id, gen_id)
                if comp_item is None:
                    gbl.Msg.AddError(f"Failed to create dynamic compensation {gen_id}")
                    continue
                comp_item.name = str(row.get('Name', gen_id))
                comp_item.MW = 0.0  # Dynamic compensation doesn't generate real power
                comp_item.MVar = 0.0  # Reactive power controlled dynamically
                comp_item.ON = True
                if not gbl.DataModelManager.addgentotab(comp_item):
                    gbl.Msg.AddError(f"Failed to add dynamic compensation {gen_id} to DataModel")
                    return False
        gbl.Msg.AddRawMessage(f"Loaded {len(shunt_df)} {sheet_type} into DataModel")
        return True
    def _load_hvdc_links_to_datamodel(self, hvdc_df):
        """Load HVDC links into DataModel as special branches"""
        if hvdc_df.empty:
            return True
        for _, row in hvdc_df.iterrows():
            node1 = str(row.get('node_1', '')).strip() if 'node_1' in row else str(row.get('Node 1', '')).strip()
            node2 = str(row.get('node_2', '')).strip() if 'node_2' in row else str(row.get('Node 2', '')).strip()
            if not node1 or not node2 or node1 == 'nan' or node2 == 'nan':
                continue
            # Create HVDC link as special branch
            hvdc_id = f"HVDC_{node1}_{node2}"
            hvdc_branch = gbl.DataFactory.createbranch(node1, node2, 0, hvdc_id)
            if hvdc_branch is None:
                gbl.Msg.AddError(f"Failed to create HVDC link {hvdc_id}")
                continue
            # Set HVDC properties
            hvdc_branch.name = str(row.get('Name', hvdc_id))
            hvdc_branch.ON = True
            hvdc_branch.IsHVDC = True  # Special flag for HVDC (if your Branch class supports it)
            # Add to DataModel
            gbl.DataModelManager.Branch_TAB.append(hvdc_branch)
        gbl.Msg.AddRawMessage(f"Loaded {len(hvdc_df)} HVDC links into DataModel")
        return True

    def export_from_datamodel_to_source(self, format_type='excel'):
        """Export current DataModel back to ETYS format"""
        print("Exporting DataModel to ETYS format...")
        # TODO: Implement actual export logic
        return {}
    def orchestrate_source_data_loading(self, standardised_etys_data, load_strategy="datamodel"):
        if load_strategy == "datamodel":
            return self.load_from_source_to_datamodel(standardised_etys_data)
        elif load_strategy == "direct" and gbl.EngineContainer.engine_type == "PowerFactory":
            return self.load_from_source_to_engine(standardised_etys_data, "PowerFactory")
        elif load_strategy == "direct" and gbl.EngineContainer.engine_type == "ipsa":
            return self.load_from_source_to_engine(standardised_etys_data, "ipsa")
        else:
            raise ValueError(f"Unsupported load strategy: {load_strategy}")
    def load_from_source_to_engine(self, standardised_etys_data, engine_type):
        """Load ETYS data directly to specified engine, bypassing DataModel"""
        if engine_type == "PowerFactory":
            return self._load_to_powerfactory_engine(standardised_etys_data)
        elif engine_type == "ipsa":
            return self._load_to_ipsa_engine(standardised_etys_data)
        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")
    def _load_to_powerfactory_engine(self, standardised_etys_data):
        if not gbl.EngineContainer or not gbl.EngineContainer.m_pFApp:
            raise RuntimeError("PowerFactory engine not initialized")
        # TODO: Implement PowerFactory direct loading
        pass

    def _load_to_ipsa_engine(self, standardised_etys_data):
        """Load ETYS data directly to IPSA engine"""
        # TODO: Implement IPSA direct loading
        pass
