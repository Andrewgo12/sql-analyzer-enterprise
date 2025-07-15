"""
Enterprise Database Engine Support System
Comprehensive support for 50+ database types including SQL and NoSQL
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import re
import logging

logger = logging.getLogger(__name__)

class DatabaseCategory(Enum):
    """Database categories for classification"""
    RELATIONAL_SQL = "relational_sql"
    NOSQL_DOCUMENT = "nosql_document"
    NOSQL_KEY_VALUE = "nosql_key_value"
    NOSQL_COLUMN_FAMILY = "nosql_column_family"
    NOSQL_GRAPH = "nosql_graph"
    TIME_SERIES = "time_series"
    SEARCH_ENGINE = "search_engine"
    DATA_WAREHOUSE = "data_warehouse"
    CLOUD_NATIVE = "cloud_native"
    IN_MEMORY = "in_memory"
    EMBEDDED = "embedded"
    SPECIALIZED = "specialized"

class DatabaseEngine(Enum):
    """Comprehensive database engine enumeration (50+ types)"""
    
    # === RELATIONAL SQL DATABASES ===
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQL_SERVER = "sql_server"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    MARIADB = "mariadb"
    DB2 = "db2"
    SYBASE = "sybase"
    FIREBIRD = "firebird"
    HSQLDB = "hsqldb"
    H2 = "h2"
    DERBY = "derby"
    INFORMIX = "informix"
    INGRES = "ingres"
    MONETDB = "monetdb"
    CUBRID = "cubrid"
    MAXDB = "maxdb"
    
    # === DATA WAREHOUSE & ANALYTICS ===
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    TERADATA = "teradata"
    VERTICA = "vertica"
    GREENPLUM = "greenplum"
    NETEZZA = "netezza"
    EXADATA = "exadata"
    AZURE_SYNAPSE = "azure_synapse"
    DATABRICKS = "databricks"
    
    # === CLOUD DATABASES ===
    AZURE_SQL = "azure_sql"
    AWS_RDS = "aws_rds"
    GOOGLE_CLOUD_SQL = "google_cloud_sql"
    AMAZON_AURORA = "amazon_aurora"
    PLANETSCALE = "planetscale"
    NEON = "neon"
    SUPABASE = "supabase"
    COCKROACHDB = "cockroachdb"
    YUGABYTEDB = "yugabytedb"
    TIDB = "tidb"
    VITESS = "vitess"
    SPANNER = "spanner"
    FAUNA = "fauna"
    XATA = "xata"
    RAILWAY = "railway"
    
    # === NOSQL DOCUMENT DATABASES ===
    MONGODB = "mongodb"
    COUCHDB = "couchdb"
    COUCHBASE = "couchbase"
    AMAZON_DOCUMENTDB = "amazon_documentdb"
    AZURE_COSMOS_DB = "azure_cosmos_db"
    ORIENTDB = "orientdb"
    RETHINKDB = "rethinkdb"
    
    # === NOSQL KEY-VALUE STORES ===
    REDIS = "redis"
    MEMCACHED = "memcached"
    AMAZON_DYNAMODB = "amazon_dynamodb"
    AZURE_TABLE_STORAGE = "azure_table_storage"
    RIAK = "riak"
    VOLDEMORT = "voldemort"
    
    # === NOSQL COLUMN-FAMILY ===
    CASSANDRA = "cassandra"
    HBASE = "hbase"
    AMAZON_SIMPLEDB = "amazon_simpledb"
    HYPERTABLE = "hypertable"
    
    # === GRAPH DATABASES ===
    NEO4J = "neo4j"
    AMAZON_NEPTUNE = "amazon_neptune"
    ARANGODB = "arangodb"
    ORIENTDB_GRAPH = "orientdb_graph"
    JANUSGRAPH = "janusgraph"
    DGRAPH = "dgraph"
    
    # === TIME SERIES DATABASES ===
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    PROMETHEUS = "prometheus"
    OPENTSDB = "opentsdb"
    KAIROSDB = "kairosdb"
    
    # === SEARCH ENGINES ===
    ELASTICSEARCH = "elasticsearch"
    SOLR = "solr"
    SPHINX = "sphinx"
    AMAZON_CLOUDSEARCH = "amazon_cloudsearch"
    
    # === SPECIALIZED DATABASES ===
    SAP_HANA = "sap_hana"
    CLICKHOUSE = "clickhouse"
    DRUID = "druid"
    PINOT = "pinot"
    PRESTO = "presto"
    TRINO = "trino"
    SPARK_SQL = "spark_sql"
    DUCKDB = "duckdb"

    # === ADDITIONAL DATABASES ===
    BERKELEYDB = "berkeleydb"
    LEVELDB = "leveldb"
    ROCKSDB = "rocksdb"
    INTERBASE = "interbase"
    PARADOX = "paradox"
    DBASE = "dbase"
    FOXPRO = "foxpro"
    ACCESS = "access"
    IMS = "ims"
    ADABAS = "adabas"
    IDMS = "idms"
    KYLIN = "kylin"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    CHROMA = "chroma"
    WEAVIATE = "weaviate"
    PINECONE = "pinecone"
    HIVE = "hive"

    # === AUTO DETECTION ===
    AUTO_DETECT = "auto_detect"
    UNKNOWN = "unknown"

@dataclass
class DatabaseFeatures:
    """Database-specific features and capabilities"""
    supports_transactions: bool = True
    supports_joins: bool = True
    supports_subqueries: bool = True
    supports_window_functions: bool = False
    supports_cte: bool = False
    supports_json: bool = False
    supports_arrays: bool = False
    supports_stored_procedures: bool = True
    supports_triggers: bool = True
    supports_views: bool = True
    supports_indexes: bool = True
    case_sensitive: bool = False
    quote_character: str = '"'
    escape_character: str = '\\'
    comment_styles: List[str] = None
    max_identifier_length: int = 64
    reserved_words: List[str] = None

@dataclass
class DatabaseInfo:
    """Complete database information"""
    engine: DatabaseEngine
    name: str
    category: DatabaseCategory
    vendor: str
    description: str
    features: DatabaseFeatures
    syntax_patterns: List[str]
    connection_patterns: List[str]
    file_extensions: List[str]
    default_port: Optional[int] = None
    documentation_url: str = ""
    is_open_source: bool = True
    license_type: str = ""

class DatabaseRegistry:
    """Registry of all supported database engines"""
    
    def __init__(self):
        self.databases = self._initialize_database_registry()
        logger.info(f"DatabaseRegistry initialized with {len(self.databases)} database engines")
    
    def get_database_info(self, engine: DatabaseEngine) -> Optional[DatabaseInfo]:
        """Get database information by engine"""
        return self.databases.get(engine)
    
    def detect_database_engine(self, content: str, connection_string: str = "") -> DatabaseEngine:
        """Auto-detect database engine from content and connection string"""
        content_upper = content.upper()
        
        # Check connection string first
        if connection_string:
            for engine, info in self.databases.items():
                for pattern in info.connection_patterns:
                    if re.search(pattern, connection_string, re.IGNORECASE):
                        logger.info(f"Database detected from connection string: {engine.value}")
                        return engine
        
        # Check syntax patterns
        engine_scores = {}
        for engine, info in self.databases.items():
            score = 0
            for pattern in info.syntax_patterns:
                matches = len(re.findall(pattern, content_upper))
                score += matches
            engine_scores[engine] = score
        
        # Return engine with highest score
        if engine_scores:
            detected_engine = max(engine_scores, key=engine_scores.get)
            if engine_scores[detected_engine] > 0:
                logger.info(f"Database detected from syntax: {detected_engine.value}")
                return detected_engine
        
        # Default fallback
        logger.info("Database detection failed, defaulting to MySQL")
        return DatabaseEngine.MYSQL
    
    def get_supported_engines(self, category: DatabaseCategory = None) -> List[DatabaseEngine]:
        """Get list of supported engines, optionally filtered by category"""
        if category:
            return [engine for engine, info in self.databases.items() 
                   if info.category == category]
        return list(self.databases.keys())
    
    def get_database_categories(self) -> List[DatabaseCategory]:
        """Get all database categories"""
        return list(DatabaseCategory)

# Global registry instance
database_registry = DatabaseRegistry()
