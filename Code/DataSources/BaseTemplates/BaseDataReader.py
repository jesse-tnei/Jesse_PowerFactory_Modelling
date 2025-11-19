"""
BaseDataReader - Abstract base class for data readers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd


class BaseDataReader(ABC):
    """Abstract base class for all data readers"""
    @abstractmethod
    def load_data(self, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Load data from source and return dictionary of DataFrames
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping data type to DataFrame
        """
        pass
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Return list of supported data formats
        Returns:
            List[str]: List of supported format identifiers
        """
        pass
    def get_data_source_info(self) -> Dict[str, Any]:
        """
        Return metadata about this data source
        Returns:
            Dict[str, Any]: Source metadata
        """
        return {
            'source_type': self.__class__.__name__,
            'supported_formats': self.get_supported_formats()
        }