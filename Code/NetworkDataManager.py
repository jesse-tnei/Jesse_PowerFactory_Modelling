"""
NetworkDataManager - Orchestrates data sources for network modeling
Manages multiple data sources and provides standardized data access for the framework.
Part of the Jesse PowerFactory Modelling Framework.
"""

from typing import Dict, Any
import pandas as pd

from Code.DataSources.ETYS.ETYSDataReader import ETYSDataReader
from Code.DataSources.ETYS.ETYSDataValidator import ETYSDataValidator
from Code.DataSources.ValidationResult import ValidationResult


class NetworkDataManager:
    """Orchestrates multiple data sources for network modeling"""
    def __init__(self):
        self.data_sources = {
            'etys': (ETYSDataReader(), ETYSDataValidator())
        }
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
    def get_standardized_data(self, source_type: str, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Get validated and standardized data ready for network creation
        Args:
            source_type (str): Type of data source ('etys', etc.)
            **kwargs: Arguments passed to the data reader
        Returns:
            Dict[str, pd.DataFrame]: Standardized data format
        Raises:
            ValueError: If data validation fails
        """
        validation_result = self.load_and_validate_data(source_type, **kwargs)
        if not validation_result.is_valid:
            raise ValueError(f"Data validation failed: {validation_result.detailed_report()}")
        return self._standardize_to_common_format(validation_result.cleaned_data, source_type)
    def _standardize_to_common_format(self, data: Dict[str, pd.DataFrame], source_type: str) -> Dict[str, pd.DataFrame]:
        """
        Standardize data to common format expected by DataModel and Engines
        Args:
            data (Dict[str, pd.DataFrame]): Source-specific data
            source_type (str): Source type for source-specific handling
        Returns:
            Dict[str, pd.DataFrame]: Standardized data format
        """
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
                standardized_data[standard_name] = self._transform_etys_sheet_data(df, original_sheet, standard_name)
            else:
                # Keep original name if no mapping exists
                standardized_data[original_sheet] = df
        return standardized_data
    def _transform_etys_sheet_data(self, df: pd.DataFrame, original_sheet: str, standard_name: str) -> pd.DataFrame:
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
                transformed_df['voltage_kv'] = pd.to_numeric(transformed_df['Voltage (Derived)'], errors='coerce')
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