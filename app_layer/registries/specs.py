from dataclasses import dataclass
from typing import Any, List, Optional, Generic, TypeVar
from abc import ABC

# Type variable for the parameter value type
PT = TypeVar("PT")

@dataclass(frozen=True)
class ParamSpec(ABC, Generic[PT]):
    """
    Base abstract class for all parameter specifications.
    
    The generic type PT ensures that the default value matches 
    the specific parameter type.
    """
    id: str
    label: str
    description: str
    default: PT

@dataclass(frozen=True)
class IntParamSpec(ParamSpec[int]):
    """Specifies an integer parameter with optional range constraints."""
    default: int
    min_value: Optional[int] = None
    max_value: Optional[int] = None

@dataclass(frozen=True)
class FloatParamSpec(ParamSpec[float]):
    """Specifies a floating-point parameter with range and step constraints."""
    default: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: float = 0.1

@dataclass(frozen=True)
class ChoiceParamSpec(ParamSpec[str]):
    """Specifies a parameter that must be chosen from a predefined list of strings."""
    choices: List[str]
    default: str

@dataclass(frozen=True)
class BoolParamSpec(ParamSpec[bool]):
    """Specifies a boolean toggle parameter."""
    default: bool