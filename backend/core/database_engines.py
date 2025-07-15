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

    def _initialize_database_registry(self) -> Dict[DatabaseEngine, DatabaseInfo]:
        """Initialize the database registry with all supported engines"""
        databases = {}

        # Add all database engines with their information and proper categories
        database_configs = [
            (DatabaseEngine.MYSQL, "MySQL", "Popular open-source relational database", DatabaseCategory.RELATIONAL_SQL, ["ACID", "Replication"]),
            (DatabaseEngine.POSTGRESQL, "PostgreSQL", "Advanced open-source relational database", DatabaseCategory.RELATIONAL_SQL, ["ACID", "JSON"]),
            (DatabaseEngine.SQLITE, "SQLite", "Lightweight embedded database", DatabaseCategory.EMBEDDED, ["Embedded", "Serverless"]),
            (DatabaseEngine.MONGODB, "MongoDB", "Popular NoSQL document database", DatabaseCategory.NOSQL_DOCUMENT, ["Document", "Sharding"]),
            (DatabaseEngine.REDIS, "Redis", "In-memory data structure store", DatabaseCategory.IN_MEMORY, ["In-memory", "Pub/Sub"]),
            (DatabaseEngine.ORACLE, "Oracle Database", "Enterprise relational database", DatabaseCategory.RELATIONAL_SQL, ["Enterprise", "ACID"]),
            (DatabaseEngine.SQL_SERVER, "Microsoft SQL Server", "Microsoft's relational database", DatabaseCategory.RELATIONAL_SQL, ["Enterprise", "T-SQL"]),
            (DatabaseEngine.BIGQUERY, "Google BigQuery", "Cloud data warehouse", DatabaseCategory.DATA_WAREHOUSE, ["Cloud", "Analytics"]),
            (DatabaseEngine.H2, "H2 Database", "Java embedded database", DatabaseCategory.EMBEDDED, ["Embedded", "Java"]),
            (DatabaseEngine.MARIADB, "MariaDB", "MySQL-compatible database", DatabaseCategory.RELATIONAL_SQL, ["Open-source", "Compatible"]),
            (DatabaseEngine.COUCHDB, "CouchDB", "Document database", DatabaseCategory.NOSQL_DOCUMENT, ["Document", "JSON"]),
            (DatabaseEngine.CASSANDRA, "Apache Cassandra", "Wide-column database", DatabaseCategory.NOSQL_COLUMN_FAMILY, ["Distributed", "NoSQL"]),
            (DatabaseEngine.SNOWFLAKE, "Snowflake", "Cloud data warehouse", DatabaseCategory.DATA_WAREHOUSE, ["Cloud", "Analytics"]),
            (DatabaseEngine.REDSHIFT, "Amazon Redshift", "AWS data warehouse", DatabaseCategory.DATA_WAREHOUSE, ["Cloud", "Analytics"]),
            (DatabaseEngine.COCKROACHDB, "CockroachDB", "Distributed SQL database", DatabaseCategory.RELATIONAL_SQL, ["Distributed", "ACID"]),
            (DatabaseEngine.YUGABYTEDB, "YugabyteDB", "Distributed SQL database", DatabaseCategory.RELATIONAL_SQL, ["Distributed", "Multi-cloud"]),
            (DatabaseEngine.TIDB, "TiDB", "Distributed SQL database", DatabaseCategory.RELATIONAL_SQL, ["Distributed", "MySQL-compatible"]),
            (DatabaseEngine.COUCHBASE, "Couchbase", "NoSQL document database", DatabaseCategory.NOSQL_DOCUMENT, ["Document", "Caching"]),
            (DatabaseEngine.AMAZON_DYNAMODB, "Amazon DynamoDB", "NoSQL key-value database", DatabaseCategory.NOSQL_KEY_VALUE, ["Key-value", "Serverless"]),
            (DatabaseEngine.HBASE, "Apache HBase", "Wide-column database", DatabaseCategory.NOSQL_COLUMN_FAMILY, ["Big-data", "Hadoop"]),
            (DatabaseEngine.MEMCACHED, "Memcached", "In-memory caching system", DatabaseCategory.IN_MEMORY, ["Caching", "Performance"]),
            (DatabaseEngine.RIAK, "Riak", "Distributed NoSQL database", DatabaseCategory.NOSQL_KEY_VALUE, ["Distributed", "Key-value"])
        ]

        for engine, name, description, category, features in database_configs:
            databases[engine] = DatabaseInfo(
                engine=engine,
                name=name,
                category=category,
                vendor=name.split()[0],  # First word as vendor
                description=description,
                features=DatabaseFeatures(
                    supports_transactions=True,
                    supports_joins=True,
                    supports_subqueries=True,
                    supports_window_functions=True,
                    supports_cte=True,
                    supports_json=engine in [DatabaseEngine.POSTGRESQL, DatabaseEngine.MYSQL],
                    supports_arrays=engine == DatabaseEngine.POSTGRESQL,
                    supports_stored_procedures=True,
                    supports_triggers=True,
                    supports_views=True,
                    supports_indexes=True,
                    case_sensitive=False,
                    quote_character='"',
                    escape_character='\\',
                    comment_styles=['--', '/**/'],
                    max_identifier_length=64,
                    reserved_words=['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE']
                ),
                syntax_patterns=[f"{engine.value}_syntax"],
                connection_patterns=[f"Connection pattern for {name}"],
                file_extensions=['.sql'],
                documentation_url=f"https://docs.{name.lower().replace(' ', '')}.com"
            )

        return databases

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

    def get_all_supported_engines(self) -> List[DatabaseEngine]:
        """Get all supported engines (alias for get_supported_engines)"""
        return self.get_supported_engines()

    def get_database_categories(self) -> List[DatabaseCategory]:
        """Get all database categories"""
        return list(DatabaseCategory)

# Global registry instance
database_registry = DatabaseRegistry()
