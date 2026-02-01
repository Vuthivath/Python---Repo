from datetime import datetime

class ConsoleReportGenerator:
    def __init__(self, db_connection):
        """Initialize report generator"""
        self.db = db_connection
    
    def menu(self):
        """Show reports menu"""
        while True:
            print("\n" + "=" * 60)
            print("REPORTS & ANALYTICS")
            print("=" * 60)
            print("1. Student List Report")
            print("2. Grade Summary Report")
            print("3. Student Transcript")
            print("4. Top Performers")
            print("5. Course Statistics")
            print("6. At-Risk Students")
            print("7. Export Report to File")
            print("8. Back to Main Menu")
            print("-" * 60)
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                self.generate_student_list()
            elif choice == "2":
                self.generate_grade_summary()
            elif choice == "3":
                self.generate_student_transcript()
            elif choice == "4":
                self.generate_top_performers()
            elif choice == "5":
                self.generate_course_stats()
            elif choice == "6":
                self.generate_at_risk()
            elif choice == "7":
                self.export_report()
            elif choice == "8":
                break
            else:
                print("[✗] Invalid choice. Please try again.")
    
    def generate_student_list(self):
        """Generate list of all students"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, 
                       dateOfbirth, contact, department, status
                FROM tblStudent
                ORDER BY lastName, firstName
            """
            rows = self.db.fetch_all(query)
            
            print("\n" + "=" * 100)
            print("STUDENT LIST REPORT")
            print("=" * 100)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Students: {len(rows)}")
            print("-" * 100)
            
            print(f"{'ID':<8} {'Name':<25} {'Gender':<8} {'Department':<20} {'Status':<12}")
            print("-" * 100)
            
            for row in rows:
                name = f"{row.firstName} {row.lastName}"
                print(f"{row.studentID:<8} {name:<25} {row.gender:<8} {row.department:<20} {row.status:<12}")
            
            print("=" * 100)
            
            # Statistics
            print("\nSTATISTICS:")
            print(f"  Total Students: {len(rows)}")
            
            # Gender distribution
            male_count = sum(1 for r in rows if r.gender and r.gender.upper() in ['M', 'MALE'])
            female_count = sum(1 for r in rows if r.gender and r.gender.upper() in ['F', 'FEMALE'])
            print(f"  By Gender:")
            print(f"    - Male: {male_count}")
            print(f"    - Female: {female_count}")
            
            # Status distribution
            status_dist = {}
            for row in rows:
                status = row.status or "Unknown"
                status_dist[status] = status_dist.get(status, 0) + 1
            
            print(f"  By Status:")
            for status, count in sorted(status_dist.items()):
                print(f"    - {status}: {count}")
            
            # Department distribution
            department_dist = {}
            for row in rows:
                department = row.department or "Undeclared"
                department_dist[department] = department_dist.get(department, 0) + 1
            
            print(f"  By Department:")
            for department, count in sorted(department_dist.items()):
                print(f"    - {department}: {count}")
            
        except Exception as e:
            print(f"[✗] Error generating report: {e}")
    
    def generate_grade_summary(self):
        """Generate grade summary report"""
        try:
            query = """
                SELECT s.firstName, s.lastName, c.courseName,
                       g.gpa, g.firstSemester, g.secondSemester, g.status
                FROM ((tblGrade g
                INNER JOIN tblStudent s ON g.studentID = s.studentID)
                INNER JOIN tblCourse c ON g.courseID = c.courseID)
                ORDER BY s.lastName, g.firstSemester
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                print("\n[i] No grade records found.")
                return
            
            print("\n" + "=" * 110)
            print("GRADE SUMMARY REPORT")
            print("=" * 110)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Records: {len(rows)}")
            print("-" * 110)
            
            print(f"{'Student':<25} {'Course Name':<30} {'GPA':<6} {'Sem1':<8} {'Sem2':<8} {'Status':<12}")
            print("-" * 110)
            
            for row in rows:
                student_name = f"{row.firstName} {row.lastName}"
                print(f"{student_name:<25} {row.courseName:<30} {row.gpa:<6} {row.firstSemester:<8} {row.secondSemester:<8} {row.status:<12}")
            
            print("=" * 110)
            
            # Grade distribution
            print("\nGPA DISTRIBUTION:")
            grade_dist = {}
            for row in rows:
                gpa = row.gpa or 0.0
                grade_dist[gpa] = grade_dist.get(gpa, 0) + 1
            
            for grade, count in sorted(grade_dist.items()):
                percentage = (count / len(rows)) * 100
                print(f"  {grade}: {count} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"[✗] Error generating report: {e}")
    
    def generate_student_transcript(self):
        """Generate transcript for a student"""
        try:
            student_id = input("Enter student ID: ").strip()
            
            # Get student info
            student_query = """
                SELECT firstName, lastName, department, status 
                FROM tblStudent WHERE studentID=?
            """
            student_info = self.db.fetch_one(student_query, (student_id,))
            
            if not student_info:
                print("[✗] Student not found.")
                return
            
            # Get grades
            grades_query = """
                SELECT c.courseName, c.credit,
                       g.gpa, g.firstSemester, g.secondSemester
                FROM (tblGrade g
                INNER JOIN tblCourse c ON g.courseID = c.courseID)
                WHERE g.studentID=?
                ORDER BY g.firstSemester, c.courseName
            """
            grades = self.db.fetch_all(grades_query, (student_id,))
            
            print("\n" + "=" * 100)
            print("OFFICIAL STUDENT TRANSCRIPT")
            print("=" * 100)
            print(f"Student: {student_info.firstName} {student_info.lastName}")
            print(f"Student ID: {student_id}")
            print(f"Department: {student_info.department}")
            print(f"Status: {student_info.status}")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 100)
            
            if not grades:
                print("[i] No grades found for this student.")
                print("=" * 100)
                return
            
            print(f"{'Course Name':<35} {'Credit':<8} {'GPA':<6} {'Sem1':<8} {'Sem2':<8}")
            print("-" * 100)
            
            total_credits = 0
            earned_credits = 0
            total_points = 0
            
            for grade in grades:
                try:
                    cred = float(grade.credit) if grade.credit else 0.0
                except:
                    cred = 0.0
                
                try:
                    gpa_val = float(grade.gpa) if grade.gpa else 0.0
                except:
                    gpa_val = 0.0

                print(f"{grade.courseName:<35} {cred:<8} {gpa_val:<6} {grade.firstSemester:<8} {grade.secondSemester:<8}")
                
                total_credits += cred
                if gpa_val > 0:
                    earned_credits += cred
                    total_points += gpa_val * cred
            
            print("-" * 100)
            
            # Calculate GPA
            gpa = total_points / total_credits if total_credits > 0 else 0
            completion_rate = (earned_credits / total_credits * 100) if total_credits > 0 else 0
            
            print(f"\nSUMMARY:")
            print(f"  Total Courses: {len(grades)}")
            print(f"  Total Credits Attempted: {total_credits}")
            print(f"  Total Credits Earned: {earned_credits}")
            print(f"  GPA: {gpa:.2f}")
            print(f"  Completion Rate: {completion_rate:.1f}%")
            print("=" * 100)
            
        except Exception as e:
            print(f"[✗] Error: {e}")
    
    def generate_top_performers(self):
        """Generate top performers report"""
        try:
            # Fetch raw data and calculate in Python to avoid Access SQL aggregation errors
            query = """
                SELECT s.studentID, s.firstName, s.lastName, s.department, g.gpa
                FROM tblStudent s
                INNER JOIN tblGrade g ON s.studentID = g.studentID
            """
            rows = self.db.fetch_all(query)
            
            # Process data in Python
            student_stats = {}
            for row in rows:
                sid = row.studentID
                if sid not in student_stats:
                    student_stats[sid] = {
                        'name': f"{row.firstName} {row.lastName}",
                        'dept': row.department,
                        'gpas': []
                    }
                try:
                    if row.gpa is not None:
                        student_stats[sid]['gpas'].append(float(row.gpa))
                except:
                    pass
            
            # Calculate averages
            results = []
            for sid, data in student_stats.items():
                gpas = data['gpas']
                if gpas:
                    avg_gpa = sum(gpas) / len(gpas)
                    results.append({
                        'studentID': sid,
                        'firstName': data['name'].split()[0], # Simplified
                        'lastName': " ".join(data['name'].split()[1:]),
                        'department': data['dept'],
                        'courses_taken': len(gpas),
                        'avg_gpa': avg_gpa
                    })
            
            # Sort by GPA descending
            results.sort(key=lambda x: x['avg_gpa'], reverse=True)
            
            print("\n" + "=" * 100)
            print("TOP PERFORMERS REPORT")
            print("=" * 100)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 100)
            
            print(f"{'Rank':<6} {'ID':<8} {'Name':<25} {'Department':<20} {'Courses':<10} {'GPA':<8}")
            print("-" * 100)
            
            for rank, row in enumerate(results[:10], 1):
                name = f"{row['firstName']} {row['lastName']}"
                gpa = row['avg_gpa']
                print(f"{rank:<6} {row['studentID']:<8} {name:<25} {row['department']:<20} {row['courses_taken']:<10} {gpa:<8.2f}")
            
            print("=" * 100)
            print(f"\n[i] Showing top 10 performers out of {len(results)} students with grades")
            
        except Exception as e:
            print(f"[✗] Error generating report: {e}")
    
    def generate_course_stats(self):
        """Generate course statistics"""
        try:
            # Fetch raw data and calculate in Python
            query = """
                SELECT c.courseID, c.courseName, c.credit, g.gpa
                FROM tblCourse c
                LEFT JOIN tblGrade g ON c.courseID = g.courseID
            """
            rows = self.db.fetch_all(query)
            
            # Process data
            course_stats = {}
            for row in rows:
                cid = row.courseID
                if cid not in course_stats:
                    course_stats[cid] = {
                        'name': row.courseName,
                        'credit': row.credit,
                        'gpas': []
                    }
                try:
                    if row.gpa is not None:
                        course_stats[cid]['gpas'].append(float(row.gpa))
                except:
                    pass
            
            # Prepare results
            results = []
            for cid, data in course_stats.items():
                gpas = data['gpas']
                avg_grade = sum(gpas) / len(gpas) if gpas else 0.0
                results.append({
                    'courseName': data['name'],
                    'credit': data['credit'],
                    'enrollments': len(gpas),
                    'avg_grade': avg_grade
                })
            
            # Sort by name
            results.sort(key=lambda x: x['courseName'])
            
            print("\n" + "=" * 100)
            print("COURSE STATISTICS REPORT")
            print("=" * 100)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 100)
            
            print(f"{'Course Name':<35} {'Credit':<8} {'Enrollments':<12} {'Avg GPA':<10}")
            print("-" * 100)
            
            total_enrollments = 0
            for row in results:
                avg_grade = row['avg_grade']
                enrollments = row['enrollments']
                total_enrollments += enrollments
                print(f"{row['courseName']:<35} {row['credit']:<8} {enrollments:<12} {avg_grade:<10.2f}")
            
            print("-" * 100)
            print(f"Total Enrollments: {total_enrollments}")
            print(f"Total Courses: {len(results)}")
            print("=" * 100)
            
        except Exception as e:
            print(f"[✗] Error generating report: {e}")
    
    def generate_at_risk(self):
        """Generate at-risk students report"""
        try:
            # Fetch raw data and filter in Python
            query = """
                SELECT s.studentID, s.firstName, s.lastName, s.department, s.status, g.gpa
                FROM tblStudent s
                LEFT JOIN tblGrade g ON s.studentID = g.studentID
            """
            rows = self.db.fetch_all(query)
            
            # Process data
            student_stats = {}
            for row in rows:
                # Filter active students only (case-insensitive check)
                if not row.status or row.status.lower() != 'active':
                    continue
                    
                sid = row.studentID
                if sid not in student_stats:
                    student_stats[sid] = {
                        'name': f"{row.firstName} {row.lastName}",
                        'dept': row.department,
                        'gpas': []
                    }
                try:
                    if row.gpa is not None:
                        student_stats[sid]['gpas'].append(float(row.gpa))
                except:
                    pass
            
            # Identify at-risk
            at_risk_students = []
            for sid, data in student_stats.items():
                gpas = data['gpas']
                if not gpas: continue
                
                avg_gpa = sum(gpas) / len(gpas)
                failed_count = sum(1 for g in gpas if g < 1.0)
                
                if avg_gpa < 2.0 or failed_count > 0:
                    at_risk_students.append({
                        'studentID': sid,
                        'name': data['name'],
                        'department': data['dept'],
                        'total_grades': len(gpas),
                        'failed_courses': failed_count,
                        'current_gpa': avg_gpa
                    })
            
            # Sort by GPA
            at_risk_students.sort(key=lambda x: x['current_gpa'])
            
            print("\n" + "=" * 110)
            print("AT-RISK STUDENTS REPORT")
            print("=" * 110)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Criteria: GPA < 2.0 or has failed courses")
            print("-" * 110)
            
            print(f"{'ID':<8} {'Name':<25} {'Department':<20} {'Total Grades':<12} {'Failed':<8} {'GPA':<8}")
            print("-" * 110)
            
            for row in at_risk_students:
                name = row['name']
                gpa = row['current_gpa']
                failed = row['failed_courses']
                print(f"{row['studentID']:<8} {name:<25} {row['department']:<20} {row['total_grades']:<12} {failed:<8} {gpa:<8.2f}")
            
            print("-" * 110)
            print(f"[⚠] {len(at_risk_students)} student(s) identified as at-risk")
            print("=" * 110)
            
        except Exception as e:
            print(f"[✗] Error generating report: {e}")
    
    def export_report(self):
        """Export report to file"""
        filename = input("Enter filename (without extension): ").strip()
        if not filename:
            print("[✗] Filename cannot be empty.")
            return
        
        filename = f"{filename}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("STUDENT GRADE MANAGEMENT SYSTEM - REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 100 + "\n\n")
                
                # Student List
                f.write("STUDENT LIST\n")
                f.write("-" * 100 + "\n")
                query = "SELECT COUNT(*) FROM tblStudent"
                result = self.db.fetch_one(query)
                f.write(f"Total Students: {result[0] if result else 0}\n\n")
                
                # Grade Summary
                f.write("GRADE SUMMARY\n")
                f.write("-" * 100 + "\n")
                query = "SELECT COUNT(*) FROM tblGrade"
                result = self.db.fetch_one(query)
                f.write(f"Total Grades: {result[0] if result else 0}\n\n")
                
                # Course Summary
                f.write("COURSE SUMMARY\n")
                f.write("-" * 100 + "\n")
                query = "SELECT COUNT(*) FROM tblCourse"
                result = self.db.fetch_one(query)
                f.write(f"Total Courses: {result[0] if result else 0}\n")
            
            print(f"[✓] Report exported to {filename}")
        except Exception as e:
            print(f"[✗] Error exporting report: {e}")
