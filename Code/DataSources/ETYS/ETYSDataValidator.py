"""
ETYSDataValidator - ETYS-specific validation implementation  
Handles validation, business rule enforcement, and data quality checks for ETYS data.
Part of the Jesse PowerFactory Modelling Framework.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set

from Code.DataSources.BaseTemplates.BaseDataValidator import BaseDataValidator
from Code.DataSources.ValidationResult import ValidationResult, ValidationMessage, ValidationSeverity


class ETYSDataValidator(BaseDataValidator):
    """
    Handles validation, business rule enforcement, and quality assurance for ETYS network data.
    Validates ETYS-specific data structure, electrical parameters, and engineering constraints.
    """

    def __init__(self):
        self.required_node_columns = [
            'Node', 'Voltage (Derived)', 'latitude', 'longitude', 
            'Site Name', 'Relevant TO', 'Type', 'Indoor/Outdoor'
        ]
        self.required_line_columns = [
            'Node 1', 'Node 2', 'Winter Rating (MVA)', 'Summer Rating (MVA)',
            'R (% on 100MVA)', 'X (% on 100MVA)', 'B (% on 100MVA)'
        ]
        self.valid_voltage_levels = {
            0.4, 11, 13, 33, 66, 132, 220, 275, 400, 500, 765
        }

    # =====================================================================
    # Main Validation Functions
    # =====================================================================
    def validate(self, data: Dict[str, pd.DataFrame]) -> ValidationResult:
        """
        Validate ETYS data - implements BaseDataValidator.validate()
        Args:
            data (Dict[str, pd.DataFrame]): ETYS data to validate
        Returns:
            ValidationResult: Validation results
        """
        return self.validate_complete_dataset(data)
    def validate_complete_dataset(self, data_dict: Dict[str, pd.DataFrame]) -> ValidationResult:
        """
        Perform complete validation of network dataset.
        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of DataFrames by sheet name
        Returns:
            ValidationResult: Comprehensive validation results
        """
        messages = []
        # Structural validation
        messages.extend(self._validate_excel_structure(data_dict))
        # Data quality validation
        messages.extend(self._validate_data_quality(data_dict))
        # Business rule validation
        messages.extend(self._validate_business_rules(data_dict))
        # Engineering parameter validation
        messages.extend(self._validate_electrical_parameters(data_dict))
        # Cross-sheet validation
        messages.extend(self._validate_cross_sheet_references(data_dict))
        # Determine overall validity
        has_critical_errors = any(
            msg.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
            for msg in messages
        )
        return ValidationResult(
            is_valid=not has_critical_errors,
            messages=messages,
            cleaned_data=self._clean_and_normalize_data(data_dict) if not has_critical_errors else None
        )

    def validate_excel_structure(self, data_dict: Dict[str, pd.DataFrame]) -> ValidationResult:
        """
        Validate Excel file structure and required sheets/columns.
        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of DataFrames by sheet name
        Returns:
            ValidationResult: Structural validation results
        """
        messages = self._validate_excel_structure(data_dict)
        has_errors = any(msg.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for msg in messages)
        return ValidationResult(
            is_valid=not has_errors,
            messages=messages
        )

    # =====================================================================
    # Structural Validation Functions
    # =====================================================================

    def _validate_excel_structure(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate Excel file structure."""
        messages = []
        # Check for required sheets
        required_sheets = ['Nodes']
        optional_sheets = [
            'OHL', 'Cable', 'Composite', 'Zero Length',
            'Transformer', 'Quadbooster', 'Series Compensation', 'SSSC',
            'Shunt Reactor', 'Mechanically Switched Capacitor',
            'SVC', 'STATCOM', 'Sync Comp', 'Series Reactor', 'Series Capacitor',
            'Demand Data', 'TEC Register', 'IC Register', 'Intra_HVDC'
        ]
        for sheet in required_sheets:
            if sheet not in data_dict:
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.CRITICAL,
                    category="Structure",
                    message=f"Required sheet '{sheet}' not found in Excel file",
                    suggestion="Ensure the Excel file contains all required sheets"
                ))
            elif data_dict[sheet].empty:
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="Structure",
                    message=f"Required sheet '{sheet}' is empty"
                ))
        # Check for column structure in key sheets
        if 'Nodes' in data_dict:
            missing_cols = [col for col in self.required_node_columns if col not in data_dict['Nodes'].columns]
            if missing_cols:
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="Structure",
                    message=f"Nodes sheet missing required columns: {missing_cols}",
                    suggestion="Add missing columns to the Nodes sheet"
                ))
        # Check optional sheets that are present
        for sheet in optional_sheets:
            if sheet in data_dict:
                if data_dict[sheet].empty:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.WARNING,
                        category="Structure",
                        message=f"Sheet '{sheet}' is present but empty"
                    ))
                else:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.INFO,
                        category="Structure",
                        message=f"Sheet '{sheet}' found with {len(data_dict[sheet])} rows"
                    ))
        return messages

    # =====================================================================
    # Data Quality Validation Functions
    # =====================================================================

    def _validate_data_quality(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate data quality and completeness."""
        messages = []
        if 'Nodes' not in data_dict:
            return messages
        df_nodes = data_dict['Nodes']
        # Check for missing node names
        null_nodes = df_nodes['Node'].isnull().sum()
        if null_nodes > 0:
            messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="Data Quality",
                message=f"{null_nodes} nodes have missing names",
                suggestion="Ensure all nodes have valid names"
            ))
        # Check for duplicate nodes
        duplicate_nodes = df_nodes[df_nodes.duplicated(subset=['Node'], keep=False)]
        if not duplicate_nodes.empty:
            messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="Data Quality",
                message=f"Duplicate node names found: {list(duplicate_nodes['Node'].unique())}",
                suggestion="Remove or rename duplicate nodes"
            ))
        # Check for missing coordinates
        missing_lat = df_nodes['latitude'].isnull().sum()
        missing_lon = df_nodes['longitude'].isnull().sum()
        if missing_lat > 0 or missing_lon > 0:
            messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                category="Data Quality",
                message=f"Missing coordinates: {missing_lat} latitude, {missing_lon} longitude",
                suggestion="Verify coordinate data for proper diagram positioning"
            ))
        # Check for missing voltage data
        missing_voltage = df_nodes['Voltage (Derived)'].isnull().sum()
        if missing_voltage > 0:
            messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="Data Quality",
                message=f"{missing_voltage} nodes have missing voltage levels",
                suggestion="Ensure all nodes have valid voltage levels"
            ))
        return messages

    # =====================================================================
    # Business Rule Validation Functions
    # =====================================================================

    def _validate_business_rules(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate business rules and domain constraints."""
        messages = []
        # Validate voltage levels are reasonable
        if 'Nodes' in data_dict:
            df_nodes = data_dict['Nodes']
            invalid_voltages = df_nodes[
                (df_nodes['Voltage (Derived)'].notna()) & 
                (~df_nodes['Voltage (Derived)'].isin(self.valid_voltage_levels))
            ]
            if not invalid_voltages.empty:
                invalid_vals = invalid_voltages['Voltage (Derived)'].unique()
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    category="Business Rules",
                    message=f"Non-standard voltage levels found: {list(invalid_vals)}",
                    suggestion=f"Standard voltage levels are: {sorted(self.valid_voltage_levels)}"
                ))
        # Validate equipment naming conventions
        messages.extend(self._validate_naming_conventions(data_dict))
        # Validate zone consistency
        messages.extend(self._validate_zone_consistency(data_dict))
        return messages

    def _validate_naming_conventions(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate equipment naming conventions."""
        messages = []
        if 'Nodes' in data_dict:
            df_nodes = data_dict['Nodes']
            # Check node naming patterns
            invalid_names = df_nodes[
                df_nodes['Node'].str.contains(r'[^\w\-_]', regex=True, na=False)
            ]
            if not invalid_names.empty:
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    category="Business Rules",
                    message=f"{len(invalid_names)} nodes have non-standard characters in names",
                    suggestion="Node names should only contain letters, numbers, hyphens, and underscores"
                ))
        return messages

    def _validate_zone_consistency(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate zone assignment consistency."""
        messages = []
        if 'Nodes' not in data_dict:
            return messages
        df_nodes = data_dict['Nodes']
        # Check for nodes without zone assignments
        zone_columns = ['Major Flop Zone', 'DESNZ T-Zone']
        for col in zone_columns:
            if col in df_nodes.columns:
                missing_zones = df_nodes[col].isnull().sum()
                if missing_zones > 0:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.WARNING,
                        category="Business Rules",
                        message=f"{missing_zones} nodes missing {col} assignment",
                        suggestion=f"Verify zone assignments for proper network organization"
                    ))
        return messages

    # =====================================================================
    # Electrical Parameter Validation Functions
    # =====================================================================

    def _validate_electrical_parameters(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate electrical parameters and engineering constraints."""
        messages = []
        # Validate line parameters
        line_sheets = ['OHL', 'Cable', 'Composite', 'Zero Length']
        for sheet in line_sheets:
            if sheet in data_dict:
                messages.extend(self._validate_line_parameters(data_dict[sheet], sheet))
        # Validate transformer parameters
        transformer_sheets = ['Transformer', 'Quadbooster', 'Series Compensation', 'SSSC']
        for sheet in transformer_sheets:
            if sheet in data_dict:
                messages.extend(self._validate_transformer_parameters(data_dict[sheet], sheet))
        # Validate generator parameters
        generator_sheets = ['TEC Register', 'IC Register']
        for sheet in generator_sheets:
            if sheet in data_dict:
                messages.extend(self._validate_generator_parameters(data_dict[sheet], sheet))
        return messages

    def _validate_line_parameters(self, df: pd.DataFrame, sheet_name: str) -> List[ValidationMessage]:
        """Validate line electrical parameters."""
        messages = []
        # Check for negative impedances
        impedance_cols = ['R (% on 100MVA)', 'X (% on 100MVA)']
        for col in impedance_cols:
            if col in df.columns:
                negative_vals = df[df[col] < 0]
                if not negative_vals.empty:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.ERROR,
                        category="Electrical Parameters",
                        message=f"{sheet_name}: {len(negative_vals)} lines have negative {col}",
                        location=sheet_name,
                        suggestion="Impedance values should be positive"
                    ))
        # Check for unreasonable ratings
        rating_cols = ['Winter Rating (MVA)', 'Summer Rating (MVA)']
        for col in rating_cols:
            if col in df.columns:
                # Check for zero or negative ratings
                invalid_ratings = df[(df[col] <= 0) | (df[col] > 10000)]
                if not invalid_ratings.empty:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.WARNING,
                        category="Electrical Parameters",
                        message=f"{sheet_name}: {len(invalid_ratings)} lines have unreasonable {col}",
                        location=sheet_name,
                        suggestion="Verify power ratings are realistic (0-10000 MVA)"
                    ))
        return messages

    def _validate_transformer_parameters(self, df: pd.DataFrame, sheet_name: str) -> List[ValidationMessage]:
        """Validate transformer electrical parameters."""
        messages = []
        # Check transformer ratings
        if 'Winter Rating (MVA)' in df.columns:
            invalid_ratings = df[(df['Winter Rating (MVA)'] <= 0) | (df['Winter Rating (MVA)'] > 2000)]
            if not invalid_ratings.empty:
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    category="Electrical Parameters",
                    message=f"{sheet_name}: {len(invalid_ratings)} transformers have unreasonable ratings",
                    location=sheet_name,
                    suggestion="Verify transformer ratings are realistic (0-2000 MVA)"
                ))
        return messages

    def _validate_generator_parameters(self, df: pd.DataFrame, sheet_name: str) -> List[ValidationMessage]:
        """Validate generator electrical parameters."""
        messages = []
        capacity_cols = ['MW_Capacity', 'MW_Import_Capacity', 'MW_Export_Capacity']
        for col in capacity_cols:
            if col in df.columns:
                negative_capacity = df[df[col] < 0]
                if not negative_capacity.empty:
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.WARNING,
                        category="Electrical Parameters",
                        message=f"{sheet_name}: {len(negative_capacity)} generators have negative {col}",
                        location=sheet_name,
                        suggestion="Generator capacities should be positive or zero"
                    ))
        return messages

    # =====================================================================
    # Cross-Sheet Validation Functions
    # =====================================================================

    def _validate_cross_sheet_references(self, data_dict: Dict[str, pd.DataFrame]) -> List[ValidationMessage]:
        """Validate references between sheets."""
        messages = []
        if 'Nodes' not in data_dict:
            return messages
        # Get all valid node names
        valid_nodes = set(data_dict['Nodes']['Node'].dropna().astype(str))
        # Check node references in branch sheets
        branch_sheets = [
            'OHL', 'Cable', 'Composite', 'Zero Length',
            'Transformer', 'Quadbooster', 'Series Compensation', 'SSSC',
            'Series Reactor', 'Series Capacitor', 'Intra_HVDC'
        ]
        for sheet in branch_sheets:
            if sheet in data_dict:
                messages.extend(self._validate_node_references(data_dict[sheet], valid_nodes, sheet))
        # Check node references in equipment sheets
        equipment_sheets = {
            'Demand Data': 'ETYS_Node',
            'TEC Register': 'ETYS_Node',
            'IC Register': 'ETYS_Node',
            'Shunt Reactor': 'Node',
            'Mechanically Switched Capacitor': 'Node',
            'SVC': 'Node',
            'STATCOM': 'Node',
            'Sync Comp': 'Node'
        }
        for sheet, node_col in equipment_sheets.items():
            if sheet in data_dict:
                messages.extend(self._validate_equipment_node_references(
                    data_dict[sheet], valid_nodes, sheet, node_col
                ))
        return messages

    def _validate_node_references(self, df: pd.DataFrame, valid_nodes: Set[str], 
                                 sheet_name: str) -> List[ValidationMessage]:
        """Validate node references in branch sheets."""
        messages = []
        node_cols = ['Node 1', 'Node 2']
        for col in node_cols:
            if col in df.columns:
                invalid_refs = df[~df[col].isin(valid_nodes) & df[col].notna()]
                if not invalid_refs.empty:
                    invalid_nodes = invalid_refs[col].unique()
                    messages.append(ValidationMessage(
                        severity=ValidationSeverity.ERROR,
                        category="Cross-Sheet References",
                        message=f"{sheet_name}: Invalid {col} references: {list(invalid_nodes)}",
                        location=sheet_name,
                        suggestion="Ensure all referenced nodes exist in the Nodes sheet"
                    ))
        return messages

    def _validate_equipment_node_references(self, df: pd.DataFrame, valid_nodes: Set[str], 
                                          sheet_name: str, node_col: str) -> List[ValidationMessage]:
        """Validate node references in equipment sheets."""
        messages = []
        if node_col in df.columns:
            invalid_refs = df[~df[node_col].isin(valid_nodes) & df[node_col].notna()]
            if not invalid_refs.empty:
                invalid_nodes = invalid_refs[node_col].unique()
                messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="Cross-Sheet References",
                    message=f"{sheet_name}: Invalid {node_col} references: {list(invalid_nodes)}",
                    location=sheet_name,
                    suggestion="Ensure all referenced nodes exist in the Nodes sheet"
                ))
        return messages

    # =====================================================================
    # Data Cleaning and Normalization Functions
    # =====================================================================

    def _clean_and_normalize_data(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Clean and normalize data after validation."""
        cleaned_data = {}
        for sheet_name, df in data_dict.items():
            cleaned_df = df.copy()
            # Strip whitespace from string columns
            string_cols = cleaned_df.select_dtypes(include=['object']).columns
            for col in string_cols:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # Replace empty strings with NaN
            cleaned_df = cleaned_df.replace('', pd.NA)
            cleaned_data[sheet_name] = cleaned_df
        return cleaned_data

    def clean_and_normalize(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Public method to clean and normalize data.
        Args:
            data_dict (Dict[str, pd.DataFrame]): Raw data dictionary
        Returns:
            Dict[str, pd.DataFrame]: Cleaned data dictionary
        """
        return self._clean_and_normalize_data(data_dict)