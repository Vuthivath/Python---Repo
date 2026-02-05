class ConsoleCourseManager:
    """Manages course catalog operations including adding, updating, and viewing courses."""
    def __init__(self, db_connection):
        self.db = db_connection
    
    def menu(self):
        while True:
            print("\n--- COURSE MANAGEMENT ---")
            print("1. View All Courses")
            print("2. Search Course")
            print("3. Add Course")
            print("4. Update Course")
            print("5. Delete Course")
            print("6. Back")
            
            choice = input("Choice: ").strip()
            
            if choice == "1": self.view_all_courses()
            elif choice == "2": self.search_course()
            elif choice == "3": self.add_course()
            elif choice == "4": self.update_course()
            elif choice == "5": self.delete_course()
            elif choice == "6": break
            else: print("Invalid choice.")
    
    def view_all_courses(self): #SHOW ALL COURSES
        rows = self.db.fetch_all("SELECT * FROM tblCourse ORDER BY courseName")
        if not rows:
            print("No courses found.")
            return
        
        print("\n" + "ID".ljust(5) + "Name".ljust(30) + "Credit".ljust(8) + "Dept".ljust(20))
        print("-" * 65)
        for r in rows:
            print(str(r.courseID).ljust(5) + str(r.courseName).ljust(30) + str(r.credit).ljust(8) + str(r.department).ljust(20))
    
    def search_course(self): #SEARCH COURSE
        print("\nSearch Course:")
        print("1. By ID")
        print("2. By Name")
        c = input("Choice: ")
        if c == "1": self.search_by_id()
        elif c == "2": self.search_by_name()
        else: print("Invalid.")
    
    def search_by_id(self): #SEARCH COURSE BY ID
        cid = input("Enter Course ID: ")
        row = self.db.fetch_one("SELECT * FROM tblCourse WHERE courseID=?", (cid,))
        if row:
            print(f"\nID: {row.courseID}\nName: {row.courseName}\nCredit: {row.credit}\nDept: {row.department}")
        else:
            print("Not found.")
    
    def search_by_name(self): #SEARCH COURSE BY NAME
        name = input("Enter Course Name: ")
        rows = self.db.fetch_all("SELECT * FROM tblCourse WHERE courseName LIKE ?", (f"%{name}%",))
        if not rows:
            print("Not found.")
            return
        
        print("\n" + "ID".ljust(5) + "Name".ljust(30) + "Credit".ljust(8) + "Dept".ljust(20))
        print("-" * 65)
        for r in rows:
            print(str(r.courseID).ljust(5) + str(r.courseName).ljust(30) + str(r.credit).ljust(8) + str(r.department).ljust(20))
    
    def add_course(self): #ADD COURSE
        print("\nAdd Course")
        name = input("Name: ")
        credit = input("Credit: ")
        dept = input("Department: ")
        
        if self.db.execute_query("INSERT INTO tblCourse (courseName, credit, department) VALUES (?,?,?)", (name, credit, dept)):
            print("Added.")
        else:
            print("Failed.")
    
    def update_course(self): #UPDATE COURSE
        cid = input("Enter Course ID to update: ")
        if not self.db.fetch_one("SELECT * FROM tblCourse WHERE courseID=?", (cid,)):
            print("Not found.")
            return
            
        print("Enter new info (leave blank to keep):")
        name = input("Name: ")
        credit = input("Credit: ")
        dept = input("Department: ")
        
        # Build dynamic update query
        updates = []
        params = []
        if name:
            updates.append("courseName=?")
            params.append(name)
        if credit:
            updates.append("credit=?")
            params.append(credit)
        if dept:
            updates.append("department=?")
            params.append(dept)
            
        if updates:
            params.append(cid)
            self.db.execute_query(f"UPDATE tblCourse SET {', '.join(updates)} WHERE courseID=?", params)
            print("Updated.")
    
    def delete_course(self):
        cid = input("Enter Course ID to delete: ")
        if input("Confirm? (y/n): ") == 'y':
            self.db.execute_query("DELETE FROM tblCourse WHERE courseID=?", (cid,))
            print("Deleted.")