import console_database
import console_student
import console_course
import console_grade
import console_login
import console_report

class ConsoleGradeManagementSystem:
    def __init__(self):
        """Initialize the console-based system"""
        self.db = console_database.DatabaseConnection()
        self.current_user = None
        self.running = True
        
    def run(self):
        """Start the application"""
        print("=" * 60)
        print("STUDENT GRADE MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Check database
        if not self.db.conn:
            print("\n[-] FATAL: Could not establish database connection.")
            print("[*] Please verify:")
            print("   1. Database file exists at the configured path")
            print("   2. You have read/write permissions")
            print("   3. The database is not corrupted")
            input("\nPress Enter to exit...")
            return
        
        # Show login first
        login_system = console_login.ConsoleLoginSystem(self.db)
        self.current_user = login_system.login()
        
        if not self.current_user:
            print("Login failed. Exiting...")
            return
        
        # Main menu loop
        while self.running:
            self.show_main_menu()
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "=" * 60)
        print(f"MAIN MENU - Welcome {self.current_user['full_name']} ({self.current_user['role']})")
        print("=" * 60)
        print("1. Student Management")
        print("2. Course Management")
        print("3. Grade Management")
        print("4. Reports & Analytics")
        print("5. Logout")
        print("6. Exit")
        print("-" * 60)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            self.show_student_management()
        elif choice == "2":
            self.show_course_management()
        elif choice == "3":
            self.show_grade_management()
        elif choice == "4":
            self.show_reports()
        elif choice == "5":
            self.logout()
        elif choice == "6":
            self.exit_system()
        else:
            print("Invalid choice. Please try again.")
    
    def show_student_management(self):
        """Student management menu"""
        student_mgr = console_student.ConsoleStudentManager(self.db)
        student_mgr.menu()
    
    def show_course_management(self):
        """Course management menu"""
        course_mgr = console_course.ConsoleCourseManager(self.db)
        course_mgr.menu()
    
    def show_grade_management(self):
        """Grade management menu"""
        grade_mgr = console_grade.ConsoleGradeManager(self.db)
        grade_mgr.menu()
    
    def show_reports(self):
        """Reports and analytics menu"""
        report_gen = console_report.ConsoleReportGenerator(self.db)
        report_gen.menu()
    
    def logout(self):
        """Log out current user"""
        confirm = input("\nAre you sure you want to logout? (y/n): ").strip().lower()
        if confirm == 'y':
            self.current_user = None
            login_system = console_login.ConsoleLoginSystem(self.db)
            self.current_user = login_system.login()
            if not self.current_user:
                self.running = False
    
    def exit_system(self):
        """Exit the application"""
        confirm = input("\nAre you sure you want to exit? (y/n): ").strip().lower()
        if confirm == 'y':
            print("\nThank you for using Student Grade Management System!")
            print("Goodbye!")
            self.running = False
            self.db.close()


if __name__ == "__main__":
    app = ConsoleGradeManagementSystem()
    app.run()
