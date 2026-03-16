import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None or self.connection.closed != 0:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            self.connection = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            self.connection.autocommit = True
        return self.connection

    def get_cursor(self):
        return self.connect().cursor()

db_connection = DatabaseConnection()
