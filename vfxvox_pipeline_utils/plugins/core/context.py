"""
Validation context abstraction.

This module provides DCC-agnostic data structures for representing
scene data, validation scope, and context information.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ValidationScope(Enum):
    """Scope of validation operation."""
    SELECTION = "selection"
    SCENE = "scene"
    FILE = "file"
    BATCH = "batch"


class IssueSeverity(Enum):
    """Severity level of a validation issue."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SceneElement:
    """Represents a scene element (node, object, etc.)."""
    element_id: str
    element_type: str  # "node", "object", "geometry", "file"
    name: str
    path: str  # Hierarchical path in scene
    properties: Dict[str, Any] = field(default_factory=dict)
    dcc_handle: Any = None  # DCC-specific object reference


@dataclass
class SceneInfo:
    """Information about the current scene."""
    frame_range: Tuple[int, int]
    current_frame: int
    fps: float
    units: str  # "cm", "m", "in", "ft"
    up_axis: str  # "y", "z"
    file_format: str
    is_saved: bool
    is_modified: bool


@dataclass
class ValidationContext:
    """DCC-agnostic validation context."""
    
    # Context identification
    context_id: str
    dcc_name: str
    dcc_version: str
    scene_path: Optional[str]
    
    # Selection and scope
    selection: List[SceneElement]
    scope: ValidationScope
    
    # Scene information
    scene_info: SceneInfo
    
    # File paths
    working_directory: str
    output_directory: Optional[str]
    
    # User and project
    user: str
    project: Optional[str] = None
    shot: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Validator parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
