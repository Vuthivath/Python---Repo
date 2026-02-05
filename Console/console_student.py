class ConsoleStudentManager:
    # Manages student-related operations: creating, reading, updating, 
    # and deleting student records in the database.
    def __init__(self, db_connection):
        # Initialize student manager
        self.db = db_connection
    
    def menu(self):
        # Show student management menu
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
                print("Invalid choice. Please try again.")
    
    def view_all_students(self): #SHOW ALL STUDENTS
        print("-" * 60)
        try:
            # Select specific columns to ensure display order
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, address, department, status
                FROM tblStudent
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                print("No students found.")
                return

            # Print table header with fixed-width formatting
            print("ID".ljust(10), "First Name".ljust(15), "Last Name".ljust(15),
                  "Gender".ljust(8), "Date of Birth".ljust(15), "Address".ljust(15), "Department".ljust(15), "Status".ljust(15))

            # Iterate through rows and print formatted data
            for p in rows:
                print(str(p.studentID).ljust(10),
                      str(p.firstName).ljust(15),
                      str(p.lastName).ljust(15),
                      str(p.gender).ljust(8),
                      self.db.format_date(p.dateOfbirth).ljust(15),
                      str(p.address).ljust(15),
                      str(p.department).ljust(15),
                      str(p.status).ljust(15))

        except Exception as e:
            print("Database error:", e)
    
    def search_student(self): #CHOICES OF SEARCH STUDENTS
        """Search for a student"""
        print("-" * 60)
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
            print("Invalid choice.")
    
    def search_by_id(self): #SEARCH STUDENTS BY ID
        try:
            student_id = input("Enter Student ID to search: ").strip()

            # Use parameterized query to prevent SQL injection
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, department, status
                FROM tblStudent WHERE studentID=?
            """
            row = self.db.fetch_one(query, (student_id,))
            
            if row:
                print("=" * 60)
                print("STUDENT DETAILS")
                print("=" * 60)
                print(f"ID:             {row.studentID}")
                print(f"Name:           {row.firstName} {row.lastName}")
                print(f"Gender:         {row.gender}")
                print(f"DOB:            {self.db.format_date(row.dateOfbirth)}")
                print(f"Contact:        {row.contact}")
                print(f"Address:        {row.address}")
                print(f"Department:     {row.department}")
                print(f"Status:         {row.status}")
                print("=" * 60)
            else:
                print("Student not found.")
        except Exception as e:
            print("Error: {e}")
    
    def search_by_name(self): #SEARCH STUDENTS BY NAME
        try:
            name = input("Enter student name (first or last): ").strip()
            
            # Search for partial matches in either first or last name
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, department, status
                FROM tblStudent 
                WHERE firstName LIKE ? OR lastName LIKE ?
                ORDER BY lastName, firstName
            """
            # Add wildcards for partial matching
            search_pattern = f"%{name}%"
            rows = self.db.fetch_all(query, (search_pattern, search_pattern))
            
            if not rows:
                print("No students found with that name.")
                return
            
            print("\n" + "-" * 100)
            print(f"Found {len(rows)} student(s):")
            print("-" * 100)
            print("ID".ljust(10), "First Name".ljust(15), "Last Name".ljust(15), 
                  "Gender".ljust(8), "Contact".ljust(15), "Department".ljust(20), "Status".ljust(10))
            print("-" * 100)
            
            for row in rows:
                print(str(row.studentID).ljust(10), str(row.firstName).ljust(15), 
                      str(row.lastName).ljust(15), str(row.gender).ljust(8), 
                      str(row.contact).ljust(15), str(row.department).ljust(20), 
                      str(row.status).ljust(10))
            
            print("-" * 100)
        except Exception as e:
            print(f"Error: {e}")
    
    def add_student(self): #ADD STUDENTS
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
                print("First name and last name are required.")
                return
            
            # Insert new student record
            query = """
                INSERT INTO tblStudent (firstName, lastName, gender, dateOfbirth, 
                                       contact, address, department, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (first_name, last_name, gender, dob, contact, address, department, status)
            
            if self.db.execute_query(query, values):
                print("Student added successfully!")
            else:
                print("Failed to add student.")
        except Exception as e:
            print(f"Error: {e}")
    
    def update_student(self): #UPDATE STUDENT
        print("-" * 60)
        print("UPDATE STUDENT")
        print("-" * 60)
        
        try:
            student_id = input("Enter student ID to update: ").strip()
            
            # Check if student exists
            query = "SELECT * FROM tblStudent WHERE studentID=?"
            if not self.db.fetch_one(query, (student_id,)):
                print("Student not found.")
                return
            
            print("\nEnter new information (leave blank to keep current value):")
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            gender = input("Gender (M/F): ").strip().upper()
            dob = input("Date of Birth (YYYY-MM-DD): ").strip()
            contact = input("Contact: ").strip()
            address = input("Address: ").strip()
            department = input("Department: ").strip()
            status = input("Status (Active/Inactive): ").strip()
            
            # Dynamically build the UPDATE query based on provided inputs
            # Only fields that are not empty will be updated
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
                print("No updates provided.")
                return
            
            # Add the ID as the final parameter for the WHERE clause
            params.append(student_id)
            query = f"UPDATE tblStudent SET {', '.join(updates)} WHERE studentID=?"
            
            if self.db.execute_query(query, params):
                print("Student updated successfully!")
            else:
                print("Failed to update student.")
        except Exception as e:
            print(f"Error: {e}")
    
    def delete_student(self): #DELETE STUDENTS
        """Delete a student"""
        print("-" * 60)
        print("DELETE STUDENT")
        print("-" * 60)
        
        try:
            student_id = input("Enter student ID to delete: ").strip()
            confirm = input("Are you sure you want to delete this student? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return
            
            query = "DELETE FROM tblStudent WHERE studentID=?"
            if self.db.execute_query(query, (student_id,)):
                print("Student deleted successfully!")
            else:
                print("Failed to delete student.")
        except Exception as e:
            print(f"Error: {e}")