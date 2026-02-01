class ConsoleGradeManager:
    def __init__(self, db_connection):
        """Initialize grade manager"""
        self.db = db_connection
    
    def menu(self):
        """Show grade management menu"""
        while True:
            print("\n" + "=" * 60)
            print("GRADE MANAGEMENT")
            print("=" * 60)
            print("1. View All Grades")
            print("2. View Grades by Student")
            print("3. View Grades by Course")
            print("4. Add Grade")
            print("5. Update Grade")
            print("6. Delete Grade")
            print("7. Back to Main Menu")
            print("-" * 60)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                self.view_all_grades()
            elif choice == "2":
                self.view_grades_by_student()
            elif choice == "3":
                self.view_grades_by_course()
            elif choice == "4":
                self.add_grade()
            elif choice == "5":
                self.update_grade()
            elif choice == "6":
                self.delete_grade()
            elif choice == "7":
                break
            else:
                print("[✗] Invalid choice. Please try again.")
    
    def view_all_grades(self):
        """Display all grades (5 per page)"""
        try:
            query = """
                SELECT enrollmentID, studentID, courseID, firstSemester, secondSemester, gpa, status
                FROM tblGrade
                ORDER BY enrollmentID
            """
            rows = self.db.fetch_all(query)
            
            if not rows or len(rows) == 0:
                print("\n[i] No grades found in the database.")
                return
            
            # Paginate: show 5 grades at a time
            grades_per_page = 5
            total_pages = (len(rows) + grades_per_page - 1) // grades_per_page
            
            for page in range(total_pages):
                start_idx = page * grades_per_page
                end_idx = min(start_idx + grades_per_page, len(rows))
                page_rows = rows[start_idx:end_idx]
                
                print("\n" + "=" * 90)
                print(f"GRADES (Page {page + 1}/{total_pages})")
                print("=" * 90)
                print(f"{'ID':<5} {'StudentID':<10} {'CourseID':<10} {'Sem1':<10} {'Sem2':<10} {'GPA':<6} {'Status':<12}")
                print("-" * 90)
                
                for row in page_rows:
                    try:
                        sem1 = row.firstSemester or "-"
                        sem2 = row.secondSemester or "-"
                        gpa = row.gpa or 0.0
                        status = row.status or ""
                        print(f"{row.enrollmentID:<5} {row.studentID:<10} {row.courseID:<10} {sem1:<10} {sem2:<10} {gpa:<6} {status:<12}")
                    except Exception as row_error:
                        print(f"[✗] Error processing row: {row_error}")
                        continue
                
                print("=" * 90)
                
                # Ask if user wants to see next page
                if page < total_pages - 1:
                    cont = input("Press Enter to see next page (or 'q' to quit): ").strip().lower()
                    if cont == 'q':
                        break
            
            print(f"\n[i] Total grades: {len(rows)}")
            
        except Exception as e:
            print(f"[✗] Error loading grades: {e}")
            print(f"[!] Please check if tblGrade, tblStudent, and tblCourse tables exist")
    
    def view_grades_by_student(self):
        """View grades for a specific student"""
        try:
            student_id = input("Enter student ID: ").strip()
            
            query = """
                SELECT courseID, firstSemester, secondSemester, gpa, status
                FROM tblGrade
                WHERE studentID = ?
                ORDER BY courseID
            """
            rows = self.db.fetch_all(query, (student_id,))
            
            if not rows:
                print("[✗] Student not found or has no grades.")
                return
            
            print("\n" + "=" * 100)
            print(f"GRADES FOR STUDENT ID: {student_id}")
            print("=" * 100)

            print(f"{'CourseID':<10} {'Sem1':<10} {'Sem2':<10} {'GPA':<6} {'Status':<12}")
            print("-" * 100)
            
            for row in rows:
                sem1 = row.firstSemester or "-"
                sem2 = row.secondSemester or "-"
                gpa = row.gpa or 0.0
                status = row.status or ""

                print(f"{row.courseID:<10} {sem1:<10} {sem2:<10} {gpa:<6} {status:<12}")
            
            print("-" * 100)
            print("=" * 100)
            
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def view_grades_by_course(self):
        """View grades for a specific course"""
        try:
            course_id = input("Enter course ID: ").strip()
            
            query = """
                SELECT studentID, firstSemester, secondSemester, gpa, status
                FROM tblGrade
                WHERE courseID = ?
                ORDER BY studentID
            """
            rows = self.db.fetch_all(query, (course_id,))
            
            if not rows:
                print("[✗] Course not found or has no grades.")
                return
            
            print("\n" + "=" * 100)
            print(f"GRADES FOR COURSE ID: {course_id}")
            print("=" * 100)

            print(f"{'StudentID':<10} {'Sem1':<10} {'Sem2':<10} {'GPA':<6} {'Status':<12}")
            print("-" * 100)
            
            for row in rows:
                sem1 = row.firstSemester or "-"
                sem2 = row.secondSemester or "-"
                gpa = row.gpa or 0.0
                status = row.status or ""

                print(f"{row.studentID:<10} {sem1:<10} {sem2:<10} {gpa:<6} {status:<12}")
            
            print("-" * 100)
            print(f"\nTotal enrollments: {len(rows)}")
            print("=" * 100)
            
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def add_grade(self):
        """Add a new grade"""
        print("\n" + "-" * 60)
        print("ADD NEW GRADE")
        print("-" * 60)
        
        try:
            student_id = input("Student ID: ").strip()
            course_id = input("Course ID: ").strip()
            sem1 = input("First Semester: ").strip()
            sem2 = input("Second Semester: ").strip()
            gpa = input("GPA: ").strip()
            status = input("Status: ").strip()
            
            if not student_id or not course_id:
                print("[✗] Student ID and Course ID are required.")
                return
            
            query = """
                INSERT INTO tblGrade (studentID, courseID, firstSemester, secondSemester, 
                                     gpa, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            values = (student_id, course_id, sem1, sem2, gpa, status)
            
            if self.db.execute_query(query, values):
                print("[✓] Grade added successfully!")
            else:
                print("[✗] Failed to add grade.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def update_grade(self):
        """Update existing grade"""
        print("\n" + "-" * 60)
        print("UPDATE GRADE")
        print("-" * 60)
        
        try:
            grade_id = input("Enter Enrollment ID to update: ").strip()
            
            query = "SELECT * FROM tblGrade WHERE enrollmentID=?"
            if not self.db.fetch_one(query, (grade_id,)):
                print("[✗] Enrollment record not found.")
                return
            
            print("\nEnter new information (leave blank to keep current value):")
            sem1 = input("First Semester: ").strip()
            sem2 = input("Second Semester: ").strip()
            gpa = input("GPA: ").strip()
            status = input("Status: ").strip()
            
            updates = []
            params = []
            
            if sem1:
                updates.append("firstSemester=?")
                params.append(sem1)
            if sem2:
                updates.append("secondSemester=?")
                params.append(sem2)
            if gpa:
                updates.append("gpa=?")
                params.append(gpa)
            if status:
                updates.append("status=?")
                params.append(status)
            
            if not updates:
                print("[i] No updates provided.")
                return
            
            params.append(grade_id)
            query = f"UPDATE tblGrade SET {', '.join(updates)} WHERE enrollmentID=?"
            
            if self.db.execute_query(query, params):
                print("[✓] Grade updated successfully!")
            else:
                print("[✗] Failed to update grade.")
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def delete_grade(self):
        """Delete a grade"""
        print("\n" + "-" * 60)
        print("DELETE GRADE")
        print("-" * 60)
        
        try:
            grade_id = input("Enter Enrollment ID to delete: ").strip()
            
            confirm = input("Are you sure you want to delete this record? (y/n): ").strip().lower()
            if confirm != 'y':
                print("[i] Deletion cancelled.")
                return
            
            query = "DELETE FROM tblGrade WHERE enrollmentID=?"
            if self.db.execute_query(query, (grade_id,)):
                print("[✓] Grade deleted successfully!")
            else:
                print("[✗] Failed to delete grade.")
        except Exception as e:
            print(f"[✗] Error: {e}")
