import tkinter as tk
import traceback
from tkinter import ttk, messagebox
import report # report mofule
import database  # database module
import student  # student module
import login  # login module

class GradeManagementSystem:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Student Grade Management System")
            self.root.geometry("1200x800")
            
            # Initialize database connection
            self.db = database.DatabaseConnection()
            self.db.setup_users_table()
            
            # Initialize user info
            self.current_user = None
            
            # Show login first
            self.show_login()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            traceback.print_exc()
            if hasattr(self, 'root'):
                self.root.destroy()
            raise
    
    def show_login(self):
        """Display login window directly on root"""
        # Clear root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login UI directly on root
        self.root.geometry("400x500")
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="LOGIN", 
                font=("Arial", 20, "bold"), 
                bg="#2c3e50", fg="white").pack(expand=True)
        
        tk.Label(header_frame, text="Student Grade Management System", 
                font=("Arial", 10), 
                bg="#2c3e50", fg="#ecf0f1").pack()
        
        # ========== LOGIN FORM ==========
        form_frame = tk.Frame(self.root, bg="#f0f0f0", padx=30, pady=30)
        form_frame.pack(fill="both", expand=True)
        
        # Username
        tk.Label(form_frame, text="Username:", 
                font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, 
                                                       sticky="w", pady=(0, 5))
        username_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        username_entry.grid(row=1, column=0, pady=(0, 20))
        username_entry.focus()
        
        # Password
        tk.Label(form_frame, text="Password:", 
                font=("Arial", 11), bg="#f0f0f0").grid(row=2, column=0, 
                                                       sticky="w", pady=(0, 5))
        password_entry = tk.Entry(form_frame, font=("Arial", 11), 
                                 width=25, show="•")
        password_entry.grid(row=3, column=0, pady=(0, 30))
        
        # Login button
        def attempt_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            # Test credentials
            test_users = {
                'admin': 'admin123',
                'teacher': 'teacher123',
                'student': 'student123'
            }
            
            if username in test_users and password == test_users[username]:
                # Login success
                user_info = {
                    'username': username,
                    'role': {'admin': 'Administrator', 'teacher': 'Teacher', 'student': 'Student'}.get(username, 'User'),
                    'full_name': {'admin': 'System Admin', 'teacher': 'John Teacher', 'student': 'Jane Student'}.get(username, username)
                }
                self.on_login_success(user_info)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
                password_entry.delete(0, tk.END)
                password_entry.focus()
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: attempt_login())
        
        login_btn = tk.Button(form_frame, text="LOGIN", 
                             font=("Arial", 11, "bold"),
                             bg="#27ae60", fg="white",
                             width=20, height=2,
                             command=attempt_login)
        login_btn.grid(row=4, column=0, pady=(10, 0))
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#ecf0f1", height=40)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        tk.Label(footer_frame, text="© 2024 Student Grade System | Test: admin/admin123", 
                font=("Arial", 9), bg="#ecf0f1", fg="#7f8c8d").pack(pady=10)
    
    def on_login_success(self, user_info):
        """Called when user logs in successfully"""
        self.current_user = user_info
        print(f"User {user_info['username']} logged in successfully")
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main interface
        self.create_widgets()
    
    def create_widgets(self):
        """Create the main interface"""
        # Resize window back to normal
        self.root.geometry("1200x800")
        
        # Title with user info
        title_text = f"Student Grade Management System - Welcome {self.current_user['full_name']} ({self.current_user['role']})"
        title = tk.Label(self.root, text=title_text, 
                        font=("Arial", 20, "bold"))
        title.pack(pady=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="Student Management", 
                 command=self.show_students, width=20).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Grade Management", 
                 command=self.show_grades, width=20).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Reports", 
                 command=self.show_reports, width=20).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Logout", 
                 command=self.logout, width=20, bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show students by default
        self.show_students()
    
    def show_students(self):
        """Show student management interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create StudentManager in content frame
        student.StudentManager(self.content_frame, self.db)
    
    def show_grades(self):
        """Show grade management interface"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="Grade Management", 
                font=("Arial", 18)).pack(pady=50)
        # Grade management here later
    
    def show_reports(self):
        """Show reports interface"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.content_frame, text="Reports & Statistics", 
                        font=("Arial", 18, "bold"), bg="white")
        title.pack(pady=15)
        
        # Create a frame for reports
        reports_frame = tk.Frame(self.content_frame, bg="white")
        reports_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            # Get statistics from database
            query = "SELECT COUNT(*) FROM tblStudent"
            result = self.db.fetch_one(query)
            total_students = result[0] if result else 0
            
            query = "SELECT COUNT(*) FROM tblStudent WHERE status='Active'"
            result = self.db.fetch_one(query)
            active_students = result[0] if result else 0
            
            query = "SELECT COUNT(*) FROM tblStudent WHERE status='Inactive'"
            result = self.db.fetch_one(query)
            inactive_students = result[0] if result else 0
            
            # Display statistics in cards
            stats_frame = tk.Frame(reports_frame, bg="white")
            stats_frame.pack(fill="x", pady=10)
            
            # Card 1: Total Students
            card1 = tk.Frame(stats_frame, bg="#3498db", relief="ridge", bd=2)
            card1.pack(side="left", padx=10, pady=10, fill="both", expand=True)
            tk.Label(card1, text="Total Students", font=("Arial", 12, "bold"), 
                    bg="#3498db", fg="white").pack(pady=10)
            tk.Label(card1, text=str(total_students), font=("Arial", 24, "bold"), 
                    bg="#3498db", fg="white").pack(pady=10)
            
            # Card 2: Active Students
            card2 = tk.Frame(stats_frame, bg="#27ae60", relief="ridge", bd=2)
            card2.pack(side="left", padx=10, pady=10, fill="both", expand=True)
            tk.Label(card2, text="Active Students", font=("Arial", 12, "bold"), 
                    bg="#27ae60", fg="white").pack(pady=10)
            tk.Label(card2, text=str(active_students), font=("Arial", 24, "bold"), 
                    bg="#27ae60", fg="white").pack(pady=10)
            
            # Card 3: Inactive Students
            card3 = tk.Frame(stats_frame, bg="#e74c3c", relief="ridge", bd=2)
            card3.pack(side="left", padx=10, pady=10, fill="both", expand=True)
            tk.Label(card3, text="Inactive Students", font=("Arial", 12, "bold"), 
                    bg="#e74c3c", fg="white").pack(pady=10)
            tk.Label(card3, text=str(inactive_students), font=("Arial", 24, "bold"), 
                    bg="#e74c3c", fg="white").pack(pady=10)
            
            # Detailed Report Section
            tk.Label(reports_frame, text="Student Distribution by Status", 
                    font=("Arial", 14, "bold"), bg="white").pack(pady=(20, 10), anchor="w")
            
            # Fetch all statuses
            query = "SELECT status, COUNT(*) as count FROM tblStudent GROUP BY status"
            rows = self.db.fetch_all(query)
            
            if rows:
                for row in rows:
                    status = row[0] or "Unknown"
                    count = row[1]
                    percentage = (count / total_students * 100) if total_students > 0 else 0
                    
                    # Create a row for each status
                    row_frame = tk.Frame(reports_frame, bg="#ecf0f1")
                    row_frame.pack(fill="x", pady=5)
                    
                    tk.Label(row_frame, text=f"{status}:", font=("Arial", 11), 
                            bg="#ecf0f1", width=15, anchor="w").pack(side="left", padx=10)
                    tk.Label(row_frame, text=f"{count} students ({percentage:.1f}%)", 
                            font=("Arial", 11), bg="#ecf0f1").pack(side="left", padx=10)
            
        except Exception as e:
            tk.Label(reports_frame, text=f"Error loading reports: {str(e)}", 
                    font=("Arial", 11), fg="#e74c3c").pack(pady=20)
    
    def logout(self):
        """Log out the current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clear the user info
            self.current_user = None
            
            # Clear content
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Show login again
            self.show_login()    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GradeManagementSystem()
    app.run()