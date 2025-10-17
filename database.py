import psycopg2
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """Handle database connections for smart city data"""
    
    def __init__(self):
        # Check if DATABASE_URL is provided
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Parse DATABASE_URL
            self._parse_database_url(database_url)
        else:
            # Use individual environment variables or defaults
            self.host = os.getenv('DB_HOST', 'localhost')
            self.port = os.getenv('DB_PORT', '5432')
            self.database = os.getenv('DB_NAME', 'smart_city')
            self.user = os.getenv('DB_USER', 'admin')
            self.password = os.getenv('DB_PASSWORD', 'admin123')
        
        self.conn = None
        self.cursor = None
    
    def _parse_database_url(self, url):
        """Parse DATABASE_URL into connection parameters"""
        # Pattern: postgresql://user:password@host:port/database
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, url)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.host = match.group(3)
            self.port = match.group(4)
            self.database = match.group(5)
        else:
            raise ValueError("Invalid DATABASE_URL format")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.database}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
