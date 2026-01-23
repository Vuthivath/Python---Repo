import pyodbc
from datetime import date, datetime

class DatabaseConnection:
    def setup_users_table(self):
        """Create Users table if it doesn't exist"""
        try:
            # Check if table exists using a different approach
            try:
                self.cursor.execute("SELECT * FROM tblUsers WHERE 1=0")
                return
            except:
                self.cursor.execute("""
                    CREATE TABLE tblUsers (
                        userID COUNTER PRIMARY KEY,
                        username TEXT(50) NOT NULL,
                        password_hash TEXT(64) NOT NULL,
                        role TEXT(20) NOT NULL,
                        fullName TEXT(100),
                        email TEXT(100)
                    )
                """)
                
                # Default users
                import hashlib
                default_users = [
                    ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrator', 'System Admin'),
                    ('teacher', hashlib.sha256('teacher123'.encode()).hexdigest(), 'Teacher', 'John Doe'),
                    ('student', hashlib.sha256('student123'.encode()).hexdigest(), 'Student', 'Jane Smith')
                ]
                
                for user in default_users:
                    self.cursor.execute("""
                        INSERT INTO tblUsers (username, password_hash, role, fullName)
                        VALUES (?, ?, ?, ?)
                    """, user)
                
                self.conn.commit()
                print("Users table created with default accounts")
                
        except Exception as e:
            print(f"Note: Could not setup users table: {e}")
            print("This is OK - the table may already exist or permissions may be restricted")
    def __init__(self, db_path=None):
        if db_path is None:
            # Default path
            self.db_path = r"D:\Documents\DBMS\Assignment-Python.accdb"
        else:
            self.db_path = db_path
            
        self.conn_string = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={self.db_path};"
        )
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish connection"""
        try:
            self.conn = pyodbc.connect(self.conn_string)
            self.cursor = self.conn.cursor()
            print("Database connected successfully.")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def format_date(self, d):
        """Format date for display"""
        if isinstance(d, (date, datetime)):
            return d.strftime("%Y-%b-%d")
        return ""
    
    def execute_query(self, query, params=None):
        """Execute a query and commit"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Query error: {e}")
            return False
    
    def fetch_one(self, query, params=None):
        """Fetch single row"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Fetch error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Fetch error: {e}")
            return []
    
    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")
