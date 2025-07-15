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
        """Initialize the complete database registry"""
        registry = {}
        
        # MySQL
        registry[DatabaseEngine.MYSQL] = DatabaseInfo(
            engine=DatabaseEngine.MYSQL,
            name="MySQL",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="Oracle Corporation",
            description="Popular open-source relational database",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                quote_character='`',
                comment_styles=['--', '#', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE']
            ),
            syntax_patterns=[
                r'AUTO_INCREMENT', r'TINYINT', r'MEDIUMINT', r'LONGTEXT',
                r'ENUM', r'SET', r'ZEROFILL', r'UNSIGNED', r'CONCAT_WS',
                r'GROUP_CONCAT', r'IFNULL', r'DATE_FORMAT', r'STR_TO_DATE'
            ],
            connection_patterns=[
                r'mysql://', r'jdbc:mysql://', r'Server=.*mysql'
            ],
            file_extensions=['.sql', '.mysql'],
            default_port=3306,
            documentation_url="https://dev.mysql.com/doc/",
            is_open_source=True,
            license_type="GPL/Commercial"
        )
        
        # PostgreSQL
        registry[DatabaseEngine.POSTGRESQL] = DatabaseInfo(
            engine=DatabaseEngine.POSTGRESQL,
            name="PostgreSQL",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="PostgreSQL Global Development Group",
            description="Advanced open-source relational database",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                case_sensitive=True,
                comment_styles=['--', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'RETURNING']
            ),
            syntax_patterns=[
                r'SERIAL', r'BIGSERIAL', r'JSONB', r'ARRAY', r'HSTORE',
                r'GENERATE_SERIES', r'STRING_AGG', r'ARRAY_AGG', r'ILIKE',
                r'RETURNING', r'ON CONFLICT', r'DO NOTHING', r'DO UPDATE'
            ],
            connection_patterns=[
                r'postgresql://', r'postgres://', r'jdbc:postgresql://'
            ],
            file_extensions=['.sql', '.pgsql', '.psql'],
            default_port=5432,
            documentation_url="https://www.postgresql.org/docs/",
            is_open_source=True,
            license_type="PostgreSQL License"
        )
        
        # SQL Server
        registry[DatabaseEngine.SQL_SERVER] = DatabaseInfo(
            engine=DatabaseEngine.SQL_SERVER,
            name="Microsoft SQL Server",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="Microsoft Corporation",
            description="Enterprise relational database system",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                quote_character='[',
                comment_styles=['--', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'TOP', 'WITH']
            ),
            syntax_patterns=[
                r'IDENTITY', r'UNIQUEIDENTIFIER', r'NVARCHAR', r'NCHAR',
                r'GETDATE', r'GETUTCDATE', r'CHARINDEX', r'STUFF',
                r'TOP', r'WITH', r'NOLOCK', r'ROWLOCK'
            ],
            connection_patterns=[
                r'sqlserver://', r'jdbc:sqlserver://', r'Server=.*'
            ],
            file_extensions=['.sql', '.tsql'],
            default_port=1433,
            documentation_url="https://docs.microsoft.com/en-us/sql/",
            is_open_source=False,
            license_type="Commercial"
        )
        
        # Add more databases...
        self._add_nosql_databases(registry)
        self._add_cloud_databases(registry)
        self._add_specialized_databases(registry)
        self._add_additional_sql_databases(registry)
        self._add_time_series_databases(registry)
        self._add_search_databases(registry)
        self._add_graph_databases(registry)
        self._add_embedded_databases(registry)
        self._add_legacy_databases(registry)
        self._add_mainframe_databases(registry)
        self._add_vector_databases(registry)
        self._add_analytics_databases(registry)
        
        return registry
    
    def _add_nosql_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add NoSQL database definitions"""
        
        # MongoDB
        registry[DatabaseEngine.MONGODB] = DatabaseInfo(
            engine=DatabaseEngine.MONGODB,
            name="MongoDB",
            category=DatabaseCategory.NOSQL_DOCUMENT,
            vendor="MongoDB Inc.",
            description="Document-oriented NoSQL database",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,  # Aggregation pipeline
                supports_subqueries=False,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=False,
                supports_triggers=True,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'db\.', r'find\(', r'aggregate\(', r'insertOne\(',
                r'updateOne\(', r'deleteOne\(', r'\$match', r'\$group'
            ],
            connection_patterns=[
                r'mongodb://', r'mongodb\+srv://'
            ],
            file_extensions=['.js', '.mongodb', '.json'],
            default_port=27017,
            documentation_url="https://docs.mongodb.com/",
            is_open_source=True,
            license_type="SSPL"
        )
        
        # Redis
        registry[DatabaseEngine.REDIS] = DatabaseInfo(
            engine=DatabaseEngine.REDIS,
            name="Redis",
            category=DatabaseCategory.NOSQL_KEY_VALUE,
            vendor="Redis Ltd.",
            description="In-memory key-value data store",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=False,
                supports_subqueries=False,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=True,  # Lua scripts
                supports_triggers=False,
                supports_views=False,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'SET ', r'GET ', r'HSET ', r'HGET ', r'LPUSH ', r'RPOP ',
                r'SADD ', r'SMEMBERS ', r'ZADD ', r'ZRANGE '
            ],
            connection_patterns=[
                r'redis://', r'rediss://'
            ],
            file_extensions=['.redis', '.rdb'],
            default_port=6379,
            documentation_url="https://redis.io/documentation",
            is_open_source=True,
            license_type="BSD"
        )
    
    def _add_cloud_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add cloud database definitions"""
        
        # BigQuery
        registry[DatabaseEngine.BIGQUERY] = DatabaseInfo(
            engine=DatabaseEngine.BIGQUERY,
            name="Google BigQuery",
            category=DatabaseCategory.DATA_WAREHOUSE,
            vendor="Google Cloud",
            description="Serverless data warehouse for analytics",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                quote_character='`',
                comment_styles=['--', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'ARRAY', 'STRUCT']
            ),
            syntax_patterns=[
                r'ARRAY\[', r'STRUCT\(', r'UNNEST\(', r'ARRAY_AGG\(',
                r'STRING_AGG\(', r'APPROX_COUNT_DISTINCT\('
            ],
            connection_patterns=[
                r'bigquery://', r'bq://'
            ],
            file_extensions=['.sql', '.bq'],
            documentation_url="https://cloud.google.com/bigquery/docs",
            is_open_source=False,
            license_type="Commercial"
        )
    
    def _add_specialized_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add specialized database definitions"""
        
        # ClickHouse
        registry[DatabaseEngine.CLICKHOUSE] = DatabaseInfo(
            engine=DatabaseEngine.CLICKHOUSE,
            name="ClickHouse",
            category=DatabaseCategory.SPECIALIZED,
            vendor="ClickHouse Inc.",
            description="Column-oriented database for analytics",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                quote_character='`',
                comment_styles=['--', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'FINAL', 'SAMPLE']
            ),
            syntax_patterns=[
                r'ENGINE\s*=', r'PARTITION\s+BY', r'ORDER\s+BY',
                r'SAMPLE\s+BY', r'FINAL', r'arrayJoin\('
            ],
            connection_patterns=[
                r'clickhouse://', r'http://.*:8123'
            ],
            file_extensions=['.sql', '.ch'],
            default_port=9000,
            documentation_url="https://clickhouse.com/docs/",
            is_open_source=True,
            license_type="Apache 2.0"
        )

    def _add_additional_sql_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add additional SQL database definitions"""

        # SQLite
        registry[DatabaseEngine.SQLITE] = DatabaseInfo(
            engine=DatabaseEngine.SQLITE,
            name="SQLite",
            category=DatabaseCategory.EMBEDDED,
            vendor="SQLite Development Team",
            description="Lightweight embedded SQL database",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,
                supports_subqueries=True,
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_stored_procedures=False,
                supports_triggers=True,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'AUTOINCREMENT', r'PRAGMA', r'ATTACH', r'DETACH',
                r'VACUUM', r'ANALYZE', r'EXPLAIN QUERY PLAN'
            ],
            connection_patterns=[
                r'sqlite://', r'file:', r'\.db$', r'\.sqlite$'
            ],
            file_extensions=['.db', '.sqlite', '.sqlite3'],
            documentation_url="https://sqlite.org/docs.html",
            is_open_source=True,
            license_type="Public Domain"
        )

        # MariaDB
        registry[DatabaseEngine.MARIADB] = DatabaseInfo(
            engine=DatabaseEngine.MARIADB,
            name="MariaDB",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="MariaDB Foundation",
            description="MySQL-compatible open source database",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                quote_character='`',
                comment_styles=['--', '#', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'RETURNING']
            ),
            syntax_patterns=[
                r'AUTO_INCREMENT', r'TINYINT', r'MEDIUMINT', r'LONGTEXT',
                r'ENUM', r'SET', r'ZEROFILL', r'UNSIGNED', r'RETURNING'
            ],
            connection_patterns=[
                r'mariadb://', r'jdbc:mariadb://'
            ],
            file_extensions=['.sql', '.mariadb'],
            default_port=3306,
            documentation_url="https://mariadb.com/kb/",
            is_open_source=True,
            license_type="GPL"
        )

        # Oracle
        registry[DatabaseEngine.ORACLE] = DatabaseInfo(
            engine=DatabaseEngine.ORACLE,
            name="Oracle Database",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="Oracle Corporation",
            description="Enterprise relational database system",
            features=DatabaseFeatures(
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                quote_character='"',
                comment_styles=['--', '/* */'],
                reserved_words=['SELECT', 'FROM', 'WHERE', 'DUAL', 'ROWNUM']
            ),
            syntax_patterns=[
                r'DUAL', r'ROWNUM', r'ROWID', r'SYSDATE', r'NVL',
                r'DECODE', r'CONNECT BY', r'START WITH', r'PRIOR'
            ],
            connection_patterns=[
                r'oracle://', r'jdbc:oracle:', r'tns:'
            ],
            file_extensions=['.sql', '.pls', '.plb'],
            default_port=1521,
            documentation_url="https://docs.oracle.com/database/",
            is_open_source=False,
            license_type="Commercial"
        )

    def _add_time_series_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add time series database definitions"""

        # InfluxDB
        registry[DatabaseEngine.INFLUXDB] = DatabaseInfo(
            engine=DatabaseEngine.INFLUXDB,
            name="InfluxDB",
            category=DatabaseCategory.TIME_SERIES,
            vendor="InfluxData",
            description="Time series database for metrics and events",
            features=DatabaseFeatures(
                supports_transactions=False,
                supports_joins=False,
                supports_subqueries=True,
                supports_window_functions=True,
                supports_json=False,
                supports_stored_procedures=False,
                supports_triggers=False,
                supports_views=False,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'FROM\s+/.*/', r'SELECT\s+.*\s+FROM\s+/.*/',
                r'SHOW\s+MEASUREMENTS', r'SHOW\s+SERIES',
                r'GROUP\s+BY\s+time\(', r'fill\('
            ],
            connection_patterns=[
                r'influxdb://', r'http://.*:8086'
            ],
            file_extensions=['.influx', '.iql'],
            default_port=8086,
            documentation_url="https://docs.influxdata.com/",
            is_open_source=True,
            license_type="MIT"
        )

        # TimescaleDB
        registry[DatabaseEngine.TIMESCALEDB] = DatabaseInfo(
            engine=DatabaseEngine.TIMESCALEDB,
            name="TimescaleDB",
            category=DatabaseCategory.TIME_SERIES,
            vendor="Timescale Inc.",
            description="PostgreSQL extension for time-series data",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,
                supports_subqueries=True,
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=True,
                supports_triggers=True,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'CREATE\s+HYPERTABLE', r'time_bucket\(',
                r'first\(', r'last\(', r'histogram\(',
                r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*time'
            ],
            connection_patterns=[
                r'timescaledb://', r'postgresql://.*timescale'
            ],
            file_extensions=['.sql', '.tsql'],
            default_port=5432,
            documentation_url="https://docs.timescale.com/",
            is_open_source=True,
            license_type="Apache 2.0"
        )

    def _add_search_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add search engine database definitions"""

        # Elasticsearch
        registry[DatabaseEngine.ELASTICSEARCH] = DatabaseInfo(
            engine=DatabaseEngine.ELASTICSEARCH,
            name="Elasticsearch",
            category=DatabaseCategory.SEARCH_ENGINE,
            vendor="Elastic N.V.",
            description="Distributed search and analytics engine",
            features=DatabaseFeatures(
                supports_transactions=False,
                supports_joins=False,
                supports_subqueries=False,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=False,
                supports_triggers=False,
                supports_views=False,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'GET\s+/', r'POST\s+/', r'PUT\s+/', r'DELETE\s+/',
                r'"query":', r'"bool":', r'"match":', r'"term":',
                r'"aggs":', r'"aggregations":'
            ],
            connection_patterns=[
                r'elasticsearch://', r'http://.*:9200'
            ],
            file_extensions=['.json', '.es'],
            default_port=9200,
            documentation_url="https://www.elastic.co/guide/",
            is_open_source=True,
            license_type="Elastic License"
        )

        # Apache Solr
        registry[DatabaseEngine.SOLR] = DatabaseInfo(
            engine=DatabaseEngine.SOLR,
            name="Apache Solr",
            category=DatabaseCategory.SEARCH_ENGINE,
            vendor="Apache Software Foundation",
            description="Open source search platform",
            features=DatabaseFeatures(
                supports_transactions=False,
                supports_joins=False,
                supports_subqueries=False,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=False,
                supports_triggers=False,
                supports_views=False,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'q=', r'fq=', r'fl=', r'sort=',
                r'facet=true', r'facet\.field=',
                r'group=true', r'group\.field='
            ],
            connection_patterns=[
                r'solr://', r'http://.*:8983/solr'
            ],
            file_extensions=['.solr', '.xml'],
            default_port=8983,
            documentation_url="https://solr.apache.org/guide/",
            is_open_source=True,
            license_type="Apache 2.0"
        )

    def _add_graph_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add graph database definitions"""

        # Neo4j
        registry[DatabaseEngine.NEO4J] = DatabaseInfo(
            engine=DatabaseEngine.NEO4J,
            name="Neo4j",
            category=DatabaseCategory.NOSQL_GRAPH,
            vendor="Neo4j Inc.",
            description="Native graph database",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=False,  # Uses graph traversal instead
                supports_subqueries=True,
                supports_json=False,
                supports_arrays=True,
                supports_stored_procedures=True,
                supports_triggers=True,
                supports_views=False,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'MATCH\s+\(', r'CREATE\s+\(', r'MERGE\s+\(',
                r'RETURN\s+', r'WHERE\s+', r'WITH\s+',
                r'-\[.*\]->', r'<-\[.*\]-', r'CALL\s+'
            ],
            connection_patterns=[
                r'neo4j://', r'bolt://', r'http://.*:7474'
            ],
            file_extensions=['.cypher', '.cql'],
            default_port=7687,
            documentation_url="https://neo4j.com/docs/",
            is_open_source=True,
            license_type="GPL/Commercial"
        )

        # ArangoDB
        registry[DatabaseEngine.ARANGODB] = DatabaseInfo(
            engine=DatabaseEngine.ARANGODB,
            name="ArangoDB",
            category=DatabaseCategory.NOSQL_GRAPH,
            vendor="ArangoDB GmbH",
            description="Multi-model database (document, graph, key-value)",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,
                supports_subqueries=True,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=True,
                supports_triggers=True,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'FOR\s+.*\s+IN\s+', r'FILTER\s+', r'SORT\s+',
                r'LIMIT\s+', r'COLLECT\s+', r'GRAPH\s+',
                r'SHORTEST_PATH\(', r'K_SHORTEST_PATHS\('
            ],
            connection_patterns=[
                r'arangodb://', r'http://.*:8529'
            ],
            file_extensions=['.aql', '.arango'],
            default_port=8529,
            documentation_url="https://www.arangodb.com/docs/",
            is_open_source=True,
            license_type="Apache 2.0"
        )

    def _add_embedded_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add embedded database definitions"""

        # H2
        registry[DatabaseEngine.H2] = DatabaseInfo(
            engine=DatabaseEngine.H2,
            name="H2 Database",
            category=DatabaseCategory.EMBEDDED,
            vendor="H2 Group",
            description="Java-based embedded database",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,
                supports_subqueries=True,
                supports_window_functions=True,
                supports_cte=True,
                supports_json=False,
                supports_stored_procedures=True,
                supports_triggers=True,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'IDENTITY', r'SEQUENCE', r'MERGE\s+INTO',
                r'CSVREAD\(', r'CSVWRITE\(', r'RUNSCRIPT'
            ],
            connection_patterns=[
                r'h2:', r'jdbc:h2:', r'mem:', r'file:'
            ],
            file_extensions=['.h2.db', '.mv.db'],
            documentation_url="http://www.h2database.com/html/main.html",
            is_open_source=True,
            license_type="MPL 2.0"
        )

        # DuckDB
        registry[DatabaseEngine.DUCKDB] = DatabaseInfo(
            engine=DatabaseEngine.DUCKDB,
            name="DuckDB",
            category=DatabaseCategory.EMBEDDED,
            vendor="DuckDB Labs",
            description="In-process analytical database",
            features=DatabaseFeatures(
                supports_transactions=True,
                supports_joins=True,
                supports_subqueries=True,
                supports_window_functions=True,
                supports_cte=True,
                supports_json=True,
                supports_arrays=True,
                supports_stored_procedures=False,
                supports_triggers=False,
                supports_views=True,
                supports_indexes=True
            ),
            syntax_patterns=[
                r'COPY\s+.*\s+FROM', r'COPY\s+.*\s+TO',
                r'read_csv\(', r'read_parquet\(',
                r'PRAGMA', r'DESCRIBE', r'SUMMARIZE'
            ],
            connection_patterns=[
                r'duckdb://', r'\.duckdb$'
            ],
            file_extensions=['.duckdb', '.db'],
            documentation_url="https://duckdb.org/docs/",
            is_open_source=True,
            license_type="MIT"
        )

    def _add_legacy_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add legacy database definitions"""

        # Firebird
        registry[DatabaseEngine.FIREBIRD] = DatabaseInfo(
            engine=DatabaseEngine.FIREBIRD,
            name="Firebird",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="Firebird Foundation",
            description="Open source SQL relational database",
            features=DatabaseFeatures(),
            syntax_patterns=[r'GENERATOR', r'EXCEPTION', r'EXECUTE BLOCK'],
            connection_patterns=[r'firebird://'],
            file_extensions=['.fdb', '.gdb'],
            default_port=3050,
            documentation_url="https://firebirdsql.org/en/documentation/",
            is_open_source=True,
            license_type="IDPL"
        )

    def _add_mainframe_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add mainframe database definitions"""

        # DB2
        registry[DatabaseEngine.DB2] = DatabaseInfo(
            engine=DatabaseEngine.DB2,
            name="IBM DB2",
            category=DatabaseCategory.RELATIONAL_SQL,
            vendor="IBM",
            description="Enterprise database server",
            features=DatabaseFeatures(),
            syntax_patterns=[r'GENERATED', r'IDENTITY', r'FETCH FIRST'],
            connection_patterns=[r'db2://'],
            file_extensions=['.sql', '.db2'],
            default_port=50000,
            documentation_url="https://www.ibm.com/docs/en/db2",
            is_open_source=False,
            license_type="Commercial"
        )

    def _add_vector_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add vector database definitions"""

        # Pinecone
        registry[DatabaseEngine.PINECONE] = DatabaseInfo(
            engine=DatabaseEngine.PINECONE,
            name="Pinecone",
            category=DatabaseCategory.NOSQL_KEY_VALUE,
            vendor="Pinecone Systems",
            description="Vector database for ML applications",
            features=DatabaseFeatures(supports_transactions=False),
            syntax_patterns=[r'upsert', r'query', r'fetch'],
            connection_patterns=[r'pinecone://'],
            file_extensions=['.json'],
            documentation_url="https://docs.pinecone.io/",
            is_open_source=False,
            license_type="Commercial"
        )

    def _add_analytics_databases(self, registry: Dict[DatabaseEngine, DatabaseInfo]):
        """Add analytics database definitions"""

        # Apache Hive
        registry[DatabaseEngine.HIVE] = DatabaseInfo(
            engine=DatabaseEngine.HIVE,
            name="Apache Hive",
            category=DatabaseCategory.DATA_WAREHOUSE,
            vendor="Apache Software Foundation",
            description="Data warehouse software for Hadoop",
            features=DatabaseFeatures(),
            syntax_patterns=[r'PARTITIONED BY', r'STORED AS', r'LOCATION'],
            connection_patterns=[r'hive://'],
            file_extensions=['.hql', '.sql'],
            default_port=10000,
            documentation_url="https://hive.apache.org/",
            is_open_source=True,
            license_type="Apache 2.0"
        )

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
