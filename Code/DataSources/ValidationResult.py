"""
ValidationResult - Classes for validation results
Part of the Jesse PowerFactory Modelling Framework.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import pandas as pd


class ValidationSeverity(Enum):
    """Enumeration for validation message severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationMessage:
    """Container for validation messages."""
    severity: ValidationSeverity
    category: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Container for validation results."""
    is_valid: bool
    messages: List[ValidationMessage]
    cleaned_data: Optional[Dict[str, pd.DataFrame]] = None
    @property
    def errors(self) -> List[ValidationMessage]:
        """Get only error messages."""
        return [msg for msg in self.messages if msg.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]
    @property
    def warnings(self) -> List[ValidationMessage]:
        """Get only warning messages."""
        return [msg for msg in self.messages if msg.severity == ValidationSeverity.WARNING]
    def detailed_report(self) -> str:
        """Generate detailed validation report."""
        report = ["Network Data Validation Report", "=" * 35, ""]
        if self.is_valid:
            report.append("✓ Overall Status: VALID")
        else:
            report.append("✗ Overall Status: INVALID")
        report.extend(["", f"Total Messages: {len(self.messages)}", ""])
        for severity in ValidationSeverity:
            severity_msgs = [msg for msg in self.messages if msg.severity == severity]
            if severity_msgs:
                report.append(f"{severity.value} Messages ({len(severity_msgs)}):")
                report.append("-" * 30)
                for msg in severity_msgs:
                    location = f" [{msg.location}]" if msg.location else ""
                    report.append(f"  • {msg.category}: {msg.message}{location}")
                    if msg.suggestion:
                        report.append(f"    Suggestion: {msg.suggestion}")
                report.append("")
        return "\n".join(report)