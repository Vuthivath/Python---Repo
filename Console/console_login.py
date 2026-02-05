import hashlib
class ConsoleLoginSystem:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def login(self): # SHOW LOGIN
        print("\n" + "=" * 60)
        print("LOGIN - STUDENT GRADE MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Allow a limited number of login attempts
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("Please enter both username and password")
                attempts += 1
                continue
            
            # Validate credentials against stored users
            if self.validate_credentials(username, password):
                user_info = {
                    'username': username,
                    'role': self.get_user_role(username),
                    'full_name': self.get_user_full_name(username)
                }
                print(f"\nLogin successful! Welcome {user_info['full_name']}")
                return user_info
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"Invalid username or password. Attempts remaining: {remaining}")
        
        print("Login failed - Maximum attempts exceeded")
        return None
    
    def validate_credentials(self, username, password): #USER/PASSWORD
        test_users = {
            'admin': 'admin123',
            'teacher': 'teacher123',
            'student': 'student123'
        }
        
        return username in test_users and password == test_users[username]
    
    def get_user_role(self, username): #USERNAME
        roles = {
            'admin': 'Administrator',
            'teacher': 'Teacher',
            'student': 'Student'
        }
        return roles.get(username, 'User')
    
    def get_user_full_name(self, username): #USER FULL NAME
        names = {
            'admin': 'System Administrator',
            'teacher': 'John Teacher',
            'student': 'Jane Student'
        }
        return names.get(username, username)