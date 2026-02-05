class ConsoleGradeManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def menu(self):
        while True:
            print("\n--- GRADE MANAGEMENT ---")
            print("1. View All Grades")
            print("2. View Grades by Student")
            print("3. View Grades by Course")
            print("4. Add Grade")
            print("5. Update Grade")
            print("6. Delete Grade")
            print("7. Back")
            
            choice = input("Choice: ").strip()
            
            if choice == "1": self.view_all_grades()
            elif choice == "2": self.view_grades_by_student()
            elif choice == "3": self.view_grades_by_course()
            elif choice == "4": self.add_grade()
            elif choice == "5": self.update_grade()
            elif choice == "6": self.delete_grade()
            elif choice == "7": break
            else: print("Invalid choice.")
    
    def view_all_grades(self): #SHOW ALL GRADES
        rows = self.db.fetch_all("SELECT * FROM tblGrade ORDER BY enrollmentID")
        if not rows:
            print("No grades found.")
            return
        
        print("\n" + "ID".ljust(5) + "StuID".ljust(10) + "CrsID".ljust(10) + "Sem1".ljust(10) + "Sem2".ljust(10) + "GPA".ljust(6) + "Status".ljust(12))
        print("-" * 70)
        for r in rows:
            print(str(r.enrollmentID).ljust(5) + 
                  str(r.studentID).ljust(10) + 
                  str(r.courseID).ljust(10) + 
                  str(r.firstSemester or '-').ljust(10) + 
                  str(r.secondSemester or '-').ljust(10) + 
                  str(r.gpa or 0).ljust(6) + 
                  str(getattr(r, 'status', getattr(r, 'Status', '')) or '').ljust(12))
    
    def view_grades_by_student(self): #SHOW GRADES BY STUDENT
        sid = input("Enter Student ID: ")
        rows = self.db.fetch_all("SELECT * FROM tblGrade WHERE studentID=?", (sid,))
        if not rows:
            print("No grades found.")
            return

        print("\n" + "CourseID".ljust(10) + "Sem1".ljust(10) + "Sem2".ljust(10) + "GPA".ljust(6) + "Status".ljust(12))
        print("-" * 50)
        for r in rows:
            print(str(r.courseID).ljust(10) + 
                  str(r.firstSemester or '-').ljust(10) + 
                  str(r.secondSemester or '-').ljust(10) + 
                  str(r.gpa or 0).ljust(6) + 
                  str(getattr(r, 'status', getattr(r, 'Status', '')) or '').ljust(12))
    
    def view_grades_by_course(self): #SHOW GRADES BY COURSE
        cid = input("Enter Course ID: ")
        rows = self.db.fetch_all("SELECT * FROM tblGrade WHERE courseID=?", (cid,))
        if not rows:
            print("No grades found.")
            return

        print("\n" + "StudentID".ljust(10) + "Sem1".ljust(10) + "Sem2".ljust(10) + "GPA".ljust(6) + "Status".ljust(12))
        print("-" * 50)
        for r in rows:
            print(str(r.studentID).ljust(10) + 
                  str(r.firstSemester or '-').ljust(10) + 
                  str(r.secondSemester or '-').ljust(10) + 
                  str(r.gpa or 0).ljust(6) + 
                  str(getattr(r, 'status', getattr(r, 'Status', '')) or '').ljust(12))
    
    def add_grade(self): #ADD GRADE
        print("\nAdd New Grade")
        sid = input("Student ID: ")
        cid = input("Course ID: ")
        sem1 = input("Sem 1: ")
        sem2 = input("Sem 2: ")
        gpa = input("GPA: ")
        status = input("Status: ")
        
        if self.db.execute_query("INSERT INTO tblGrade (studentID, courseID, firstSemester, secondSemester, gpa, status) VALUES (?,?,?,?,?,?)", 
                               (sid, cid, sem1, sem2, gpa, status)):
            print("Added successfully.")
        else:
            print("Failed to add.")
    
    def update_grade(self): #UPDATE GRADE
        gid = input("Enter Enrollment ID to update: ")
        if not self.db.fetch_one("SELECT * FROM tblGrade WHERE enrollmentID=?", (gid,)):
            print("Record not found.")
            return
        
        print("Enter new info (leave blank to keep):")
        sem1 = input("Sem 1: ")
        sem2 = input("Sem 2: ")
        gpa = input("GPA: ")
        status = input("Status: ")
        
        # Build dynamic update query
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
            
        if updates:
            params.append(gid)
            self.db.execute_query(f"UPDATE tblGrade SET {', '.join(updates)} WHERE enrollmentID=?", params)
            print("Updated.")
    
    def delete_grade(self): #REMOVE GRADE
        gid = input("Enrollment ID to delete: ")
        if input("Confirm? (y/n): ") == 'y':
            self.db.execute_query("DELETE FROM tblGrade WHERE enrollmentID=?", (gid,))
            print("Deleted.")
