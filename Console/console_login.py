"""
Console-based Login System
Handles user authentication
"""

import hashlib

class ConsoleLoginSystem:
    def __init__(self, db_connection):
        """Initialize login system"""
        self.db = db_connection
    
    def login(self):
        """Display login screen and authenticate user"""
        print("\n" + "=" * 60)
        print("LOGIN - STUDENT GRADE MANAGEMENT SYSTEM")
        print("=" * 60)
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("[-] Please enter both username and password")
                attempts += 1
                continue
            
            # Validate credentials
            if self.validate_credentials(username, password):
                user_info = {
                    'username': username,
                    'role': self.get_user_role(username),
                    'full_name': self.get_user_full_name(username)
                }
                print(f"\n[+] Login successful! Welcome {user_info['full_name']}")
                return user_info
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"[-] Invalid username or password. Attempts remaining: {remaining}")
        
        print("[-] Login failed - Maximum attempts exceeded")
        return None
    
    def validate_credentials(self, username, password):
        """Check if credentials are valid"""
        # Test users for demonstration
        test_users = {
            'admin': 'admin123',
            'teacher': 'teacher123',
            'student': 'student123'
        }
        
        return username in test_users and password == test_users[username]
    
    def get_user_role(self, username):
        """Get user's role"""
        roles = {
            'admin': 'Administrator',
            'teacher': 'Teacher',
            'student': 'Student'
        }
        return roles.get(username, 'User')
    
    def get_user_full_name(self, username):
        """Get user's full name"""
        names = {
            'admin': 'System Administrator',
            'teacher': 'John Teacher',
            'student': 'Jane Student'
        }
        return names.get(username, username)
