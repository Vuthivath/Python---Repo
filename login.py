import tkinter as tk
from tkinter import messagebox
import hashlib

class LoginSystem:
    def __init__(self, parent, db_connection, on_login_success):
        """
        Initialize login system
        :param parent: Parent window (from main.py)
        :param db_connection: Database connection object
        :param on_login_success: Callback function when login succeeds
        """
        self.parent = parent
        self.db = db_connection
        self.on_login_success = on_login_success
        
        # Create login window
        self.create_login_window()
    
    def create_login_window(self):
        """Create the login interface"""
        # Create a top-level window for login
        self.login_window = tk.Toplevel(self.parent)
        self.login_window.title("Login - Student Grade System")
        self.login_window.geometry("400x450")
        self.login_window.resizable(False, False)
        
        # Center the window
        self.login_window.transient(self.parent)
        self.login_window.grab_set()  # Make it modal
        
        # Look nice
        self.login_window.configure(bg="#f0f0f0")
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.login_window, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="LOGIN", 
                font=("Arial", 20, "bold"), 
                bg="#2c3e50", fg="white").pack(expand=True)
        
        tk.Label(header_frame, text="Student Grade Management System", 
                font=("Arial", 10), 
                bg="#2c3e50", fg="#ecf0f1").pack()
        
        # ========== LOGIN FORM ==========
        form_frame = tk.Frame(self.login_window, bg="#f0f0f0", padx=30, pady=30)
        form_frame.pack(fill="both", expand=True)
        
        # Username
        tk.Label(form_frame, text="Username:", 
                font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, 
                                                       sticky="w", pady=(0, 5))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 11), 
                                      width=25)
        self.username_entry.grid(row=1, column=0, pady=(0, 20))
        self.username_entry.focus()  # Auto-focus on username
        
        # Password
        tk.Label(form_frame, text="Password:", 
                font=("Arial", 11), bg="#f0f0f0").grid(row=2, column=0, 
                                                       sticky="w", pady=(0, 5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), 
                                      width=25, show="•")
        self.password_entry.grid(row=3, column=0, pady=(0, 30))
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.attempt_login())
        
        # Login button
        login_btn = tk.Button(form_frame, text="LOGIN", 
                             font=("Arial", 11, "bold"),
                             bg="#27ae60", fg="white",
                             width=20, height=2,
                             command=self.attempt_login)
        login_btn.grid(row=4, column=0)
        
        # Forgot password/Register (optional)
        bottom_frame = tk.Frame(form_frame, bg="#f0f0f0")
        bottom_frame.grid(row=5, column=0, pady=(20, 0))
        
        tk.Button(bottom_frame, text="Forgot Password?", 
                 font=("Arial", 9), fg="#3498db", bg="#f0f0f0",
                 bd=0, cursor="hand2",
                 command=self.show_forgot_password).pack(side="left", padx=5)
        
        tk.Label(bottom_frame, text="|", bg="#f0f0f0", fg="#bdc3c7").pack(side="left")
        
        tk.Button(bottom_frame, text="Register",
font=("Arial", 9), fg="#e74c3c", bg="#f0f0f0",
                 bd=0, cursor="hand2",
                 command=self.show_register).pack(side="left", padx=5)
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(self.login_window, bg="#ecf0f1", height=40)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        tk.Label(footer_frame, text="© 2024 Student Grade System", 
                font=("Arial", 9), bg="#ecf0f1", fg="#7f8c8d").pack(pady=10)
        
        # Test credentials label (remove in production!)
        test_label = tk.Label(self.login_window, 
                             text="Test: admin/admin123", 
                             font=("Arial", 8), bg="#f0f0f0", fg="#95a5a6")
        test_label.place(x=10, y=420)
    
    def attempt_login(self):
        """Validate login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Basic validation
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # For demonstration - Replace with database check
        if self.validate_credentials(username, password):
            # Store user info
            user_info = {
                'username': username,
                'role': self.get_user_role(username),
                'full_name': self.get_user_full_name(username)
            }
            
            # Close login window
            self.login_window.destroy()
            
            # Call success callback with user info
            self.on_login_success(user_info)
        else:
            messagebox.showerror("Login Failed", 
                                "Invalid username or password")
            self.password_entry.delete(0, tk.END)  # Clear password field
            self.password_entry.focus()
    
    def validate_credentials(self, username, password):
        """Check if credentials are valid"""
        # TEMPORARY: For testing without database setup
        test_users = {
            'admin': 'admin123',
            'teacher': 'teacher123',
            'student': 'student123'
        }
        
        # Check if user exists and password matches
        if username in test_users and password == test_users[username]:
            return True
        
        return False
    
    def check_credentials_in_db(self, username, password):
        """Check credentials against database"""
        try:
            query = """
                SELECT password_hash, role 
                FROM tblUsers 
                WHERE username = ?
            """
            result = self.db.fetch_one(query, (username,))
            
            if result:
                stored_hash = result[0]
                # Hash the entered password and compare
                entered_hash = self.hash_password(password)
                if entered_hash == stored_hash:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_user_role(self, username):
        """Get user's role from database"""
        # Temporary roles
        roles = {
            'admin': 'Administrator',
            'teacher': 'Teacher',
            'student': 'Student'
        }
        return roles.get(username, 'Student')
    
    def get_user_full_name(self, username):
        """Get user's full name"""
        names = {
            'admin': 'System Administrator',
            'teacher': 'John Teacher',
            'student': 'Jane Student'
        }
        return names.get(username, username)
    
    def show_forgot_password(self):
        """Show forgot password dialog"""
        messagebox.showinfo("Forgot Password", 
                          "Please contact system administrator.\n"
                          "Email: admin@school.edu")
    
    def show_register(self):
        """Show registration form"""
        messagebox.showinfo("Registration", 
                          "User registration is currently disabled.\n"
                          "Please contact administrator for account creation.")
