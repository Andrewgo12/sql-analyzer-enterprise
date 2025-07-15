"""
Universal Data Type Support System

Comprehensive support for ALL SQL data types including database-specific,
custom types, and even the most obscure data types across all database systems.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTypeCategory(Enum):
    """Categories of data types."""
    NUMERIC = "Numeric"
    STRING = "String/Text"
    DATE_TIME = "Date/Time"
    BOOLEAN = "Boolean"
    BINARY = "Binary/BLOB"
    JSON_XML = "JSON/XML"
    GEOMETRIC = "Geometric/Spatial"
    ARRAY = "Array/Collection"
    CUSTOM = "Custom/User-Defined"
    NETWORK = "Network/Internet"
    UUID = "UUID/Identifier"
    MONETARY = "Monetary/Currency"
    INTERVAL = "Interval/Duration"
    ENUM = "Enumeration"
    COMPOSITE = "Composite/Structured"
    RANGE = "Range/Interval"
    FULL_TEXT = "Full-Text Search"
    CRYPTOGRAPHIC = "Cryptographic"
    MACHINE_LEARNING = "Machine Learning"
    SCIENTIFIC = "Scientific/Mathematical"
    MULTIMEDIA = "Multimedia/Media"


@dataclass
class DataTypeInfo:
    """Comprehensive information about a data type."""
    name: str
    category: DataTypeCategory
    database_systems: List[str]
    aliases: List[str] = field(default_factory=list)
    size_info: Optional[str] = None
    precision_scale: Optional[Tuple[int, int]] = None
    default_value: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    conversion_rules: Dict[str, str] = field(default_factory=dict)
    validation_pattern: Optional[str] = None
    description: str = ""
    examples: List[str] = field(default_factory=list)
    storage_requirements: Optional[str] = None
    performance_notes: List[str] = field(default_factory=list)
    compatibility_notes: Dict[str, str] = field(default_factory=dict)
    deprecated: bool = False
    introduced_version: Optional[str] = None


class UniversalDataTypeRegistry:
    """
    Universal registry for ALL SQL data types across all database systems.
    
    Supports:
    - Standard SQL data types
    - Database-specific types (MySQL, PostgreSQL, Oracle, SQL Server, etc.)
    - Custom and user-defined types
    - Obscure and legacy data types
    - Scientific and specialized data types
    - Modern data types (JSON, arrays, etc.)
    """
    
    def __init__(self):
        """Initialize the universal data type registry."""
        self.data_types: Dict[str, DataTypeInfo] = {}
        self.category_index: Dict[DataTypeCategory, List[str]] = defaultdict(list)
        self.database_index: Dict[str, List[str]] = defaultdict(list)
        self.alias_index: Dict[str, str] = {}
        
        # Initialize all data types
        self._initialize_standard_types()
        self._initialize_mysql_types()
        self._initialize_postgresql_types()
        self._initialize_oracle_types()
        self._initialize_sqlserver_types()
        self._initialize_sqlite_types()
        self._initialize_specialized_types()
        self._initialize_scientific_types()
        self._initialize_legacy_types()
        self._initialize_modern_types()
        
        # Build indexes
        self._build_indexes()
    
    def get_data_type(self, type_name: str) -> Optional[DataTypeInfo]:
        """Get data type information by name or alias."""
        # Try exact match first
        if type_name in self.data_types:
            return self.data_types[type_name]

        # Try case-insensitive lookup
        upper_name = type_name.upper()
        if upper_name in self.alias_index:
            canonical_name = self.alias_index[upper_name]
            return self.data_types[canonical_name]

        return None

    def get_types_by_category(self, category: DataTypeCategory) -> List[DataTypeInfo]:
        """Get all data types in a specific category."""
        type_names = self.category_index.get(category, [])
        return [self.data_types[name] for name in type_names]

    def get_types_by_database(self, database_system: str) -> List[DataTypeInfo]:
        """Get all data types supported by a specific database system."""
        type_names = self.database_index.get(database_system, [])
        return [self.data_types[name] for name in type_names]

    def find_compatible_types(self, source_type: str, target_database: str) -> List[DataTypeInfo]:
        """Find compatible data types for conversion between databases."""
        source_info = self.get_data_type(source_type)
        if not source_info:
            return []

        # Get all types for target database
        target_types = self.get_types_by_database(target_database)

        # Find compatible types (same category or explicit conversion rules)
        compatible = []
        for target_type in target_types:
            if (target_type.category == source_info.category or
                target_database in source_info.conversion_rules):
                compatible.append(target_type)

        return compatible

    def suggest_data_type(self, value_examples: List[str],
                         target_database: str = None) -> List[Tuple[DataTypeInfo, float]]:
        """Suggest appropriate data types based on value examples."""
        suggestions = []

        for type_info in self.data_types.values():
            if target_database and target_database not in type_info.database_systems:
                continue

            confidence = self._calculate_type_confidence(value_examples, type_info)
            if confidence > 0:
                suggestions.append((type_info, confidence))

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:10]  # Return top 10 suggestions

    def get_conversion_path(self, source_type: str, target_type: str) -> Optional[List[str]]:
        """Get conversion path between two data types."""
        source_info = self.get_data_type(source_type)
        target_info = self.get_data_type(target_type)

        if not source_info or not target_info:
            return None

        # Direct conversion
        if target_type in source_info.conversion_rules:
            return [source_type, target_type]

        # Same category conversion
        if source_info.category == target_info.category:
            return [source_type, target_type]

        # Multi-step conversion (simplified)
        # In a real implementation, this would use graph algorithms
        intermediate_types = []

        # Try to find common category
        for type_name, type_info in self.data_types.items():
            if (type_info.category == source_info.category and
                target_type in type_info.conversion_rules):
                intermediate_types.append(type_name)

        if intermediate_types:
            return [source_type, intermediate_types[0], target_type]

        return None

    def validate_data_type_usage(self, type_name: str,
                                database_system: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate data type usage in a specific context."""
        type_info = self.get_data_type(type_name)

        result = {
            'valid': False,
            'warnings': [],
            'suggestions': [],
            'compatibility_notes': []
        }

        if not type_info:
            result['warnings'].append(f"Unknown data type: {type_name}")
            return result

        # Check database compatibility
        if database_system not in type_info.database_systems:
            result['warnings'].append(f"{type_name} is not supported in {database_system}")

            # Suggest alternatives
            compatible_types = self.find_compatible_types(type_name, database_system)
            if compatible_types:
                suggestions = [t.name for t in compatible_types[:3]]
                result['suggestions'].extend(suggestions)
        else:
            result['valid'] = True

        # Check for deprecation
        if type_info.deprecated:
            result['warnings'].append(f"{type_name} is deprecated")

            # Suggest modern alternatives
            modern_alternatives = self.get_types_by_category(type_info.category)
            non_deprecated = [t for t in modern_alternatives if not t.deprecated]
            if non_deprecated:
                result['suggestions'].extend([t.name for t in non_deprecated[:2]])

        # Add compatibility notes
        if database_system in type_info.compatibility_notes:
            result['compatibility_notes'].append(type_info.compatibility_notes[database_system])

        # Context-specific validation
        if context:
            self._validate_context_specific(type_info, context, result)

        return result

    def get_all_categories(self) -> List[DataTypeCategory]:
        """Get all available data type categories."""
        return list(self.category_index.keys())

    def get_all_databases(self) -> List[str]:
        """Get all supported database systems."""
        return list(self.database_index.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the data type registry."""
        return {
            'total_types': len(self.data_types),
            'categories': len(self.category_index),
            'databases': len(self.database_index),
            'aliases': len(self.alias_index),
            'deprecated_types': sum(1 for t in self.data_types.values() if t.deprecated),
            'types_by_category': {cat.value: len(types) for cat, types in self.category_index.items()},
            'types_by_database': {db: len(types) for db, types in self.database_index.items()}
        }


# Global instance of the data type registry
DATA_TYPE_REGISTRY = UniversalDataTypeRegistry()
