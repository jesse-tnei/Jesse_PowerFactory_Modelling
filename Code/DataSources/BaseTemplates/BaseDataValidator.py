"""
BaseDataValidator - Abstract base class for data validators
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum
import pandas as pd
from Code.DataSources.ValidationResult import ValidationResult


class BaseDataValidator(ABC):
    """Abstract base class for all data validators"""
    @abstractmethod
    def validate(self, data: Dict[str, pd.DataFrame]) -> ValidationResult:
        """
        Validate data and return results
        Args:
            data (Dict[str, pd.DataFrame]): Data to validate
        Returns:
            ValidationResult: Validation results
        """
        pass
    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Return metadata about validation rules
        Returns:
            Dict[str, Any]: Validation rule metadata
        """
        return {
            'validator_type': self.__class__.__name__,
            'rules_version': '1.0'
        }