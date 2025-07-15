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
    
    def _initialize_healthcare_patterns(self):
        """Initialize healthcare domain patterns."""
        self.domain_patterns[IndustryDomain.HEALTHCARE] = DomainPattern(
            domain=IndustryDomain.HEALTHCARE,
            table_patterns=[
                'patient', 'doctor', 'physician', 'nurse', 'medical_record', 'diagnosis',
                'treatment', 'prescription', 'medication', 'hospital', 'clinic', 'ward',
                'appointment', 'visit', 'admission', 'discharge', 'surgery', 'procedure',
                'lab_result', 'test', 'examination', 'vital_signs', 'allergy', 'immunization',
                'insurance_claim', 'billing', 'medical_history', 'symptom', 'condition',
                'department', 'specialty', 'radiology', 'pathology', 'pharmacy', 'emergency'
            ],
            column_patterns=[
                'patient_id', 'medical_record_number', 'mrn', 'ssn', 'date_of_birth', 'dob',
                'blood_type', 'blood_pressure', 'heart_rate', 'temperature', 'weight', 'height',
                'diagnosis_code', 'icd_code', 'cpt_code', 'medication_name', 'dosage', 'frequency',
                'allergies', 'medical_history', 'insurance_number', 'provider_id', 'npi',
                'admission_date', 'discharge_date', 'room_number', 'bed_number', 'emergency_contact'
            ],
            keyword_indicators=[
                'medical', 'health', 'clinical', 'therapeutic', 'diagnostic', 'surgical',
                'pharmaceutical', 'hospital', 'healthcare', 'medicine', 'treatment', 'care',
                'wellness', 'disease', 'illness', 'injury', 'recovery', 'rehabilitation'
            ],
            relationship_patterns=[
                'patient_has_appointments', 'doctor_treats_patient', 'patient_has_allergies',
                'prescription_contains_medications', 'visit_includes_procedures'
            ],
            data_type_preferences={
                'patient_id': ['VARCHAR', 'UUID', 'BIGINT'],
                'medical_record_number': ['VARCHAR', 'CHAR'],
                'date_of_birth': ['DATE'],
                'blood_pressure': ['VARCHAR', 'DECIMAL'],
                'diagnosis_code': ['VARCHAR', 'CHAR']
            },
            naming_conventions=[
                'Use patient_id as primary identifier',
                'Include audit fields (created_by, updated_by, created_at, updated_at)',
                'Use standard medical coding systems (ICD, CPT, SNOMED)',
                'Maintain HIPAA compliance in naming'
            ],
            business_rules=[
                'Patient data must be encrypted',
                'Audit trail required for all changes',
                'Access control based on role and need-to-know',
                'Data retention policies must be enforced'
            ],
            confidence_weight=1.0
        )
    
    def _initialize_finance_patterns(self):
        """Initialize finance domain patterns."""
        self.domain_patterns[IndustryDomain.FINANCE] = DomainPattern(
            domain=IndustryDomain.FINANCE,
            table_patterns=[
                'account', 'customer', 'transaction', 'payment', 'transfer', 'deposit',
                'withdrawal', 'loan', 'credit', 'debit', 'balance', 'statement', 'invoice',
                'bill', 'receipt', 'portfolio', 'investment', 'stock', 'bond', 'mutual_fund',
                'bank', 'branch', 'atm', 'card', 'credit_card', 'debit_card', 'merchant',
                'currency', 'exchange_rate', 'interest', 'fee', 'commission', 'tax',
                'audit', 'compliance', 'risk', 'fraud', 'kyc', 'aml', 'regulatory'
            ],
            column_patterns=[
                'account_number', 'customer_id', 'transaction_id', 'amount', 'currency_code',
                'balance', 'available_balance', 'credit_limit', 'interest_rate', 'apr',
                'routing_number', 'swift_code', 'iban', 'sort_code', 'bsb', 'ifsc',
                'transaction_date', 'settlement_date', 'value_date', 'posting_date',
                'merchant_id', 'terminal_id', 'authorization_code', 'reference_number',
                'tax_id', 'ssn', 'ein', 'vat_number', 'risk_score', 'credit_score'
            ],
            keyword_indicators=[
                'financial', 'banking', 'monetary', 'fiscal', 'economic', 'commercial',
                'payment', 'transaction', 'account', 'balance', 'credit', 'debit',
                'investment', 'trading', 'portfolio', 'asset', 'liability', 'equity'
            ],
            relationship_patterns=[
                'customer_has_accounts', 'account_has_transactions', 'customer_has_cards',
                'transaction_involves_accounts', 'portfolio_contains_investments'
            ],
            data_type_preferences={
                'account_number': ['VARCHAR', 'CHAR'],
                'amount': ['DECIMAL', 'MONEY', 'NUMERIC'],
                'balance': ['DECIMAL', 'MONEY'],
                'interest_rate': ['DECIMAL', 'FLOAT'],
                'transaction_date': ['TIMESTAMP', 'DATETIME']
            },
            naming_conventions=[
                'Use account_number for account identification',
                'Monetary amounts should use DECIMAL type',
                'Include currency_code for multi-currency support',
                'Maintain transaction audit trail'
            ],
            business_rules=[
                'All monetary transactions must be logged',
                'Regulatory compliance required (SOX, PCI-DSS)',
                'Data encryption for sensitive financial data',
                'Real-time fraud detection and monitoring'
            ],
            confidence_weight=1.0
        )
    
    def _initialize_ecommerce_patterns(self):
        """Initialize e-commerce domain patterns."""
        self.domain_patterns[IndustryDomain.ECOMMERCE] = DomainPattern(
            domain=IndustryDomain.ECOMMERCE,
            table_patterns=[
                'product', 'category', 'brand', 'inventory', 'stock', 'warehouse',
                'customer', 'user', 'order', 'cart', 'shopping_cart', 'wishlist',
                'payment', 'shipping', 'delivery', 'address', 'review', 'rating',
                'coupon', 'discount', 'promotion', 'sale', 'price', 'pricing',
                'vendor', 'supplier', 'manufacturer', 'distributor', 'retailer',
                'analytics', 'tracking', 'session', 'click', 'view', 'conversion'
            ],
            column_patterns=[
                'product_id', 'sku', 'upc', 'ean', 'isbn', 'product_name', 'description',
                'price', 'cost', 'msrp', 'sale_price', 'discount_amount', 'tax_amount',
                'quantity', 'stock_level', 'reorder_point', 'weight', 'dimensions',
                'category_id', 'brand_id', 'vendor_id', 'customer_id', 'user_id',
                'order_id', 'order_date', 'ship_date', 'delivery_date', 'tracking_number',
                'payment_method', 'credit_card_number', 'billing_address', 'shipping_address',
                'rating', 'review_text', 'review_date', 'verified_purchase'
            ],
            keyword_indicators=[
                'commerce', 'retail', 'shopping', 'store', 'marketplace', 'catalog',
                'product', 'inventory', 'order', 'purchase', 'sale', 'customer',
                'shipping', 'delivery', 'payment', 'checkout', 'cart', 'wishlist'
            ],
            relationship_patterns=[
                'customer_places_orders', 'order_contains_products', 'product_belongs_to_category',
                'customer_writes_reviews', 'product_has_inventory'
            ],
            data_type_preferences={
                'product_id': ['VARCHAR', 'UUID', 'BIGINT'],
                'price': ['DECIMAL', 'MONEY'],
                'quantity': ['INT', 'DECIMAL'],
                'rating': ['DECIMAL', 'FLOAT'],
                'order_date': ['TIMESTAMP', 'DATETIME']
            },
            naming_conventions=[
                'Use SKU for product identification',
                'Include created_at and updated_at timestamps',
                'Use consistent naming for IDs (product_id, customer_id)',
                'Separate billing and shipping addresses'
            ],
            business_rules=[
                'Inventory tracking and management',
                'Order fulfillment workflow',
                'Customer data privacy compliance',
                'Payment processing security (PCI compliance)'
            ],
            confidence_weight=1.0
        )

    def _initialize_education_patterns(self):
        """Initialize education domain patterns."""
        self.domain_patterns[IndustryDomain.EDUCATION] = DomainPattern(
            domain=IndustryDomain.EDUCATION,
            table_patterns=[
                'student', 'teacher', 'instructor', 'professor', 'faculty', 'staff',
                'course', 'class', 'subject', 'curriculum', 'syllabus', 'lesson',
                'enrollment', 'registration', 'grade', 'transcript', 'assignment',
                'exam', 'test', 'quiz', 'homework', 'project', 'thesis', 'dissertation',
                'school', 'university', 'college', 'department', 'program', 'degree',
                'semester', 'term', 'academic_year', 'schedule', 'timetable',
                'library', 'book', 'resource', 'research', 'publication'
            ],
            column_patterns=[
                'student_id', 'student_number', 'teacher_id', 'course_id', 'class_id',
                'enrollment_date', 'graduation_date', 'gpa', 'grade_point_average',
                'credit_hours', 'credits', 'grade', 'score', 'percentage', 'marks',
                'attendance', 'absent_days', 'present_days', 'semester', 'term',
                'academic_year', 'major', 'minor', 'concentration', 'specialization',
                'degree_type', 'degree_level', 'graduation_status', 'transcript_id'
            ],
            keyword_indicators=[
                'education', 'academic', 'school', 'university', 'college', 'learning',
                'teaching', 'instruction', 'curriculum', 'course', 'student', 'teacher',
                'grade', 'exam', 'study', 'research', 'knowledge', 'scholarship'
            ],
            confidence_weight=1.0
        )

    def _initialize_government_patterns(self):
        """Initialize government domain patterns."""
        self.domain_patterns[IndustryDomain.GOVERNMENT] = DomainPattern(
            domain=IndustryDomain.GOVERNMENT,
            table_patterns=[
                'citizen', 'resident', 'taxpayer', 'voter', 'official', 'employee',
                'department', 'agency', 'bureau', 'office', 'ministry', 'council',
                'license', 'permit', 'certificate', 'registration', 'application',
                'tax', 'revenue', 'budget', 'expenditure', 'appropriation', 'fund',
                'law', 'regulation', 'ordinance', 'statute', 'policy', 'procedure',
                'case', 'hearing', 'court', 'judge', 'jury', 'verdict', 'sentence',
                'election', 'ballot', 'candidate', 'party', 'campaign', 'vote'
            ],
            column_patterns=[
                'citizen_id', 'ssn', 'tax_id', 'voter_id', 'license_number',
                'permit_number', 'case_number', 'docket_number', 'file_number',
                'issue_date', 'expiry_date', 'renewal_date', 'effective_date',
                'jurisdiction', 'district', 'precinct', 'ward', 'zone', 'region',
                'tax_amount', 'fee_amount', 'fine_amount', 'penalty_amount',
                'status', 'approval_status', 'compliance_status', 'payment_status'
            ],
            keyword_indicators=[
                'government', 'public', 'municipal', 'federal', 'state', 'local',
                'official', 'administrative', 'regulatory', 'legal', 'civic',
                'citizen', 'taxpayer', 'voter', 'license', 'permit', 'compliance'
            ],
            confidence_weight=1.0
        )

    def _initialize_manufacturing_patterns(self):
        """Initialize manufacturing domain patterns."""
        self.domain_patterns[IndustryDomain.MANUFACTURING] = DomainPattern(
            domain=IndustryDomain.MANUFACTURING,
            table_patterns=[
                'product', 'component', 'part', 'material', 'raw_material', 'ingredient',
                'assembly', 'subassembly', 'bom', 'bill_of_materials', 'recipe', 'formula',
                'production', 'manufacturing', 'batch', 'lot', 'run', 'order',
                'work_order', 'job', 'operation', 'process', 'step', 'stage',
                'machine', 'equipment', 'tool', 'fixture', 'die', 'mold',
                'factory', 'plant', 'facility', 'line', 'station', 'cell',
                'quality', 'inspection', 'test', 'defect', 'rework', 'scrap',
                'inventory', 'stock', 'warehouse', 'storage', 'location', 'bin'
            ],
            column_patterns=[
                'part_number', 'component_id', 'material_id', 'batch_number',
                'lot_number', 'serial_number', 'work_order_id', 'job_number',
                'operation_id', 'machine_id', 'tool_id', 'station_id',
                'quantity_produced', 'quantity_required', 'quantity_consumed',
                'start_time', 'end_time', 'cycle_time', 'setup_time', 'run_time',
                'yield', 'efficiency', 'utilization', 'downtime', 'uptime',
                'defect_count', 'rework_count', 'scrap_count', 'quality_score'
            ],
            keyword_indicators=[
                'manufacturing', 'production', 'assembly', 'fabrication', 'processing',
                'industrial', 'factory', 'plant', 'machine', 'equipment', 'tool',
                'quality', 'batch', 'lot', 'component', 'material', 'inventory'
            ],
            confidence_weight=1.0
        )

    def _initialize_technology_patterns(self):
        """Initialize technology domain patterns."""
        self.domain_patterns[IndustryDomain.TECHNOLOGY] = DomainPattern(
            domain=IndustryDomain.TECHNOLOGY,
            table_patterns=[
                'user', 'account', 'profile', 'session', 'login', 'authentication',
                'application', 'software', 'system', 'service', 'api', 'endpoint',
                'server', 'database', 'table', 'index', 'query', 'transaction',
                'log', 'event', 'error', 'exception', 'alert', 'notification',
                'deployment', 'release', 'version', 'build', 'commit', 'branch',
                'project', 'repository', 'code', 'module', 'component', 'library',
                'test', 'bug', 'issue', 'ticket', 'feature', 'requirement'
            ],
            column_patterns=[
                'user_id', 'username', 'email', 'password_hash', 'api_key', 'token',
                'session_id', 'ip_address', 'user_agent', 'device_id', 'platform',
                'application_id', 'service_id', 'server_id', 'instance_id',
                'timestamp', 'created_at', 'updated_at', 'last_login', 'last_seen',
                'status', 'state', 'is_active', 'is_enabled', 'is_deleted',
                'version_number', 'build_number', 'commit_hash', 'branch_name',
                'cpu_usage', 'memory_usage', 'disk_usage', 'network_usage'
            ],
            keyword_indicators=[
                'technology', 'software', 'system', 'application', 'digital',
                'computer', 'internet', 'web', 'mobile', 'cloud', 'api',
                'database', 'server', 'network', 'security', 'authentication'
            ],
            confidence_weight=1.0
        )

    def _initialize_scientific_patterns(self):
        """Initialize scientific research domain patterns."""
        self.domain_patterns[IndustryDomain.SCIENTIFIC_RESEARCH] = DomainPattern(
            domain=IndustryDomain.SCIENTIFIC_RESEARCH,
            table_patterns=[
                'experiment', 'study', 'research', 'project', 'investigation',
                'sample', 'specimen', 'subject', 'participant', 'volunteer',
                'measurement', 'observation', 'data_point', 'reading', 'result',
                'analysis', 'calculation', 'computation', 'model', 'simulation',
                'hypothesis', 'theory', 'conclusion', 'finding', 'discovery',
                'publication', 'paper', 'article', 'journal', 'conference',
                'researcher', 'scientist', 'investigator', 'author', 'collaborator',
                'laboratory', 'facility', 'equipment', 'instrument', 'device'
            ],
            column_patterns=[
                'experiment_id', 'study_id', 'sample_id', 'specimen_id',
                'participant_id', 'subject_id', 'measurement_id', 'observation_id',
                'value', 'measurement_value', 'reading', 'result', 'outcome',
                'unit', 'measurement_unit', 'precision', 'accuracy', 'error',
                'confidence_interval', 'p_value', 'significance', 'correlation',
                'date_collected', 'time_collected', 'collection_method',
                'researcher_id', 'principal_investigator', 'lab_id', 'facility_id'
            ],
            keyword_indicators=[
                'scientific', 'research', 'experimental', 'analytical', 'empirical',
                'laboratory', 'study', 'investigation', 'measurement', 'observation',
                'hypothesis', 'theory', 'data', 'analysis', 'result', 'finding'
            ],
            confidence_weight=1.0
        )

    def _initialize_specialized_patterns(self):
        """Initialize specialized domain patterns."""
        # Legal domain
        self.domain_patterns[IndustryDomain.LEGAL] = DomainPattern(
            domain=IndustryDomain.LEGAL,
            table_patterns=[
                'case', 'client', 'lawyer', 'attorney', 'judge', 'court', 'hearing',
                'contract', 'agreement', 'document', 'evidence', 'witness', 'testimony',
                'law', 'statute', 'regulation', 'precedent', 'ruling', 'verdict',
                'billing', 'timesheet', 'invoice', 'retainer', 'fee', 'expense'
            ],
            column_patterns=[
                'case_number', 'client_id', 'attorney_id', 'court_id', 'docket_number',
                'filing_date', 'hearing_date', 'trial_date', 'settlement_date',
                'billable_hours', 'hourly_rate', 'total_fee', 'retainer_amount'
            ],
            keyword_indicators=['legal', 'law', 'court', 'attorney', 'case', 'contract'],
            confidence_weight=1.0
        )

        # Military domain
        self.domain_patterns[IndustryDomain.MILITARY] = DomainPattern(
            domain=IndustryDomain.MILITARY,
            table_patterns=[
                'personnel', 'soldier', 'officer', 'unit', 'division', 'battalion',
                'mission', 'operation', 'deployment', 'assignment', 'duty', 'post',
                'equipment', 'weapon', 'vehicle', 'aircraft', 'vessel', 'supply',
                'rank', 'promotion', 'decoration', 'medal', 'award', 'commendation'
            ],
            column_patterns=[
                'service_number', 'rank', 'unit_id', 'deployment_id', 'mission_id',
                'security_clearance', 'mos', 'specialty_code', 'enlistment_date',
                'discharge_date', 'service_years', 'combat_tours'
            ],
            keyword_indicators=['military', 'army', 'navy', 'air_force', 'marine', 'defense'],
            confidence_weight=1.0
        )

        # Sports domain
        self.domain_patterns[IndustryDomain.SPORTS] = DomainPattern(
            domain=IndustryDomain.SPORTS,
            table_patterns=[
                'player', 'team', 'coach', 'game', 'match', 'season', 'league',
                'tournament', 'championship', 'score', 'statistic', 'performance',
                'injury', 'training', 'practice', 'venue', 'stadium', 'arena'
            ],
            column_patterns=[
                'player_id', 'team_id', 'game_id', 'season_id', 'jersey_number',
                'position', 'goals', 'assists', 'points', 'wins', 'losses',
                'batting_average', 'era', 'yards', 'touchdowns', 'fouls'
            ],
            keyword_indicators=['sports', 'athletic', 'game', 'team', 'player', 'competition'],
            confidence_weight=1.0
        )

    def _initialize_modern_patterns(self):
        """Initialize modern and emerging domain patterns."""
        # Cryptocurrency domain
        self.domain_patterns[IndustryDomain.CRYPTOCURRENCY] = DomainPattern(
            domain=IndustryDomain.CRYPTOCURRENCY,
            table_patterns=[
                'wallet', 'address', 'transaction', 'block', 'blockchain', 'hash',
                'cryptocurrency', 'token', 'coin', 'exchange', 'trading', 'order',
                'mining', 'miner', 'pool', 'reward', 'fee', 'gas', 'smart_contract'
            ],
            column_patterns=[
                'wallet_address', 'transaction_hash', 'block_hash', 'block_number',
                'amount', 'gas_price', 'gas_limit', 'nonce', 'confirmation_count',
                'private_key', 'public_key', 'signature', 'timestamp'
            ],
            keyword_indicators=['crypto', 'blockchain', 'bitcoin', 'ethereum', 'token', 'mining'],
            confidence_weight=1.0
        )

        # AI/ML domain
        self.domain_patterns[IndustryDomain.ARTIFICIAL_INTELLIGENCE] = DomainPattern(
            domain=IndustryDomain.ARTIFICIAL_INTELLIGENCE,
            table_patterns=[
                'model', 'dataset', 'training', 'validation', 'test', 'prediction',
                'feature', 'label', 'algorithm', 'neural_network', 'layer', 'neuron',
                'experiment', 'hyperparameter', 'metric', 'accuracy', 'loss', 'epoch'
            ],
            column_patterns=[
                'model_id', 'dataset_id', 'feature_vector', 'prediction_score',
                'confidence_score', 'accuracy', 'precision', 'recall', 'f1_score',
                'learning_rate', 'batch_size', 'epoch_number', 'loss_value'
            ],
            keyword_indicators=['ai', 'ml', 'machine_learning', 'neural', 'deep_learning', 'algorithm'],
            confidence_weight=1.0
        )

    def _build_pattern_indexes(self):
        """Build indexes for efficient pattern matching."""
        self.table_keyword_index = defaultdict(list)
        self.column_keyword_index = defaultdict(list)
        self.general_keyword_index = defaultdict(list)

        for domain, pattern in self.domain_patterns.items():
            # Index table patterns
            for table_pattern in pattern.table_patterns:
                self.table_keyword_index[table_pattern.lower()].append(domain)

            # Index column patterns
            for column_pattern in pattern.column_patterns:
                self.column_keyword_index[column_pattern.lower()].append(domain)

            # Index general keywords
            for keyword in pattern.keyword_indicators:
                self.general_keyword_index[keyword.lower()].append(domain)

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

    def _analyze_table_name(self, table_name: str) -> Dict[IndustryDomain, float]:
        """Analyze table name for domain indicators."""
        scores = defaultdict(float)
        table_lower = table_name.lower()

        # Direct keyword matching
        for keyword, domains in self.table_keyword_index.items():
            if keyword in table_lower:
                for domain in domains:
                    scores[domain] += 1.0

        # Fuzzy matching for similar words
        for keyword, domains in self.table_keyword_index.items():
            similarity = 1 - (levenshtein(table_lower, keyword) / max(len(table_lower), len(keyword)))
            if similarity > 0.8:  # High similarity threshold
                for domain in domains:
                    scores[domain] += similarity * 0.7

        # Word-based analysis
        table_words = re.findall(r'\w+', table_lower)
        for word in table_words:
            lemmatized_word = self.lemmatizer.lemmatize(word)

            # Check against general keywords
            for keyword, domains in self.general_keyword_index.items():
                if lemmatized_word == keyword or word == keyword:
                    for domain in domains:
                        scores[domain] += 0.5

        return dict(scores)

    def _analyze_column_names(self, column_names: List[str]) -> Dict[IndustryDomain, float]:
        """Analyze column names for domain indicators."""
        scores = defaultdict(float)

        for column_name in column_names:
            column_lower = column_name.lower()

            # Direct keyword matching
            for keyword, domains in self.column_keyword_index.items():
                if keyword in column_lower:
                    for domain in domains:
                        scores[domain] += 0.8

            # Pattern matching (e.g., _id, _date, _amount)
            column_words = re.findall(r'\w+', column_lower)
            for word in column_words:
                lemmatized_word = self.lemmatizer.lemmatize(word)

                # Check against general keywords
                for keyword, domains in self.general_keyword_index.items():
                    if lemmatized_word == keyword or word == keyword:
                        for domain in domains:
                            scores[domain] += 0.3

        return dict(scores)

    def _analyze_context(self, context: Dict[str, Any]) -> Dict[IndustryDomain, float]:
        """Analyze additional context for domain indicators."""
        scores = defaultdict(float)

        # Analyze context values
        for key, value in context.items():
            if isinstance(value, str):
                value_lower = value.lower()

                # Check against general keywords
                for keyword, domains in self.general_keyword_index.items():
                    if keyword in value_lower:
                        for domain in domains:
                            scores[domain] += 0.2

        return dict(scores)

    def _generate_domain_suggestions(self, domain: IndustryDomain,
                                   table_name: str,
                                   column_names: List[str]) -> List[str]:
        """Generate domain-specific suggestions."""
        suggestions = []

        if domain == IndustryDomain.UNKNOWN:
            return ["Consider adding more descriptive table and column names to improve domain recognition"]

        domain_pattern = self.domain_patterns.get(domain)
        if not domain_pattern:
            return suggestions

        # Suggest missing common columns
        existing_columns_lower = [col.lower() for col in column_names]

        if domain == IndustryDomain.HEALTHCARE:
            if 'patient_id' not in existing_columns_lower:
                suggestions.append("Consider adding 'patient_id' column for patient identification")
            if 'created_at' not in existing_columns_lower:
                suggestions.append("Add audit fields: created_at, updated_at for HIPAA compliance")
            if 'medical_record_number' not in existing_columns_lower and 'patient' in table_name.lower():
                suggestions.append("Consider adding 'medical_record_number' for unique patient identification")

        elif domain == IndustryDomain.FINANCE:
            if 'amount' in table_name.lower() or 'transaction' in table_name.lower():
                if 'currency_code' not in existing_columns_lower:
                    suggestions.append("Add 'currency_code' for multi-currency support")
                if 'transaction_date' not in existing_columns_lower:
                    suggestions.append("Include 'transaction_date' with timezone information")
            if 'account' in table_name.lower():
                if 'account_number' not in existing_columns_lower:
                    suggestions.append("Add 'account_number' for unique account identification")

        elif domain == IndustryDomain.ECOMMERCE:
            if 'product' in table_name.lower():
                if 'sku' not in existing_columns_lower:
                    suggestions.append("Add 'sku' (Stock Keeping Unit) for product identification")
                if 'price' not in existing_columns_lower:
                    suggestions.append("Include 'price' column for product pricing")
            if 'order' in table_name.lower():
                if 'order_date' not in existing_columns_lower:
                    suggestions.append("Add 'order_date' for order tracking")
                if 'customer_id' not in existing_columns_lower:
                    suggestions.append("Include 'customer_id' for customer relationship")

        # Add naming convention suggestions
        suggestions.extend(domain_pattern.naming_conventions[:2])  # Limit to 2 suggestions

        return suggestions

    def _get_business_context(self, domain: IndustryDomain) -> Dict[str, Any]:
        """Get business context for the domain."""
        context = {
            'domain': domain.value,
            'typical_operations': [],
            'key_metrics': [],
            'common_workflows': [],
            'data_sensitivity': 'Medium'
        }

        if domain == IndustryDomain.HEALTHCARE:
            context.update({
                'typical_operations': ['Patient registration', 'Appointment scheduling', 'Medical records management'],
                'key_metrics': ['Patient satisfaction', 'Treatment outcomes', 'Readmission rates'],
                'common_workflows': ['Admission-Discharge-Transfer', 'Clinical documentation', 'Billing'],
                'data_sensitivity': 'Very High'
            })

        elif domain == IndustryDomain.FINANCE:
            context.update({
                'typical_operations': ['Account management', 'Transaction processing', 'Risk assessment'],
                'key_metrics': ['Transaction volume', 'Account balance', 'Risk scores'],
                'common_workflows': ['Payment processing', 'Account opening', 'Compliance reporting'],
                'data_sensitivity': 'Very High'
            })

        elif domain == IndustryDomain.ECOMMERCE:
            context.update({
                'typical_operations': ['Order processing', 'Inventory management', 'Customer service'],
                'key_metrics': ['Conversion rate', 'Average order value', 'Customer lifetime value'],
                'common_workflows': ['Order fulfillment', 'Returns processing', 'Customer onboarding'],
                'data_sensitivity': 'High'
            })

        return context

    def _get_compliance_requirements(self, domain: IndustryDomain) -> List[str]:
        """Get compliance requirements for the domain."""
        requirements = []

        if domain == IndustryDomain.HEALTHCARE:
            requirements = [
                'HIPAA (Health Insurance Portability and Accountability Act)',
                'HITECH (Health Information Technology for Economic and Clinical Health)',
                'FDA regulations for medical devices',
                'State medical privacy laws'
            ]

        elif domain == IndustryDomain.FINANCE:
            requirements = [
                'SOX (Sarbanes-Oxley Act)',
                'PCI DSS (Payment Card Industry Data Security Standard)',
                'GDPR (General Data Protection Regulation)',
                'Basel III banking regulations',
                'Anti-Money Laundering (AML) requirements'
            ]

        elif domain == IndustryDomain.ECOMMERCE:
            requirements = [
                'PCI DSS for payment processing',
                'GDPR for customer data protection',
                'CCPA (California Consumer Privacy Act)',
                'FTC regulations for online commerce'
            ]

        elif domain == IndustryDomain.GOVERNMENT:
            requirements = [
                'FISMA (Federal Information Security Management Act)',
                'Privacy Act of 1974',
                'Freedom of Information Act (FOIA)',
                'Government data classification requirements'
            ]

        return requirements

    def _get_industry_standards(self, domain: IndustryDomain) -> List[str]:
        """Get industry standards for the domain."""
        standards = []

        if domain == IndustryDomain.HEALTHCARE:
            standards = [
                'HL7 FHIR for healthcare data exchange',
                'ICD-10 for diagnosis coding',
                'CPT for procedure coding',
                'SNOMED CT for clinical terminology',
                'DICOM for medical imaging'
            ]

        elif domain == IndustryDomain.FINANCE:
            standards = [
                'ISO 20022 for financial messaging',
                'SWIFT standards for international transfers',
                'FIX protocol for trading',
                'XBRL for financial reporting',
                'ISO 27001 for information security'
            ]

        elif domain == IndustryDomain.ECOMMERCE:
            standards = [
                'EDI standards for electronic data interchange',
                'UPC/EAN for product identification',
                'ISO 8601 for date/time formatting',
                'OAuth 2.0 for API authentication',
                'OpenAPI for API documentation'
            ]

        elif domain == IndustryDomain.MANUFACTURING:
            standards = [
                'ISO 9001 for quality management',
                'ISA-95 for manufacturing operations',
                'OPC UA for industrial communication',
                'STEP for product data exchange',
                'Six Sigma for process improvement'
            ]

        return standards

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

    def _generate_schema_suggestions(self, domain: IndustryDomain,
                                   tables: Dict[str, List[str]]) -> List[str]:
        """Generate schema-level suggestions."""
        suggestions = []
        table_names = list(tables.keys())

        # Check for missing common tables in the domain
        if domain == IndustryDomain.HEALTHCARE:
            common_tables = ['patient', 'doctor', 'appointment', 'medical_record']
            missing_tables = [table for table in common_tables
                            if not any(table in name.lower() for name in table_names)]
            if missing_tables:
                suggestions.append(f"Consider adding common healthcare tables: {', '.join(missing_tables)}")

        elif domain == IndustryDomain.FINANCE:
            common_tables = ['account', 'transaction', 'customer', 'payment']
            missing_tables = [table for table in common_tables
                            if not any(table in name.lower() for name in table_names)]
            if missing_tables:
                suggestions.append(f"Consider adding common finance tables: {', '.join(missing_tables)}")

        elif domain == IndustryDomain.ECOMMERCE:
            common_tables = ['product', 'customer', 'order', 'inventory']
            missing_tables = [table for table in common_tables
                            if not any(table in name.lower() for name in table_names)]
            if missing_tables:
                suggestions.append(f"Consider adding common e-commerce tables: {', '.join(missing_tables)}")

        # Check for audit tables
        has_audit_table = any('audit' in name.lower() or 'log' in name.lower()
                             for name in table_names)
        if not has_audit_table and len(tables) > 5:
            suggestions.append("Consider adding audit/log tables for compliance and debugging")

        return suggestions

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
