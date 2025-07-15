"""
Multi-Domain Table Recognition System

Universal table structure recognition for any industry or project theme.
Supports healthcare, finance, e-commerce, government, scientific, industrial,
and all other domains with intelligent pattern recognition.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
# Text distance - use local implementation
try:
    from textdistance import levenshtein
except ImportError:
    from .local_textdistance import levenshtein
# NLTK - use local implementation
try:
    import nltk
    from nltk.corpus import wordnet
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
except ImportError:
    from .local_nltk import nltk, wordnet, word_tokenize, WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndustryDomain(Enum):
    """Comprehensive industry domains."""
    # Core Business Domains
    HEALTHCARE = "Healthcare & Medical"
    FINANCE = "Finance & Banking"
    ECOMMERCE = "E-commerce & Retail"
    EDUCATION = "Education & Learning"
    GOVERNMENT = "Government & Public Sector"
    MANUFACTURING = "Manufacturing & Industrial"
    TECHNOLOGY = "Technology & Software"
    TELECOMMUNICATIONS = "Telecommunications"
    TRANSPORTATION = "Transportation & Logistics"
    REAL_ESTATE = "Real Estate & Property"
    
    # Scientific & Research Domains
    SCIENTIFIC_RESEARCH = "Scientific Research"
    PHARMACEUTICAL = "Pharmaceutical & Biotech"
    ENVIRONMENTAL = "Environmental & Sustainability"
    AGRICULTURE = "Agriculture & Food"
    ENERGY = "Energy & Utilities"
    AEROSPACE = "Aerospace & Defense"
    AUTOMOTIVE = "Automotive"
    CHEMICAL = "Chemical & Materials"
    
    # Service Industries
    HOSPITALITY = "Hospitality & Tourism"
    ENTERTAINMENT = "Entertainment & Media"
    SPORTS = "Sports & Recreation"
    LEGAL = "Legal & Law"
    CONSULTING = "Consulting & Professional Services"
    INSURANCE = "Insurance"
    NONPROFIT = "Non-profit & NGO"
    RELIGIOUS = "Religious Organizations"
    
    # Specialized Domains
    MILITARY = "Military & Defense"
    INTELLIGENCE = "Intelligence & Security"
    EMERGENCY_SERVICES = "Emergency Services"
    SOCIAL_SERVICES = "Social Services"
    LIBRARY = "Library & Information Science"
    MUSEUM = "Museum & Cultural Heritage"
    ARCHAEOLOGY = "Archaeology & History"
    LINGUISTICS = "Linguistics & Language"
    
    # Modern & Emerging Domains
    CRYPTOCURRENCY = "Cryptocurrency & Blockchain"
    ARTIFICIAL_INTELLIGENCE = "AI & Machine Learning"
    ROBOTICS = "Robotics & Automation"
    BIOTECHNOLOGY = "Biotechnology & Genetics"
    NANOTECHNOLOGY = "Nanotechnology"
    QUANTUM_COMPUTING = "Quantum Computing"
    SPACE_EXPLORATION = "Space Exploration"
    VIRTUAL_REALITY = "Virtual & Augmented Reality"
    
    # Geographic & Cultural
    INTERNATIONAL = "International & Global"
    REGIONAL = "Regional & Local"
    CULTURAL = "Cultural & Ethnic"
    DEMOGRAPHIC = "Demographic & Census"
    
    # Generic & Unknown
    GENERIC_BUSINESS = "Generic Business"
    UNKNOWN = "Unknown Domain"


@dataclass
class DomainPattern:
    """Pattern for recognizing domain-specific tables."""
    domain: IndustryDomain
    table_patterns: List[str] = field(default_factory=list)
    column_patterns: List[str] = field(default_factory=list)
    keyword_indicators: List[str] = field(default_factory=list)
    relationship_patterns: List[str] = field(default_factory=list)
    data_type_preferences: Dict[str, List[str]] = field(default_factory=dict)
    naming_conventions: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    confidence_weight: float = 1.0


@dataclass
class DomainAnalysisResult:
    """Result of domain analysis for a table or schema."""
    primary_domain: IndustryDomain
    confidence_score: float
    secondary_domains: List[Tuple[IndustryDomain, float]] = field(default_factory=list)
    matched_patterns: List[str] = field(default_factory=list)
    domain_specific_suggestions: List[str] = field(default_factory=list)
    business_context: Dict[str, Any] = field(default_factory=dict)
    compliance_requirements: List[str] = field(default_factory=list)
    industry_standards: List[str] = field(default_factory=list)


class UniversalDomainRecognizer:
    """
    Universal domain recognition system for any industry or project theme.
    
    Features:
    - Recognizes 50+ industry domains
    - Intelligent pattern matching
    - Context-aware analysis
    - Business rule inference
    - Compliance requirement identification
    - Industry standard recommendations
    """
    
    def __init__(self):
        """Initialize the domain recognizer."""
        self.domain_patterns: Dict[IndustryDomain, DomainPattern] = {}
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize all domain patterns
        self._initialize_healthcare_patterns()
        self._initialize_finance_patterns()
        self._initialize_ecommerce_patterns()
        self._initialize_education_patterns()
        self._initialize_government_patterns()
        self._initialize_manufacturing_patterns()
        self._initialize_technology_patterns()
        self._initialize_scientific_patterns()
        self._initialize_specialized_patterns()
        self._initialize_modern_patterns()
        
        # Build pattern indexes
        self._build_pattern_indexes()
    
    def analyze_table_domain(self, table_name: str,
                           column_names: List[str],
                           table_context: Dict[str, Any] = None) -> DomainAnalysisResult:
        """
        Analyze the domain of a single table.

        Args:
            table_name: Name of the table
            column_names: List of column names
            table_context: Additional context information

        Returns:
            Domain analysis result
        """
        domain_scores = defaultdict(float)
        matched_patterns = []

        # Analyze table name
        table_score_results = self._analyze_table_name(table_name)
        for domain, score in table_score_results.items():
            domain_scores[domain] += score * 2.0  # Table name has high weight

        # Analyze column names
        column_score_results = self._analyze_column_names(column_names)
        for domain, score in column_score_results.items():
            domain_scores[domain] += score

        # Analyze context if provided
        if table_context:
            context_score_results = self._analyze_context(table_context)
            for domain, score in context_score_results.items():
                domain_scores[domain] += score * 0.5  # Context has lower weight

        # Normalize scores
        if domain_scores:
            max_score = max(domain_scores.values())
            if max_score > 0:
                for domain in domain_scores:
                    domain_scores[domain] /= max_score

        # Determine primary domain
        if domain_scores:
            primary_domain = max(domain_scores.items(), key=lambda x: x[1])
            primary_domain_enum = primary_domain[0]
            confidence_score = primary_domain[1]

            # Get secondary domains
            secondary_domains = [(domain, score) for domain, score in domain_scores.items()
                               if domain != primary_domain_enum and score > 0.3]
            secondary_domains.sort(key=lambda x: x[1], reverse=True)
        else:
            primary_domain_enum = IndustryDomain.UNKNOWN
            confidence_score = 0.0
            secondary_domains = []

        # Generate domain-specific suggestions
        suggestions = self._generate_domain_suggestions(primary_domain_enum, table_name, column_names)

        # Get business context
        business_context = self._get_business_context(primary_domain_enum)

        # Get compliance requirements
        compliance_requirements = self._get_compliance_requirements(primary_domain_enum)

        # Get industry standards
        industry_standards = self._get_industry_standards(primary_domain_enum)

        return DomainAnalysisResult(
            primary_domain=primary_domain_enum,
            confidence_score=confidence_score,
            secondary_domains=secondary_domains,
            matched_patterns=matched_patterns,
            domain_specific_suggestions=suggestions,
            business_context=business_context,
            compliance_requirements=compliance_requirements,
            industry_standards=industry_standards
        )

    def analyze_schema_domain(self, tables: Dict[str, List[str]]) -> DomainAnalysisResult:
        """
        Analyze the domain of an entire schema.

        Args:
            tables: Dictionary mapping table names to column lists

        Returns:
            Overall schema domain analysis result
        """
        domain_scores = defaultdict(float)
        all_matched_patterns = []
        table_count = len(tables)

        # Analyze each table
        for table_name, column_names in tables.items():
            table_result = self.analyze_table_domain(table_name, column_names)

            # Weight by confidence and add to overall scores
            weight = table_result.confidence_score
            domain_scores[table_result.primary_domain] += weight

            # Add secondary domain scores
            for secondary_domain, score in table_result.secondary_domains:
                domain_scores[secondary_domain] += score * 0.5

            all_matched_patterns.extend(table_result.matched_patterns)

        # Normalize scores by table count
        if table_count > 0:
            for domain in domain_scores:
                domain_scores[domain] /= table_count

        # Determine primary domain
        if domain_scores:
            primary_domain = max(domain_scores.items(), key=lambda x: x[1])
            primary_domain_enum = primary_domain[0]
            confidence_score = primary_domain[1]

            # Get secondary domains
            secondary_domains = [(domain, score) for domain, score in domain_scores.items()
                               if domain != primary_domain_enum and score > 0.2]
            secondary_domains.sort(key=lambda x: x[1], reverse=True)
        else:
            primary_domain_enum = IndustryDomain.UNKNOWN
            confidence_score = 0.0
            secondary_domains = []

        # Generate schema-level suggestions
        suggestions = self._generate_schema_suggestions(primary_domain_enum, tables)

        # Get business context
        business_context = self._get_business_context(primary_domain_enum)
        business_context['table_count'] = table_count
        business_context['schema_complexity'] = self._calculate_schema_complexity(tables)

        # Get compliance requirements
        compliance_requirements = self._get_compliance_requirements(primary_domain_enum)

        # Get industry standards
        industry_standards = self._get_industry_standards(primary_domain_enum)

        return DomainAnalysisResult(
            primary_domain=primary_domain_enum,
            confidence_score=confidence_score,
            secondary_domains=secondary_domains,
            matched_patterns=list(set(all_matched_patterns)),
            domain_specific_suggestions=suggestions,
            business_context=business_context,
            compliance_requirements=compliance_requirements,
            industry_standards=industry_standards
        )

    def _calculate_schema_complexity(self, tables: Dict[str, List[str]]) -> str:
        """Calculate schema complexity level."""
        table_count = len(tables)
        total_columns = sum(len(columns) for columns in tables.values())
        avg_columns_per_table = total_columns / table_count if table_count > 0 else 0

        if table_count < 5:
            return "Simple"
        elif table_count < 20 and avg_columns_per_table < 10:
            return "Moderate"
        elif table_count < 50 and avg_columns_per_table < 15:
            return "Complex"
        else:
            return "Very Complex"


# Global instance of the domain recognizer
DOMAIN_RECOGNIZER = UniversalDomainRecognizer()
