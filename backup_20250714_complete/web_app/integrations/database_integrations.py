#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - DATABASE INTEGRATIONS
Comprehensive database tool integrations and connectivity
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
import pymongo
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class DatabaseType(Enum):
    """Supported database types."""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    MONGODB = "mongodb"

@dataclass
class DatabaseConnection:
    """Database connection configuration."""
    name: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_string: str = ""
    is_active: bool = True

class DatabaseIntegrationManager:
    """Manage database connections and integrations."""
    
    def __init__(self, config_dir: str = "web_app/integrations"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.connections = {}
        self.active_engines = {}
        
        self.setup_logging()
        self.load_connections()
    
    def setup_logging(self):
        """Setup integration logging."""
        log_file = self.config_dir / "integrations.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_connections(self):
        """Load database connections from configuration."""
        config_file = self.config_dir / "database_connections.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                connections_data = json.load(f)
                
                for conn_id, conn_data in connections_data.items():
                    conn_data['db_type'] = DatabaseType(conn_data['db_type'])
                    self.connections[conn_id] = DatabaseConnection(**conn_data)
        else:
            # Create default SQLite connection
            self.add_connection(
                name="Default SQLite",
                db_type=DatabaseType.SQLITE,
                host="localhost",
                port=0,
                database="sql_analyzer.db",
                username="",
                password=""
            )
    
    def save_connections(self):
        """Save database connections to configuration."""
        config_file = self.config_dir / "database_connections.json"
        
        connections_data = {}
        for conn_id, conn in self.connections.items():
            conn_dict = {
                'name': conn.name,
                'db_type': conn.db_type.value,
                'host': conn.host,
                'port': conn.port,
                'database': conn.database,
                'username': conn.username,
                'password': conn.password,  # In production, encrypt this
                'connection_string': conn.connection_string,
                'is_active': conn.is_active
            }
            connections_data[conn_id] = conn_dict
        
        with open(config_file, 'w') as f:
            json.dump(connections_data, f, indent=2)
    
    def add_connection(self, name: str, db_type: DatabaseType, host: str, port: int,
                      database: str, username: str, password: str) -> str:
        """Add new database connection."""
        conn_id = f"{db_type.value}_{len(self.connections) + 1}"
        
        # Build connection string
        connection_string = self._build_connection_string(db_type, host, port, database, username, password)
        
        connection = DatabaseConnection(
            name=name,
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            connection_string=connection_string
        )
        
        self.connections[conn_id] = connection
        self.save_connections()
        
        self.logger.info(f"Database connection added: {name} ({db_type.value})")
        return conn_id
    
    def _build_connection_string(self, db_type: DatabaseType, host: str, port: int,
                                database: str, username: str, password: str) -> str:
        """Build database connection string."""
        if db_type == DatabaseType.MYSQL:
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == DatabaseType.SQLITE:
            return f"sqlite:///{database}"
        elif db_type == DatabaseType.SQLSERVER:
            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
        elif db_type == DatabaseType.ORACLE:
            return f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
        else:
            return ""
    
    def test_connection(self, conn_id: str) -> Tuple[bool, str]:
        """Test database connection."""
        if conn_id not in self.connections:
            return False, "Connection not found"
        
        connection = self.connections[conn_id]
        
        try:
            if connection.db_type == DatabaseType.MONGODB:
                return self._test_mongodb_connection(connection)
            else:
                return self._test_sql_connection(connection)
        except Exception as e:
            self.logger.error(f"Connection test failed for {connection.name}: {e}")
            return False, str(e)
    
    def _test_sql_connection(self, connection: DatabaseConnection) -> Tuple[bool, str]:
        """Test SQL database connection."""
        try:
            engine = create_engine(connection.connection_string, echo=False)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self.logger.info(f"SQL connection test successful: {connection.name}")
            return True, "Connection successful"
            
        except SQLAlchemyError as e:
            return False, f"SQL connection failed: {str(e)}"
    
    def _test_mongodb_connection(self, connection: DatabaseConnection) -> Tuple[bool, str]:
        """Test MongoDB connection."""
        try:
            client = pymongo.MongoClient(
                host=connection.host,
                port=connection.port,
                username=connection.username,
                password=connection.password,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            client.server_info()
            
            self.logger.info(f"MongoDB connection test successful: {connection.name}")
            return True, "MongoDB connection successful"
            
        except pymongo.errors.ServerSelectionTimeoutError:
            return False, "MongoDB connection timeout"
        except Exception as e:
            return False, f"MongoDB connection failed: {str(e)}"
    
    def execute_query(self, conn_id: str, query: str) -> Tuple[bool, Any]:
        """Execute query on specified database."""
        if conn_id not in self.connections:
            return False, "Connection not found"
        
        connection = self.connections[conn_id]
        
        try:
            if connection.db_type == DatabaseType.MONGODB:
                return self._execute_mongodb_query(connection, query)
            else:
                return self._execute_sql_query(connection, query)
        except Exception as e:
            self.logger.error(f"Query execution failed on {connection.name}: {e}")
            return False, str(e)
    
    def _execute_sql_query(self, connection: DatabaseConnection, query: str) -> Tuple[bool, Any]:
        """Execute SQL query."""
        try:
            engine = create_engine(connection.connection_string, echo=False)
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    
                    return True, {
                        'columns': list(columns),
                        'data': data,
                        'row_count': len(data)
                    }
                else:
                    return True, {
                        'message': 'Query executed successfully',
                        'rows_affected': result.rowcount
                    }
                    
        except SQLAlchemyError as e:
            return False, f"SQL execution failed: {str(e)}"
    
    def _execute_mongodb_query(self, connection: DatabaseConnection, query: str) -> Tuple[bool, Any]:
        """Execute MongoDB query."""
        try:
            client = pymongo.MongoClient(
                host=connection.host,
                port=connection.port,
                username=connection.username,
                password=connection.password
            )
            
            db = client[connection.database]
            
            # Parse MongoDB query (simplified)
            # In production, implement proper MongoDB query parsing
            query_data = json.loads(query)
            collection_name = query_data.get('collection')
            operation = query_data.get('operation', 'find')
            params = query_data.get('params', {})
            
            collection = db[collection_name]
            
            if operation == 'find':
                cursor = collection.find(params.get('filter', {}))
                if 'limit' in params:
                    cursor = cursor.limit(params['limit'])
                
                results = list(cursor)
                
                return True, {
                    'data': results,
                    'count': len(results)
                }
            else:
                return False, f"Unsupported MongoDB operation: {operation}"
                
        except Exception as e:
            return False, f"MongoDB execution failed: {str(e)}"
    
    def get_database_schema(self, conn_id: str) -> Tuple[bool, Any]:
        """Get database schema information."""
        if conn_id not in self.connections:
            return False, "Connection not found"
        
        connection = self.connections[conn_id]
        
        try:
            if connection.db_type == DatabaseType.SQLITE:
                return self._get_sqlite_schema(connection)
            elif connection.db_type == DatabaseType.MYSQL:
                return self._get_mysql_schema(connection)
            elif connection.db_type == DatabaseType.POSTGRESQL:
                return self._get_postgresql_schema(connection)
            else:
                return False, f"Schema extraction not implemented for {connection.db_type.value}"
                
        except Exception as e:
            self.logger.error(f"Schema extraction failed for {connection.name}: {e}")
            return False, str(e)
    
    def _get_sqlite_schema(self, connection: DatabaseConnection) -> Tuple[bool, Any]:
        """Get SQLite database schema."""
        try:
            engine = create_engine(connection.connection_string)
            
            with engine.connect() as conn:
                # Get tables
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_result.fetchall()]
                
                schema = {'tables': {}}
                
                for table in tables:
                    # Get table info
                    table_info = conn.execute(text(f"PRAGMA table_info({table})"))
                    columns = []
                    
                    for col_info in table_info.fetchall():
                        columns.append({
                            'name': col_info[1],
                            'type': col_info[2],
                            'nullable': not col_info[3],
                            'primary_key': bool(col_info[5])
                        })
                    
                    schema['tables'][table] = {'columns': columns}
                
                return True, schema
                
        except Exception as e:
            return False, f"SQLite schema extraction failed: {str(e)}"
    
    def _get_mysql_schema(self, connection: DatabaseConnection) -> Tuple[bool, Any]:
        """Get MySQL database schema."""
        try:
            engine = create_engine(connection.connection_string)
            
            with engine.connect() as conn:
                # Get tables
                tables_result = conn.execute(text(f"SHOW TABLES FROM {connection.database}"))
                tables = [row[0] for row in tables_result.fetchall()]
                
                schema = {'tables': {}}
                
                for table in tables:
                    # Get columns
                    columns_result = conn.execute(text(f"DESCRIBE {connection.database}.{table}"))
                    columns = []
                    
                    for col_info in columns_result.fetchall():
                        columns.append({
                            'name': col_info[0],
                            'type': col_info[1],
                            'nullable': col_info[2] == 'YES',
                            'primary_key': col_info[3] == 'PRI'
                        })
                    
                    schema['tables'][table] = {'columns': columns}
                
                return True, schema
                
        except Exception as e:
            return False, f"MySQL schema extraction failed: {str(e)}"
    
    def _get_postgresql_schema(self, connection: DatabaseConnection) -> Tuple[bool, Any]:
        """Get PostgreSQL database schema."""
        try:
            engine = create_engine(connection.connection_string)
            
            with engine.connect() as conn:
                # Get tables
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                """)
                tables_result = conn.execute(tables_query)
                tables = [row[0] for row in tables_result.fetchall()]
                
                schema = {'tables': {}}
                
                for table in tables:
                    # Get columns
                    columns_query = text("""
                        SELECT column_name, data_type, is_nullable, 
                               CASE WHEN column_name IN (
                                   SELECT column_name FROM information_schema.key_column_usage 
                                   WHERE table_name = :table_name
                               ) THEN true ELSE false END as is_primary_key
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """)
                    
                    columns_result = conn.execute(columns_query, {"table_name": table})
                    columns = []
                    
                    for col_info in columns_result.fetchall():
                        columns.append({
                            'name': col_info[0],
                            'type': col_info[1],
                            'nullable': col_info[2] == 'YES',
                            'primary_key': col_info[3]
                        })
                    
                    schema['tables'][table] = {'columns': columns}
                
                return True, schema
                
        except Exception as e:
            return False, f"PostgreSQL schema extraction failed: {str(e)}"
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all database connections."""
        connections_list = []
        
        for conn_id, connection in self.connections.items():
            connections_list.append({
                'id': conn_id,
                'name': connection.name,
                'type': connection.db_type.value,
                'host': connection.host,
                'port': connection.port,
                'database': connection.database,
                'is_active': connection.is_active
            })
        
        return connections_list

if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseIntegrationManager()
    
    # Test default SQLite connection
    connections = db_manager.list_connections()
    if connections:
        conn_id = connections[0]['id']
        success, message = db_manager.test_connection(conn_id)
        logger.info("Connection test: {'✅' if success else '❌'} {message}")
        
        if success:
            # Get schema
            success, schema = db_manager.get_database_schema(conn_id)
            if success:
                logger.info("✅ Schema extracted: {len(schema.get('tables', {}))} tables found")
            else:
                logger.info("❌ Schema extraction failed: {schema}")
    
    logger.info("✅ Database integration manager initialized with {len(connections)} connections")
