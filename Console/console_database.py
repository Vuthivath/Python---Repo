import pyodbc
from datetime import date, datetime
from types import SimpleNamespace

class DatabaseConnection:
    def __init__(self, db_path=None):
        """Initialize database connection"""
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
        """Establish database connection"""
        try:
            self.conn = pyodbc.connect(self.conn_string)
            self.cursor = self.conn.cursor()
            print("[+] Database connected successfully.")
            return True
        except FileNotFoundError:
            print(f"[-] Database file not found at: {self.db_path}")
            print("[!] Please ensure the database file exists.")
            return False
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False
    
    def format_date(self, d):
        """Format date for display"""
        if isinstance(d, (date, datetime)):
            return d.strftime("%Y-%m-%d")
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
            print(f"[-] Query error: {e}")
            return False
    
    def fetch_one(self, query, params=None):
        """Fetch single row"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            row = self.cursor.fetchone()
            if not row:
                return None

            # Build attribute-accessible object from row and column names
            cols = [c[0] for c in self.cursor.description] if self.cursor.description else []
            data = {cols[i]: row[i] for i in range(len(cols))} if cols else dict(enumerate(row))
            return SimpleNamespace(**data)
        except Exception as e:
            print(f"[-] Fetch error: {e}")
            print(f"    Query: {query[:100]}...")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            rows = self.cursor.fetchall()
            if not rows:
                return []

            cols = [c[0] for c in self.cursor.description] if self.cursor.description else []
            out = []
            for row in rows:
                if cols:
                    data = {cols[i]: row[i] for i in range(len(cols))}
                else:
                    data = dict(enumerate(row))
                out.append(SimpleNamespace(**data))
            return out
        except Exception as e:
            print(f"[-] Fetch error: {e}")
            print(f"    Query: {query[:100]}...")
            return []
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[+] Database connection closed.")
    
    def test_connection(self):
        """Test database connection and verify tables exist"""
        try:
            # Test basic connection
            test_query = "SELECT COUNT(*) AS count FROM tblStudent"
            result = self.fetch_one(test_query)
            if result is not None:
                print(f"[+] Database connection verified. Students: {result.count}")
                return True
            else:
                print("[-] Could not connect to database or retrieve data.")
                return False
        except Exception as e:
            print(f"[-] Connection test failed: {e}")
            return False
