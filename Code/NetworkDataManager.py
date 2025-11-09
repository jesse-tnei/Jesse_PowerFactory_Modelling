"""
NetworkDataManager - Orchestrates data sources for network modeling
Manages multiple data sources and provides standardized data access for the framework.
Part of the Jesse PowerFactory Modelling Framework.
"""

from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

from Code.DataSources.ETYS.ETYSDataReader import ETYSDataReader
from Code.DataSources.ETYS.ETYSDataValidator import ETYSDataValidator
from Code.DataSources.ValidationResult import ValidationResult


class NetworkDataManager:
    """Orchestrates multiple data sources for network modeling"""

    def __init__(self):
        self.data_sources = {'etys': (ETYSDataReader(), ETYSDataValidator())}

    def load_and_validate_data(self, source_type: str, **kwargs) -> ValidationResult:
        """
        Load and validate data from specified source
        Args:
            source_type (str): Type of data source ('etys', etc.)
            **kwargs: Arguments passed to the data reader
        Returns:
            ValidationResult: Validation results with loaded data
        Raises:
            ValueError: If source type is not supported
        """
        if source_type not in self.data_sources:
            raise ValueError(f"Unsupported data source type: {source_type}")
        reader, validator = self.data_sources[source_type]
        raw_data = reader.load_data(**kwargs)
        return validator.validate(raw_data)

    def get_standardized_data(self, source_type: str, strict_validation: bool = False, export_to_excel: bool = False, output_file_path: Optional[str] = None, **kwargs) -> Dict[str, pd.DataFrame]:
        validation_result = self.load_and_validate_data(source_type, **kwargs)
        # Check if validation passed
        is_valid = validation_result.is_valid() if callable(validation_result.is_valid) else validation_result.is_valid
        if not is_valid:
            error_msg = f"Data validation failed: {validation_result.detailed_report()}"
            if strict_validation:
                raise ValueError(error_msg)
            else:
                print(f"{error_msg}")
                print("Continuing with available data (strict_validation=False)...")
        # Check what data we actually have
        # Check what data we actually have
        if validation_result.cleaned_data is None:
            print("No cleaned_data available")
            # Try to get raw data instead as fallback
            if hasattr(validation_result, 'raw_data') and validation_result.raw_data is not None:
                print("Falling back to raw_data")
                standardized_data = self._standardize_to_common_format(validation_result.raw_data, source_type)
            else:
                raise ValueError("No data available to process - both cleaned_data and raw_data are None")
        else:
            # Create standardized data from cleaned data
            standardized_data = self._standardize_to_common_format(validation_result.cleaned_data, source_type)
        # Handle Excel export if requested
        if export_to_excel:
            if output_file_path is None:
                # Generate default filename with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file_path = f"{source_type.upper()}_Standardized_Data_{timestamp}.xlsx"
            # Export using the existing method
            self._export_to_excel_internal_use(standardized_data, output_file_path)
        return standardized_data
    def _export_to_excel_internal_use(self, standardized_data: Dict[str, pd.DataFrame], output_file_path: str):
        """
        Internal method to export standardized data to Excel
        Args:
            standardized_data (Dict[str, pd.DataFrame]): Already standardized data
            output_file_path (str): Path where Excel file should be saved
        """
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            for sheet_name, df in standardized_data.items():
                # Clean sheet name for Excel (max 31 chars, no special chars)
                clean_sheet_name = sheet_name.replace('/', '_').replace('\\', '_')[:31]
                df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
        print(f"Standardized data exported to: {output_file_path}")
        print(f"Created {len(standardized_data)} tabs: {list(standardized_data.keys())}")
    def export_standardized_data_to_excel(self, source_type: str, output_file_path: str, **kwargs):
        """
        Export standardized data to Excel file with separate tabs for each element type
        Args:
            source_type (str): Type of data source ('etys', etc.)
            output_file_path (str): Path where Excel file should be saved
            **kwargs: Arguments passed to the data reader
        """
        # Get the standardized data
        standardized_data = self.get_standardized_data(source_type, **kwargs)
        # Create Excel writer
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            for sheet_name, df in standardized_data.items():
                # Clean sheet name for Excel (max 31 chars, no special chars)
                clean_sheet_name = sheet_name.replace('/', '_').replace('\\', '_')[:31]
                df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
        print(f"Standardized data exported to: {output_file_path}")
        print(f"Created {len(standardized_data)} tabs: {list(standardized_data.keys())}")

    def _standardize_to_common_format(self, data: Optional[Dict[str, pd.DataFrame]],
                                      source_type: str) -> Dict[str, pd.DataFrame]:
        """
        Standardize data to common format expected by DataModel and Engines
        Args:
            data (Optional[Dict[str, pd.DataFrame]]): Source-specific data
            source_type (str): Source type for source-specific handling
        Returns:
            Dict[str, pd.DataFrame]: Standardized data format
        """
        if data is None:
            return {}
        if source_type == 'etys':
            return self._standardize_etys_data(data)
        else:
            # Future: Add handling for other source types (neso, geographic, etc.)
            return data

    def _standardize_etys_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Standardize ETYS data format
        Args:
            data (Dict[str, pd.DataFrame]): ETYS-specific data

        Returns:
            Dict[str, pd.DataFrame]: Standardized data format
        """
        standardized_data = {}
        # Standard sheet name mapping for ETYS
        etys_sheet_mapping = {
            # Core network structure
            'Nodes': 'nodes',
            # Branch elements (lines and cables)
            'OHL': 'overhead_lines',
            'Cable': 'cables',
            'Composite': 'composite_lines',
            'Zero Length': 'zero_length_lines',
            # Transformer elements
            'Transformer': 'transformers',
            'Quadbooster': 'quadboosters',
            'Series Compensation': 'series_compensation',
            'SSSC': 'sssc_devices',
            # Shunt compensation
            'Shunt Reactor': 'shunt_reactors',
            'Mechanically Switched Capacitor': 'switched_capacitors',
            # Dynamic compensation
            'SVC': 'svc_devices',
            'STATCOM': 'statcom_devices',
            'Sync Comp': 'sync_compensators',
            # Series devices
            'Series Reactor': 'series_reactors',
            'Series Capacitor': 'series_capacitors',
            # Loads and generation
            'Demand Data': 'loads',
            'TEC Register': 'tec_generators',
            'IC Register': 'interconnectors',
            # HVDC
            'Intra_HVDC': 'hvdc_links'
        }

        # Apply standardization
        for original_sheet, df in data.items():
            if original_sheet in etys_sheet_mapping:
                standard_name = etys_sheet_mapping[original_sheet]
                # Apply any data transformations needed
                standardized_data[standard_name] = self._transform_etys_sheet_data(
                    df, original_sheet, standard_name)
            else:
                # Keep original name if no mapping exists
                standardized_data[original_sheet] = df
        return standardized_data

    def _transform_etys_sheet_data(self, df: pd.DataFrame, original_sheet: str,
                                   standard_name: str) -> pd.DataFrame:
        """
        Apply transformations to individual ETYS sheets
        Args:
            df (pd.DataFrame): Original sheet data
            original_sheet (str): Original ETYS sheet name
            standard_name (str): Standardized sheet name
        Returns:
            pd.DataFrame: Transformed data
        """
        # Make a copy to avoid modifying original data
        transformed_df = df.copy()
        # Apply sheet-specific transformations
        if standard_name == 'nodes':
            # Ensure consistent node naming
            if 'Node' in transformed_df.columns:
                transformed_df['node_id'] = transformed_df['Node'].astype(str).str.strip()
            # Standardize voltage column
            if 'Voltage (Derived)' in transformed_df.columns:
                transformed_df['voltage_kv'] = pd.to_numeric(transformed_df['Voltage (Derived)'],
                                                             errors='coerce')
        elif standard_name in ['overhead_lines', 'cables', 'composite_lines', 'zero_length_lines']:
            # Standardize node references
            for col in ['Node 1', 'Node 2']:
                if col in transformed_df.columns:
                    new_col = col.lower().replace(' ', '_')
                    transformed_df[new_col] = transformed_df[col].astype(str).str.strip()
        elif standard_name in ['transformers', 'quadboosters']:
            # Standardize transformer node references
            for col in ['Node 1', 'Node 2']:
                if col in transformed_df.columns:
                    new_col = col.lower().replace(' ', '_')
                    transformed_df[new_col] = transformed_df[col].astype(str).str.strip()
        elif standard_name == 'loads':
            # Standardize load node references
            if 'ETYS_Node' in transformed_df.columns:
                transformed_df['node_id'] = transformed_df['ETYS_Node'].astype(str).str.strip()
        elif standard_name in ['tec_generators', 'interconnectors']:
            # Standardize generator node references
            if 'ETYS_Node' in transformed_df.columns:
                transformed_df['node_id'] = transformed_df['ETYS_Node'].astype(str).str.strip()
        # Add metadata columns
        transformed_df['source_sheet'] = original_sheet
        transformed_df['data_source'] = 'etys'
        return transformed_df
    def load_etys_data_to_framework(self, source_type: str = 'etys', load_strategy: str = "datamodel", **kwargs) -> bool:
        """
        Complete ETYS data loading pipeline: Excel → Standardized → DataModel/Engine
        Args:
            source_type (str): Data source type (default 'etys')
            load_strategy (str): 'datamodel' or 'direct' loading strategy
            **kwargs: Arguments passed to data reader (e.g., file_path)
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            # Step 1: Get standardized data (existing functionality)
            standardized_data = self.get_standardized_data(source_type, **kwargs)
            # Step 2: Load into framework using ETYSDataModelInterface (NEW)
            from Code import GlobalEngineRegistry as gbl
            if not hasattr(gbl, 'DataSourceInterfaceContainer') or gbl.DataSourceInterfaceContainer is None:
                raise RuntimeError("ETYSDataModelInterface not initialized in framework")
            # Step 3: Use orchestration to load data
            success = gbl.DataSourceInterfaceContainer.orchestrate_source_data_loading(
                standardized_data,
                load_strategy=load_strategy
            )
            if success:
                return True
            else:
                print(f"Failed to load ETYS data using {load_strategy} strategy")
                return False
        except Exception as e:
            print(f"ETYS data loading failed: {e}")
            return False

    def get_available_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available data sources
        Returns:
            Dict[str, Dict[str, Any]]: Source information including capabilities
        """
        sources_info = {}
        for source_name, (reader, validator) in self.data_sources.items():
            sources_info[source_name] = {
                'reader_info': reader.get_data_source_info(),
                'validator_info': validator.get_validation_rules(),
                'status': 'available'
            }
        return sources_info

    def add_data_source(self, source_name: str, reader, validator):
        """
        Add a new data source to the manager
        Args:
            source_name (str): Unique identifier for the data source
            reader: Data reader instance (must inherit from BaseDataReader)
            validator: Data validator instance (must inherit from BaseDataValidator)
        """
        self.data_sources[source_name] = (reader, validator)

    def remove_data_source(self, source_name: str):
        """
        Remove a data source from the manager
        Args:
            source_name (str): Data source identifier to remove
        """
        if source_name in self.data_sources:
            del self.data_sources[source_name]

    def get_validation_report(self, source_type: str, **kwargs) -> str:
        """
        Get detailed validation report without raising exceptions
        Args:
            source_type (str): Type of data source
            **kwargs: Arguments passed to the data reader
        Returns:
            str: Detailed validation report
        """
        try:
            validation_result = self.load_and_validate_data(source_type, **kwargs)
            return validation_result.detailed_report()
        except Exception as e:
            return f"Validation failed with exception: {str(e)}"