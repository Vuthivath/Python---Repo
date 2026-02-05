from datetime import datetime

class ConsoleReportGenerator:
    # Generates various statistical reports and analytics from the database.
    def __init__(self, db_connection):
        self.db = db_connection

    def menu(self): #LIST FOR CHOICE OF REPORTS
        while True:
            print("--- REPORTS ---")
            print("1. Student List")
            print("2. Grade Summary")
            print("3. Transcript")
            print("4. Top Performers")
            print("5. Course Stats")
            print("6. At-Risk")
            print("7. Export")
            print("8. Back")
            choice = input("Choice: ").strip()
            
            if choice == "1": self.generate_student_list()
            elif choice == "2": self.generate_grade_summary()
            elif choice == "3": self.generate_student_transcript()
            elif choice == "4": self.generate_top_performers()
            elif choice == "5": self.generate_course_stats()
            elif choice == "6": self.generate_at_risk()
            elif choice == "7": self.export_report()
            elif choice == "8": break
            else: print("Invalid choice.")
    
    def generate_student_list(self): #SHOW ALL STUDENTS
        # Print a simple list of all students
        rows = self.db.fetch_all("SELECT * FROM tblStudent ORDER BY lastName")
        print(f"\nSTUDENT LIST ({len(rows)} students)")
        print("=" * 80)
        print(f"{'ID':<8} {'Name':<25} {'Gender':<10} {'Department':<20} {'Status':<12}")
        print("-" * 80)
        for r in rows:
            name = f"{r.firstName} {r.lastName}"
            print(f"{str(r.studentID):<8} {name:<25} {str(r.gender or ''):<10} {str(r.department or ''):<20} {str(r.status or ''):<12}")
    
    def generate_grade_summary(self):
        # Show a summary of grades joining student and course data
        query = """SELECT s.firstName, s.lastName, c.courseName, g.gpa 
                   FROM ((tblGrade g INNER JOIN tblStudent s ON g.studentID = s.studentID) 
                   INNER JOIN tblCourse c ON g.courseID = c.courseID)"""
        rows = self.db.fetch_all(query)
        print(f"\nGRADE SUMMARY ({len(rows)} records)")
        print("=" * 70)
        print(f"{'Student Name':<25} {'Course Name':<30} {'GPA':<5}")
        print("-" * 70)
        for r in rows:
            name = f"{r.firstName} {r.lastName}"
            print(f"{name:<25} {r.courseName:<30} {r.gpa:<5}")
    
    def generate_student_transcript(self): #SHOW STUDENTS TRANSCRIPT
        print("--- TRANSCRIPT ---")
        print("-" * 60)
        sid = input("Student ID: ")
        stu = self.db.fetch_one("SELECT * FROM tblStudent WHERE studentID=?", (sid,))
        if not stu: return print("Not found.")
        
        print(f"TRANSCRIPT: {stu.firstName} {stu.lastName}")
        print("-" * 60)
        query = """
            SELECT c.courseName, c.credit, g.gpa, g.firstSemester, g.secondSemester
            FROM tblGrade g INNER JOIN tblCourse c ON g.courseID = c.courseID
            WHERE g.studentID = ?
        """
        grades = self.db.fetch_all(query, (sid,))
        
        print(f"{'Course':<30} {'Credit':<8} {'Sem1':<6} {'Sem2':<6} {'GPA':<5}")
        print("-" * 60)
        
        total_pts, total_cred = 0, 0
        # Calculate weighted GPA
        for g in grades:
            cred = float(g.credit or 0)
            gpa = float(g.gpa or 0)
            sem1 = str(g.firstSemester or '-')
            sem2 = str(g.secondSemester or '-')
            print(f"{g.courseName:<30} {cred:<8} {sem1:<6} {sem2:<6} {gpa}")
            total_pts += gpa * cred
            total_cred += cred

        print("-" * 60)
        if total_cred: print(f"Overall GPA: {total_pts/total_cred:.2f}")
        print("-" * 60)

    def generate_top_performers(self): #SHOW TOP PERFORMERS
        # Calculate and display students with the highest average GPAs
        rows = self.db.fetch_all("SELECT s.firstName, s.lastName, g.gpa FROM (tblStudent s INNER JOIN tblGrade g ON s.studentID=g.studentID)")
        stats = {}
        for r in rows:
            name = f"{r.firstName} {r.lastName}"
            if name not in stats: stats[name] = []
            if r.gpa: stats[name].append(float(r.gpa))
            
        # Calculate average GPA for each student
        avgs = [(name, sum(g)/len(g)) for name, g in stats.items() if g]
        avgs.sort(key=lambda x: x[1], reverse=True)
        
        print("\nTOP PERFORMERS REPORT")
        print("=" * 50)
        print(f"{'Rank':<6} {'Student Name':<30} {'GPA':<6}")
        print("-" * 50)
        for i, (name, gpa) in enumerate(avgs[:10], 1):
            print(f"{i:<6} {name:<30} {gpa:.2f}")
    
    def generate_course_stats(self): #SHOW COURSE STATS AND AVERAGE
        rows = self.db.fetch_all("SELECT c.courseName, g.gpa FROM (tblCourse c LEFT JOIN tblGrade g ON c.courseID=g.courseID)")
        stats = {}
        for r in rows:
            if r.courseName not in stats: stats[r.courseName] = []
            if r.gpa: stats[r.courseName].append(float(r.gpa))
            
        print("\nCOURSE STATISTICS REPORT")
        print("-" * 60)
        print(f"{'Course Name':<35} {'Students':<10} {'Avg GPA':<10}")
        print("-" * 60)
        for name, gpas in stats.items():
            avg = sum(gpas)/len(gpas) if gpas else 0
            print(f"{name:<35} {len(gpas):<10} {avg:.2f}")
    
    def generate_at_risk(self): #SHOW AT-RISK OF FAILING STUDENTS
        rows = self.db.fetch_all("SELECT s.firstName, s.lastName, g.gpa FROM (tblStudent s LEFT JOIN tblGrade g ON s.studentID=g.studentID) WHERE s.status='Active'")
        stats = {}
        for r in rows:
            name = f"{r.firstName} {r.lastName}"
            if name not in stats: stats[name] = []
            if r.gpa: stats[name].append(float(r.gpa))
            
        print("\nAT-RISK STUDENTS (GPA < 2.0)")
        print("=" * 50)
        print(f"{'Student Name':<35} {'GPA':<6}")
        print("-" * 50)
        for name, gpas in stats.items():
            if gpas:
                avg = sum(gpas)/len(gpas)
                if avg < 2.0: 
                    print(f"{name:<35} {avg:.2f}")
    
    def export_report(self): #EXPORT REPORT(PRINT OUT)
        # Export basic statistics to a text file
        fname = input("Filename: ")
        with open(f"{fname}.txt", "w") as f:
            f.write(f"Report generated: {datetime.now()}\n")
            stu_count = self.db.fetch_one('SELECT COUNT(*) as c FROM tblStudent').c
            grade_count = self.db.fetch_one('SELECT COUNT(*) as c FROM tblGrade').c
            f.write(f"Students: {stu_count}\n")
            f.write(f"Grades: {grade_count}\n")
        print("Exported.")
