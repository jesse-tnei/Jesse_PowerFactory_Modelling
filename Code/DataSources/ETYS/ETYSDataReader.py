"""
ETYSDataReader - ETYS-specific data reader implementation
Handles loading and processing of ETYS Excel files for network modeling.
Part of the Jesse PowerFactory Modelling Framework.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from Code.DataSources.BaseTemplates.BaseDataReader import BaseDataReader


class ETYSDataReader(BaseDataReader):
    """
    Handles loading, parsing, and processing of network data from various sources.
    Provides a unified interface for data access regardless of source format.
    """

    def __init__(self):
        self.coordinate_bounds = {
            'diagram_min_x': 20,
            'diagram_min_y': 20,
            'diagram_width': 260,
            'diagram_height': 170
        }

    # =====================================================================
    # Core Data Loading Functions
    # =====================================================================

    def load_data(self, file_path: str = None, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Load ETYS Excel data - implements BaseDataReader.load_data()
        Args:
            file_path (str): Path to ETYS Excel file
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of DataFrames by sheet name
        """
        if file_path is None:
            raise ValueError("file_path is required for ETYS data loading")
        return self.load_excel_data(file_path)

    def get_supported_formats(self) -> List[str]:
        """Return supported formats for ETYS"""
        return ['excel', 'xlsx', 'xls', 'ETYS']
    def load_excel_data(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        Load Excel file and return dictionary of DataFrames by sheet name.
        Args:
            file_path (str): Path to Excel file
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sheet names to DataFrames
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be read
        """
        try:
            return pd.read_excel(file_path, sheet_name=None)
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load Excel file {file_path}: {str(e)}")

    def get_required_sheets(self) -> List[str]:
        """
        Return list of required Excel sheet names for network modeling.
        Returns:
            List[str]: List of required sheet names
        """
        return [
            'Nodes', 'OHL', 'Cable', 'Composite', 'Zero Length',
            'Transformer', 'Quadbooster', 'Series Compensation', 'SSSC',
            'Shunt Reactor', 'Mechanically Switched Capacitor',
            'SVC', 'STATCOM', 'Sync Comp', 'Series Reactor', 'Series Capacitor',
            'Demand Data', 'TEC Register', 'IC Register', 'Intra_HVDC'
        ]

    def get_sheet_processing_config(self) -> Dict[str, List[str]]:
        """
        Return configuration for processing different sheet types.
        Returns:
            Dict[str, List[str]]: Configuration mapping sheet categories to sheet names
        """
        return {
            'line_sheets': ['OHL', 'Cable', 'Composite', 'Zero Length'],
            'transformer_sheets': ['Transformer', 'Quadbooster', 'Series Compensation', 'SSSC'],
            'shunt_sheets': ['Shunt Reactor', 'Mechanically Switched Capacitor'],
            'dynamic_sheets': ['SVC', 'STATCOM', 'Sync Comp'],
            'series_sheets': ['Series Reactor', 'Series Capacitor'],
            'load_sheets': ['Demand Data'],
            'generator_sheets': ['TEC Register', 'IC Register'],
            'hvdc_sheets': ['Intra_HVDC']
        }

    # =====================================================================
    # Data Type Safety Functions
    # =====================================================================

    def safe_str(self, val: Any, default: str = "") -> str:
        """
        Safely convert value to string with fallback
        Args:
            val: Value to convert
            default (str): Default value if conversion fails
        Returns:
            str: Converted string value
        """
        if pd.isna(val) or val is None:
            return default
        return str(val).strip()

    def safe_float(self, val: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float with fallback.
        Args:
            val: Value to convert
            default (float): Default value if conversion fails
        Returns:
            float: Converted float value
        """
        if pd.isna(val) or val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    # =====================================================================
    # Data Extraction Functions
    # =====================================================================

    def extract_zones_from_nodes(self, df_nodes: pd.DataFrame,
                                 zonal_column_name: str = 'Major Flop Zone') -> List[str]:
        """
        Extract unique zones from nodes dataframe.
        Args:
            df_nodes (pd.DataFrame): Nodes dataframe
            zonal_column_name (str): Name of column containing zone information
        Returns:
            List[str]: List of unique zone names
        """
        if zonal_column_name not in df_nodes.columns:
            return []
        return df_nodes[zonal_column_name].dropna().unique().tolist()

    def extract_areas_from_nodes(self, df_nodes: pd.DataFrame,
                                area_column_name: str = "DESNZ T-Zone") -> List[str]:
        """
        Extract unique areas from nodes dataframe
        Args:
            df_nodes (pd.DataFrame): Nodes dataframe
            area_column_name (str): Name of column containing area information
        Returns:
            List[str]: List of unique area names
        """
        if area_column_name not in df_nodes.columns:
            return []
        return df_nodes[area_column_name].dropna().unique().tolist()

    def filter_valid_nodes(self, df: pd.DataFrame, node_column: str = 'Node') -> pd.DataFrame:
        """
        Filter dataframe to only include rows with valid node references.
        Args:
            df (pd.DataFrame): DataFrame to filter
            node_column (str): Name of column containing node references
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        if node_column not in df.columns:
            return df
        return df[
            df[node_column].notna() &
            df[node_column].astype(str).str.strip().ne('')
        ]

    # =====================================================================
    # Geographic and Coordinate Processing
    # =====================================================================

    def calc_coords(self, nodes: pd.DataFrame, zones: Optional[List[str]] = None,
                   zonal_column_name: Optional[str] = None) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """
        Calculate diagram coordinates for nodes based on geographic data.
        Args:
            nodes (pd.DataFrame): DataFrame with Node, latitude, longitude columns
            zones (Optional[List[str]]): List of zones for per-zone coordinate calculation
            zonal_column_name (Optional[str]): Column name for zone mapping
        Returns:
            Dict: Coordinate mapping - if zones provided: {zone_name: {node_name: (x, y)}, 'global': {...}}
                  if zones None: {node_name: (x, y)}
        """
        if zonal_column_name is None:
            zonal_column_name = 'Major Flop Zone'

        def calculate_coords_for_subset(df_subset: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
            """Calculate coordinates for a subset of nodes"""
            if df_subset.empty:
                return {}

            min_lat = self.safe_float(df_subset.latitude.min())
            max_lat = self.safe_float(df_subset.latitude.max())
            min_lon = self.safe_float(df_subset.longitude.min())
            max_lon = self.safe_float(df_subset.longitude.max())

            # Handle edge case where all nodes are at same location
            lat_rng = max_lat - min_lat if max_lat > min_lat else 1.0
            lon_rng = max_lon - min_lon if max_lon > min_lon else 1.0

            coords = {}
            for _, r in df_subset.iterrows():
                x = (self.safe_float(r.longitude) - min_lon) / lon_rng * self.coordinate_bounds['diagram_width'] + self.coordinate_bounds['diagram_min_x']
                y = (self.safe_float(r.latitude) - min_lat) / lat_rng * self.coordinate_bounds['diagram_height'] + self.coordinate_bounds['diagram_min_y']
                coords[self.safe_str(r.Node)] = (x, y)

            return coords

        if zones is None:
            # Original behavior - global scaling only
            return calculate_coords_for_subset(nodes)

        # New behavior - calculate for each zone plus global
        all_coords = {}

        # Global coordinates
        all_coords['global'] = calculate_coords_for_subset(nodes)

        # Per-zone coordinates
        for zone in zones:
            if zonal_column_name in nodes.columns:
                zone_nodes = nodes[nodes[zonal_column_name] == zone]
                if not zone_nodes.empty:
                    all_coords[zone] = calculate_coords_for_subset(zone_nodes)
                else:
                    all_coords[zone] = {}
            else:
                all_coords[zone] = {}

        return all_coords

    def get_coordinate_bounds(self) -> Dict[str, float]:
        """
        Get standard coordinate bounds for diagram layout.
        Returns:
            Dict[str, float]: Dictionary with coordinate bound parameters
        """
        return self.coordinate_bounds.copy()

    # =====================================================================
    # Date and Time Processing
    # =====================================================================

    def parse_study_date(self, date_string: str) -> int:
        """
        Parse study date string into timestamp.
        Args:
            date_string (str): Date string in dd/mm/yyyy format
        Returns:
            int: Unix timestamp
        Raises:
            ValueError: If date format is invalid
        """
        try:
            return int(datetime.strptime(date_string, "%d/%m/%Y").timestamp())
        except ValueError:
            raise ValueError(f"Invalid date format: '{date_string}'. Expected dd/mm/yyyy")

    # =====================================================================
    # Configuration and Constants
    # =====================================================================

    def get_scotland_reduced_generator_specs(self) -> List[Dict[str, Any]]:
        """
        Return predefined Scotland reduced generator specifications.
        Returns:
            List[Dict[str, Any]]: List of generator specification dictionaries
        """
        return [
            {
                "bus_name": "HAKB4B",
                "name": "HARK-GRNA_ScotlandExternalGrid",
                "mw_imp": 1100.0,
                "mw_exp": 1100.0,
                "plant_type": "External Grid"
            },
            {
                "bus_name": "HAKB4-",
                "name": "HARK-MOFF_ScotlandExternalGrid",
                "mw_imp": 1100.0,
                "mw_exp": 1100.0,
                "plant_type": "External Grid"
            },
            {
                "bus_name": "STWB4Q",
                "name": "STWB-ECCL-1_ScotlandExternalGrid",
                "mw_imp": 1100.0,
                "mw_exp": 1100.0,
                "plant_type": "External Grid"
            },
            {
                "bus_name": "STWB4R",
                "name": "STWB-ECCL-2_ScotlandExternalGrid",
                "mw_imp": 1100.0,
                "mw_exp": 1100.0,
                "plant_type": "External Grid"
            }
        ]

    # =====================================================================
    # Data Processing and Transformation
    # =====================================================================

    def process_generator_data(self, df_gens: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """
        Process and filter generator data based on sheet type.
        Args:
            df_gens (pd.DataFrame): Generator data
            sheet_name (str): Name of the sheet ('TEC Register' or 'IC Register')
        Returns:
            pd.DataFrame: Processed and filtered generator data
        """
        # Filter out rows that shouldn't become machines
        if sheet_name == 'TEC Register':
            mw_mask = df_gens['MW_Capacity'].fillna(0) != 0
        else:
            imp = df_gens.get('MW_Import_Capacity', pd.Series(0, index=df_gens.index)).fillna(0)
            exp = df_gens.get('MW_Export_Capacity', pd.Series(0, index=df_gens.index)).fillna(0)
            mw_mask = (imp != 0) | (exp != 0)
        node_mask = (
            df_gens['ETYS_Node'].notna() &
            df_gens['ETYS_Node'].astype(str).str.strip().ne('')
        )
        return df_gens[mw_mask & node_mask]

    def calculate_generator_export_capacity(self, row: pd.Series, plant_type: str) -> float:
        """
        Calculate export capacity for TEC Register generators based on plant type.
        Args:
            row (pd.Series): Generator data row
            plant_type (str): Plant type string
        Returns:
            float: Export capacity in MW
        """
        mw_capacity = self.safe_float(row.get('MW_Capacity'))
        allowed_components = {"Energy Storage System", "Reactive Compensation", "Demand"}
        plant_components = set(map(str.strip, plant_type.split(";")))
        if plant_type == "Interconnector":
            return mw_capacity
        elif "Energy Storage System" in plant_components and plant_components.issubset(allowed_components):
            return mw_capacity
        elif "Energy Storage System" in plant_components:
            return mw_capacity * 0.6
        else:
            return 0.0

    # =====================================================================
    # Impedance and Electrical Parameter Processing
    # =====================================================================

    def calculate_line_impedances(self, row: pd.Series, v_base: float) -> Tuple[float, float, float]:
        """
        Calculate per-km impedances for line from per-unit values.
        Args:
            row (pd.Series): Line data row
            v_base (float): Base voltage in kV
        Returns:
            Tuple[float, float, float]: (r_ohm_per_km, x_ohm_per_km, b_ohm_per_km)
        """
        total_len = (
            self.safe_float(row.get('OHL Length (km)')) +
            self.safe_float(row.get('Cable Length (km)'))
        )
        total_len = total_len if total_len > 0.01 else 1.0

        # Calculate per-unit impedances on 100MVA base
        z_base = v_base ** 2 / 100.0  # 100 MVA base
        r_pu = self.safe_float(row.get('R (% on 100MVA)')) / 100.0
        x_pu = self.safe_float(row.get('X (% on 100MVA)')) / 100.0
        b_pu = self.safe_float(row.get('B (% on 100MVA)')) / 100.0

        r_ohm_per_km = np.clip((r_pu * z_base) / total_len, 0.01, 0.1)
        x_ohm_per_km = np.clip((x_pu * z_base) / total_len, 0.1, 1.0)
        b_ohm_per_km = np.clip((b_pu * z_base) / total_len, 0.0, 0.0)

        return r_ohm_per_km, x_ohm_per_km, b_ohm_per_km

    def calculate_transformer_parameters(self, row: pd.Series, trafo_rating: float) -> Tuple[float, float]:
        """
        Calculate transformer parameters from Excel data.
        Args:
            row (pd.Series): Transformer data row
            trafo_rating (float): Transformer rating in MVA
        Returns
            Tuple[float, float]: (vsc_percent, copper_loss_kw)
        """
        r_pct = self.safe_float(row.get('R (% on 100MVA)')) * trafo_rating / 100
        x_pct = self.safe_float(row.get('X (% on 100MVA)')) * trafo_rating / 100
        vsc_percent = (r_pct ** 2 + x_pct ** 2) ** 0.5
        copper_loss_kw = r_pct * trafo_rating * 10  # (r_pct / 100) * trafo_rating * 1000

        return vsc_percent, copper_loss_kw