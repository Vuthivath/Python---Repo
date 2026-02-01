class ConsoleStudentManager:
    def __init__(self, db_connection):
        """Initialize student manager"""
        self.db = db_connection
    
    def menu(self):
        """Show student management menu"""
        while True:
            print("\n" + "=" * 60)
            print("STUDENT MANAGEMENT")
            print("=" * 60)
            print("1. View All Students")
            print("2. Search Student")
            print("3. Add Student")
            print("4. Update Student")
            print("5. Delete Student")
            print("6. Back to Main Menu")
            print("-" * 60)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                self.view_all_students()
            elif choice == "2":
                self.search_student()
            elif choice == "3":
                self.add_student()
            elif choice == "4":
                self.update_student()
            elif choice == "5":
                self.delete_student()
            elif choice == "6":
                break
            else:
                print("[✗] Invalid choice. Please try again.")
    
    def view_all_students(self):
        """Display all students in a table (5 per page)"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, department, status
                FROM tblStudent
                ORDER BY lastName, firstName
            """
            rows = self.db.fetch_all(query)
            
            if not rows or len(rows) == 0:
                print("\n[i] No students found in the database.")
                return
            
            # Paginate: show 5 students at a time
            students_per_page = 5
            total_pages = (len(rows) + students_per_page - 1) // students_per_page
            
            for page in range(total_pages):
                start_idx = page * students_per_page
                end_idx = min(start_idx + students_per_page, len(rows))
                page_rows = rows[start_idx:end_idx]
                
                print("\n" + "=" * 90)
                print(f"STUDENTS (Page {page + 1}/{total_pages})")
                print("=" * 90)
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Gender':<8} {'department':<20} {'Status':<10}")
                print("-" * 90)
                
                for row in page_rows:
                    try:
                        print(f"{row.studentID:<5} {row.firstName:<15} {row.lastName:<15} {row.gender:<8} {row.department:<20} {row.status:<10}")
                    except Exception as row_error:
                        print(f"[✗] Error processing row: {row_error}")
                        continue
                
                print("=" * 90)
                
                # Ask if user wants to see next page
                if page < total_pages - 1:
                    cont = input("Press Enter to see next page (or 'q' to quit): ").strip().lower()
                    if cont == 'q':
                        break
            
            print(f"\n[i] Total students: {len(rows)}")
            
        except Exception as e:
            print(f"[✗] Error loading students: {e}")
            print(f"[!] Please check if tblStudent table exists in the database")
    
    def search_student(self):
        """Search for a student"""
        print("\n" + "-" * 60)
        print("SEARCH STUDENT")
        print("-" * 60)
        print("1. Search by ID")
        print("2. Search by Name")
        print("-" * 60)
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            self.search_by_id()
        elif choice == "2":
            self.search_by_name()
        else:
            print("[✗] Invalid choice.")
    
    def search_by_id(self):
        """Search student by ID"""
        try:
            student_id = input("Enter student ID: ").strip()
            
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, department, status
                FROM tblStudent WHERE studentID=?
            """
            row = self.db.fetch_one(query, (student_id,))
            
            if row:
                print("\n" + "=" * 60)
                print("STUDENT DETAILS")
                print("=" * 60)
                print(f"ID:             {row.studentID}")
                print(f"Name:           {row.firstName} {row.lastName}")
                print(f"Gender:         {row.gender}")
                print(f"DOB:            {self.db.format_date(row.dateOfbirth)}")
                print(f"Contact:        {row.contact}")
                print(f"Address:        {row.address}")
                print(f"department:     {row.department}")
                print(f"Status:         {row.status}")
                print("=" * 60)
            else:
                print("[✗] Student not found.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def search_by_name(self):
        """Search student by name"""
        try:
            name = input("Enter student name (first or last): ").strip()
            
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, department, status
                FROM tblStudent 
                WHERE firstName LIKE ? OR lastName LIKE ?
                ORDER BY lastName, firstName
            """
            search_pattern = f"%{name}%"
            rows = self.db.fetch_all(query, (search_pattern, search_pattern))
            
            if not rows:
                print("[✗] No students found with that name.")
                return
            
            print("\n" + "-" * 100)
            print(f"Found {len(rows)} student(s):")
            print("-" * 100)
            print(f"{'ID':<8} {'First Name':<15} {'Last Name':<15} {'Gender':<8} {'Contact':<15} {'department':<20} {'Status':<10}")
            print("-" * 100)
            
            for row in rows:
                print(f"{row.studentID:<8} {row.firstName:<15} {row.lastName:<15} {row.gender:<8} {row.contact:<15} {row.department:<20} {row.status:<10}")
            
            print("-" * 100)
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def add_student(self):
        """Add a new student"""
        print("\n" + "-" * 60)
        print("ADD NEW STUDENT")
        print("-" * 60)
        
        try:
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            gender = input("Gender (M/F): ").strip().upper()
            dob = input("Date of Birth (YYYY-MM-DD): ").strip()
            contact = input("Contact: ").strip()
            address = input("Address: ").strip()
            department = input("Department: ").strip()
            status = input("Status (Active/Inactive): ").strip()
            
            if not first_name or not last_name:
                print("[✗] First name and last name are required.")
                return
            
            query = """
                INSERT INTO tblStudent (firstName, lastName, gender, dateOfbirth, 
                                       contact, address, department, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (first_name, last_name, gender, dob, contact, address, department, status)
            
            if self.db.execute_query(query, values):
                print("[✓] Student added successfully!")
            else:
                print("[✗] Failed to add student.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def update_student(self):
        """Update existing student"""
        print("\n" + "-" * 60)
        print("UPDATE STUDENT")
        print("-" * 60)
        
        try:
            student_id = input("Enter student ID to update: ").strip()
            
            # Check if student exists
            query = "SELECT * FROM tblStudent WHERE studentID=?"
            if not self.db.fetch_one(query, (student_id,)):
                print("[✗] Student not found.")
                return
            
            print("\nEnter new information (leave blank to keep current value):")
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            gender = input("Gender (M/F): ").strip().upper()
            dob = input("Date of Birth (YYYY-MM-DD): ").strip()
            contact = input("Contact: ").strip()
            address = input("Address: ").strip()
            department = input("Department: ").strip()
            status = input("Status: ").strip()
            
            # Build update query dynamically (only update non-empty fields)
            updates = []
            params = []
            
            if first_name:
                updates.append("firstName=?")
                params.append(first_name)
            if last_name:
                updates.append("lastName=?")
                params.append(last_name)
            if gender:
                updates.append("gender=?")
                params.append(gender)
            if dob:
                updates.append("dateOfbirth=?")
                params.append(dob)
            if contact:
                updates.append("contact=?")
                params.append(contact)
            if address:
                updates.append("address=?")
                params.append(address)
            if department:
                updates.append("department=?")
                params.append(department)
            if status:
                updates.append("status=?")
                params.append(status)
            
            if not updates:
                print("[i] No updates provided.")
                return
            
            params.append(student_id)
            query = f"UPDATE tblStudent SET {', '.join(updates)} WHERE studentID=?"
            
            if self.db.execute_query(query, params):
                print("[✓] Student updated successfully!")
            else:
                print("[✗] Failed to update student.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def delete_student(self):
        """Delete a student"""
        print("\n" + "-" * 60)
        print("DELETE STUDENT")
        print("-" * 60)
        
        try:
            student_id = input("Enter student ID to delete: ").strip()
            
            # Confirm deletion
            confirm = input("Are you sure you want to delete this student? (y/n): ").strip().lower()
            if confirm != 'y':
                print("[i] Deletion cancelled.")
                return
            
            query = "DELETE FROM tblStudent WHERE studentID=?"
            if self.db.execute_query(query, (student_id,)):
                print("[✓] Student deleted successfully!")
            else:
                print("[✗] Failed to delete student.")
        except Exception as e:
            print(f"[✗] Error: {e}")
