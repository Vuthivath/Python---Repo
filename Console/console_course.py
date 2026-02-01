class ConsoleCourseManager:
    def __init__(self, db_connection):
        """Initialize course manager"""
        self.db = db_connection
    
    def menu(self):
        """Show course management menu"""
        while True:
            print("\n" + "=" * 60)
            print("COURSE MANAGEMENT")
            print("=" * 60)
            print("1. View All Courses")
            print("2. Search Course")
            print("3. Add Course")
            print("4. Update Course")
            print("5. Delete Course")
            print("6. Back to Main Menu")
            print("-" * 60)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                self.view_all_courses()
            elif choice == "2":
                self.search_course()
            elif choice == "3":
                self.add_course()
            elif choice == "4":
                self.update_course()
            elif choice == "5":
                self.delete_course()
            elif choice == "6":
                break
            else:
                print("[✗] Invalid choice. Please try again.")
    
    def view_all_courses(self):
        """Display all courses in a table"""
        try:
            query = """
                SELECT courseID, courseName, credit, department
                FROM tblCourse
                ORDER BY courseName
            """
            rows = self.db.fetch_all(query)
            
            if not rows or len(rows) == 0:
                print("\n[i] No courses found in the database.")
                return
            
            # Paginate: show 5 courses at a time
            courses_per_page = 5
            total_pages = (len(rows) + courses_per_page - 1) // courses_per_page
            
            for page in range(total_pages):
                start_idx = page * courses_per_page
                end_idx = min(start_idx + courses_per_page, len(rows))
                page_rows = rows[start_idx:end_idx]
                
                print("\n" + "=" * 80)
                print(f"COURSES (Page {page + 1}/{total_pages})")
                print("=" * 80)
                print(f"{'ID':<5} {'Course Name':<35} {'Credit':<8} {'Department':<15}")
                print("-" * 80)
                
                for row in page_rows:
                    try:
                        course_id = str(row.courseID) if row.courseID else ""
                        course_name = str(row.courseName)[:33] if row.courseName else ""
                        credit = str(row.credit) if row.credit else ""
                        department = str(row.department) if row.department else ""
                        
                        print(f"{course_id:<5} {course_name:<35} {credit:<8} {department:<15}")
                    except Exception as row_error:
                        print(f"[✗] Error processing row: {row_error}")
                        continue
                
                print("=" * 80)
                
                # Ask if user wants to see next page
                if page < total_pages - 1:
                    cont = input("Press Enter to see next page (or 'q' to quit): ").strip().lower()
                    if cont == 'q':
                        break
            
            print(f"\n[i] Total courses: {len(rows)}")
            
        except Exception as e:
            print(f"[✗] Error loading courses: {e}")
            print(f"[!] Please check if tblCourse table exists in the database")
    
    def search_course(self):
        """Search for a course"""
        print("\n" + "-" * 60)
        print("SEARCH COURSE")
        print("-" * 60)
        print("1. Search by ID")
        print("2. Search by Course Name")
        print("-" * 60)
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            self.search_by_id()
        elif choice == "2":
            self.search_by_name()
        else:
            print("Invalid choice.")
    
    def search_by_id(self):
        """Search course by ID"""
        try:
            course_id = input("Enter course ID: ").strip()
            
            query = """
                SELECT courseID, courseName, credit, department
                FROM tblCourse WHERE courseID=?
            """
            row = self.db.fetch_one(query, (course_id,))
            
            if row:
                print("\n" + "=" * 60)
                print("COURSE DETAILS")
                print("=" * 60)
                print(f"ID:             {row.courseID}")
                print(f"Course Name:    {row.courseName}")
                print(f"Credit:         {row.credit}")
                print(f"Department:     {row.department}")
                print("=" * 60)
            else:
                print("[✗] Course not found.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def search_by_name(self):
        """Search course by name"""
        try:
            name = input("Enter course name: ").strip()
            
            query = """
                SELECT courseID, courseName, credit, department
                FROM tblCourse 
                WHERE courseName LIKE ?
                ORDER BY courseID
            """
            rows = self.db.fetch_all(query, (f"%{name}%",))
            
            if not rows or len(rows) == 0:
                print("No courses found with that name.")
                return
            
            print("\n" + "-" * 100)
            print(f"Found {len(rows)} course(s):")
            print("-" * 100)
            print(f"{'ID':<6} {'Course Name':<35} {'Credit':<8} {'Department':<20}")
            print("-" * 100)
            
            for row in rows:
                print(f"{row.courseID:<6} {row.courseName:<35} {row.credit:<8} {row.department:<20}")
            
            print("-" * 100)
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def add_course(self):
        """Add a new course"""
        print("\n" + "-" * 60)
        print("ADD NEW COURSE")
        print("-" * 60)
        
        try:
            name = input("Course Name: ").strip()
            credit = input("Credit (default 3): ").strip()
            department = input("Department: ").strip()
            
            if not name:
                print("[✗] Course name is required.")
                return
            
            try:
                credit = int(credit) if credit else 3
            except ValueError:
                print("[✗] Credit must be a number.")
                return
            
            query = """
                INSERT INTO tblCourse (courseName, credit, department)
                VALUES (?, ?, ?)
            """
            
            values = (name, credit, department)
            
            if self.db.execute_query(query, values):
                print("[✓] Course added successfully!")
            else:
                print("[✗] Failed to add course.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def update_course(self):
        """Update existing course"""
        print("\n" + "-" * 60)
        print("UPDATE COURSE")
        print("-" * 60)
        
        try:
            course_id = input("Enter course ID to update: ").strip()
            
            # Check if course exists
            query = "SELECT courseName, credit, department FROM tblCourse WHERE courseID=?"
            row = self.db.fetch_one(query, (course_id,))
            if not row:
                print("[✗] Course not found.")
                return
            
            print(f"Updating: {row.courseName} (Credit: {row.credit}, Dept: {row.department})")
            print("\nEnter new information (leave blank to keep current value):")
            name = input("Course Name: ").strip()
            credit = input("Credit: ").strip()
            department = input("Department: ").strip()
            
            updates = []
            params = []
            
            if name:
                updates.append("courseName=?")
                params.append(name)
            if credit:
                try:
                    updates.append("credit=?")
                    params.append(int(credit))
                except ValueError:
                    print("[✗] Invalid input for credit. Please enter a number.")
                    return
            if department:
                updates.append("department=?")
                params.append(department)
            
            if not updates:
                print("[i] No updates provided.")
                return
            
            params.append(course_id)
            query = f"UPDATE tblCourse SET {', '.join(updates)} WHERE courseID=?"
            
            if self.db.execute_query(query, params):
                print("Course updated successfully!")
            else:
                print("Failed to update course.")
        except Exception as e:
            print(f"Error: {e}")
    
    def delete_course(self):
        """Delete a course"""
        print("\n" + "-" * 60)
        print("DELETE COURSE")
        print("-" * 60)
        
        try:
            course_id = input("Enter course ID to delete: ").strip()
            
            # Check if exists and get name
            row = self.db.fetch_one("SELECT courseName FROM tblCourse WHERE courseID=?", (course_id,))
            if not row:
                print("[✗] Course not found.")
                return
            
            confirm = input(f"Are you sure you want to delete '{row.courseName}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("[i] Deletion cancelled.")
                return
            
            query = "DELETE FROM tblCourse WHERE courseID=?"
            if self.db.execute_query(query, (course_id,)):
                print("Course deleted successfully!")
            else:
                print("Failed to delete course.")
        except Exception as e:
            print(f"Error: {e}")