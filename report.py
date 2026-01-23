import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime

class ReportGenerator:
    def init(self, parent_frame, db_connection):
        self.parent = parent_frame
        self.db = db_connection
        self.create_widgets()
    
    def create_widgets(self):
        """Create the reports interface"""
        # Clear parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.parent, text="📊 Reports & Analytics", 
                        font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        # ========== REPORT SELECTION ==========
        selection_frame = tk.LabelFrame(self.parent, text="Select Report Type", 
                                       padx=10, pady=10)
        selection_frame.pack(pady=10, padx=10, fill="x")
        
        # Report types
        self.report_var = tk.StringVar(value="student_list")
        
        reports = [
            ("Student List", "student_list"),
            ("Grade Summary", "grade_summary"),
            ("Student Transcript", "student_transcript"),
            ("Top Performers", "top_performers"),
            ("Course Statistics", "course_stats"),
            ("At-Risk Students", "at_risk")
        ]
        
        for i, (text, value) in enumerate(reports):
            tk.Radiobutton(selection_frame, text=text, variable=self.report_var, 
                          value=value, font=("Arial", 10)).grid(
                          row=i//2, column=i%2, sticky="w", padx=10, pady=5)
        
        # ========== FILTER OPTIONS ==========
        filter_frame = tk.LabelFrame(self.parent, text="Filters", padx=10, pady=10)
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        # Student filter
        tk.Label(filter_frame, text="Student:").grid(row=0, column=0, sticky="w", pady=5)
        self.student_var = tk.StringVar()
        student_combo = ttk.Combobox(filter_frame, textvariable=self.student_var, 
                                    width=30, state="readonly")
        student_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Course filter
        tk.Label(filter_frame, text="Course:").grid(row=1, column=0, sticky="w", pady=5)
        self.course_var = tk.StringVar()
        course_combo = ttk.Combobox(filter_frame, textvariable=self.course_var, 
                                   width=30, state="readonly")
        course_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Date range
        tk.Label(filter_frame, text="From Date:").grid(row=0, column=2, sticky="w", padx=(20,0), pady=5)
        self.from_date = tk.Entry(filter_frame, width=12)
        self.from_date.insert(0, "2024-01-01")
        self.from_date.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(filter_frame, text="To Date:").grid(row=1, column=2, sticky="w", padx=(20,0), pady=5)
        self.to_date = tk.Entry(filter_frame, width=12)
        self.to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.to_date.grid(row=1, column=3, padx=5, pady=5)
        
        # ========== ACTION BUTTONS ==========
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Generate Report", command=self.generate_report,
                 bg="#27ae60", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export to Text", command=self.export_to_text,
                 bg="#3498db", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Print Preview", command=self.print_preview,
                 bg="#9b59b6", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear Results", command=self.clear_results,bg="#e74c3c", fg="white", width=15).pack(side="left", padx=5)
        
        # ========== RESULTS AREA ==========
        # Notebook for different views
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Table View
        self.table_frame = tk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Table View")
        
        # Treeview for table display
        self.tree = ttk.Treeview(self.table_frame)
        
        # Scrollbars
        tree_scroll_y = tk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = tk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        
        # Tab 2: Text View
        self.text_frame = tk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Text View")
        
        self.text_widget = tk.Text(self.text_frame, wrap="word", font=("Courier New", 10))
        text_scroll = tk.Scrollbar(self.text_frame, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=text_scroll.set)
        
        text_scroll.pack(side="right", fill="y")
        self.text_widget.pack(fill="both", expand=True)
        
        # Tab 3: Statistics
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        self.stats_text = tk.Text(self.stats_frame, wrap="word", font=("Arial", 10))
        stats_scroll = tk.Scrollbar(self.stats_frame, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        stats_scroll.pack(side="right", fill="y")
        self.stats_text.pack(fill="both", expand=True)
        
        # Load dropdown data
        self.load_dropdown_data()
    
    def load_dropdown_data(self):
        """Load students and courses for dropdowns"""
        try:
            # Load students
            students = self.db.fetch_all("SELECT studentID, firstName, lastName FROM tblStudent ORDER BY lastName")
            student_list = ["All Students"] + [f"{s[0]} - {s[1]} {s[2]}" for s in students]
            
            student_combo = self.parent.winfo_children()[2].winfo_children()[1].winfo_children()[1]  # Get the combobox
            student_combo['values'] = student_list
            student_combo.current(0)
            
            # Load courses
            courses = self.db.fetch_all("SELECT courseID, courseCode, courseName FROM tblCourse ORDER BY courseCode")
            course_list = ["All Courses"] + [f"{c[0]} - {c[1]} {c[2]}" for c in courses]
            
            course_combo = self.parent.winfo_children()[2].winfo_children()[1].winfo_children()[3]  # Get the combobox
            course_combo['values'] = course_list
            course_combo.current(0)
            
        except Exception as e:
            print(f"Error loading dropdown data: {e}")
    
    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_var.get()
        
        if report_type == "student_list":
            self.generate_student_list()
        elif report_type == "grade_summary":
            self.generate_grade_summary()
        elif report_type == "student_transcript":
            self.generate_student_transcript()
        elif report_type == "top_performers":
            self.generate_top_performers()
        elif report_type == "course_stats":
            self.generate_course_stats()
        elif report_type == "at_risk":
            self.generate_at_risk_students()
    
    def generate_student_list(self):
        """Generate list of all students"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, 
                       dateOfbirth, contact, major, status
                FROM tblStudent
                ORDER BY lastName, firstName
            """
            rows = self.db.fetch_all(query)
            
            # Clear previous results
            self.clear_treeview()
            self.text_widget.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            
            # Configure treeview columns
            self.tree["columns"] = ("ID", "First Name", "Last Name", "Gender", 
                                   "DOB", "Contact", "Major", "Status")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
            
            # Add data to treeview
            for row in rows:
                dob = self.db.format_date(row.dateOfbirth) if row.dateOfbirth else ""
                self.tree.insert("", "end", values=(
                    row.studentID, row.firstName, row.lastName, row.gender,
                    dob, row.contact, row.major, row.status
                ))
            
            # Text view
            self.text_widget.insert(1.0, "STUDENT LIST REPORT\n")
            self.text_widget.insert(2.0, "="*50 + "\n")
            self.text_widget.insert(3.0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            self.text_widget.insert(4.0, f"Total Students: {len(rows)}\n\n")
            
            header = f"{'ID':<6} {'Name':<25} {'Gender':<8} {'Major':<15} {'Status':<10}\n"
            self.text_widget.insert(tk.END, header)
            self.text_widget.insert(tk.END, "-"*70 + "\n")
            
            for row in rows:
                line = f"{row.studentID:<6} {row.firstName} {row.lastName:<20} {row.gender:<8} {row.major:<15} {row.status:<10}\n"
                self.text_widget.insert(tk.END, line)
            
            # Statistics
            stats = f"""
            STUDENT STATISTICS
            ==================
            Total Students: {len(rows)}
            
            By Gender:
            - Male: {sum(1 for r in rows if str(r.gender).upper() == 'MALE' or r.gender == 'M')}
            - Female: {sum(1 for r in rows if str(r.gender).upper() == 'FEMALE' or r.gender == 'F')}
            
            By Status:
            - Active: {sum(1 for r in rows if str(r.status).upper() == 'ACTIVE')}
            - Inactive: {sum(1 for r in rows if str(r.status).upper() == 'INACTIVE')}
            - Graduated: {sum(1 for r in rows if str(r.status).upper() == 'GRADUATED')}
            
            By Major:
            """
            self.stats_text.insert(1.0, stats)
            
            # Count by major
            majors = {}
            for row in rows:
                major = row.major or "Undeclared"
                majors[major] = majors.get(major, 0) + 1
            
            for major, count in sorted(majors.items()):
                self.stats_text.insert(tk.END, f"- {major}: {count}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def generate_grade_summary(self):
        """Generate grade summary report"""
        try:
            query = """
                SELECT s.studentID, s.firstName, s.lastName, 
                       g.courseID, c.courseCode, c.courseName,
                       g.grade, g.semester
                FROM tblStudent s
                JOIN tblGrade g ON s.studentID = g.studentID
                JOIN tblCourse c ON g.courseID = c.courseIDORDER BY s.lastName, s.firstName, g.semester
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                messagebox.showinfo("No Data", "No grade records found.")
                return
            
            # Clear and setup treeview
            self.clear_treeview()
            self.text_widget.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            
            self.tree["columns"] = ("Student ID", "Student Name", "Course", 
                                   "Grade", "Semester")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
            
            # Add data
            for row in rows:
                self.tree.insert("", "end", values=(
                    row.studentID, f"{row.firstName} {row.lastName}",
                    f"{row.courseCode} - {row.courseName}",
                    row.grade, row.semester
                ))
            
            # Text view
            self.text_widget.insert(1.0, "GRADE SUMMARY REPORT\n")
            self.text_widget.insert(2.0, "="*50 + "\n")
            
            # Statistics
            total_grades = len(rows)
            grade_counts = {}
            for row in rows:
                grade = row.grade or "No Grade"
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            stats = f"""
            GRADE DISTRIBUTION
            ==================
            Total Grade Records: {total_grades}
            
            Grade Breakdown:
            """
            for grade, count in sorted(grade_counts.items()):
                percentage = (count / total_grades) * 100
                stats += f"- {grade}: {count} ({percentage:.1f}%)\n"
            
            self.stats_text.insert(1.0, stats)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate grade report:\n{str(e)}")
    
    def generate_student_transcript(self):
        """Generate transcript for a specific student"""
        student_selection = self.student_var.get()
        if student_selection == "All Students" or not student_selection:
            messagebox.showwarning("Selection Needed", "Please select a specific student for transcript.")
            return
        
        try:
            # Extract student ID from selection
            student_id = int(student_selection.split(" - ")[0])
            
            # Get student info
            student_query = """
                SELECT firstName, lastName, major, status 
                FROM tblStudent WHERE studentID=?
            """
            student_info = self.db.fetch_one(student_query, (student_id,))
            
            if not student_info:
                messagebox.showerror("Error", "Student not found.")
                return
            
            # Get grades
            grades_query = """
                SELECT c.courseCode, c.courseName, c.credits,
                       g.grade, g.semester
                FROM tblGrade g
                JOIN tblCourse c ON g.courseID = c.courseID
                WHERE g.studentID=?
                ORDER BY g.semester, c.courseCode
            """
            grades = self.db.fetch_all(grades_query, (student_id,))
            
            # Clear displays
            self.clear_treeview()
            self.text_widget.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            
            # Setup treeview
            self.tree["columns"] = ("Course Code", "Course Name", "Credits", 
                                   "Grade", "Semester")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
            
            # Add grades to treeview
            total_credits = 0
            earned_credits = 0
            grade_points = 0
            
            for grade in grades:
                credits = float(grade.credits or 0)
                total_credits += credits
                
                # Calculate GPA (simple version)
                grade_value = self.grade_to_points(grade.grade)
                if grade_value > 0:
                    earned_credits += credits
                    grade_points += grade_value * credits
                
                self.tree.insert("", "end", values=grade)
            
            # Calculate GPA
            gpa = grade_points / total_credits if total_credits > 0 else 0
            
            # Text view (official transcript look)
            transcript = f"""
            OFFICIAL TRANSCRIPT
            {'='*50}
            Student: {student_info.firstName} {student_info.lastName}
            Student ID: {student_id}
            Major: {student_info.major}
            Status: {student_info.status}
            
            {'='*50}
            COURSE HISTORY
            {'='*50}
            """
            self.text_widget.insert(1.0, transcript)
            
            for grade in grades:
                course_line = f"{grade.courseCode:10} {grade.courseName:30} {grade.credits:3} credits  {grade.grade:5}  {grade.semester}\n"
                self.text_widget.insert(tk.END, course_line)
            
            summary = f"""
            {'='*50}
            ACADEMIC SUMMARY
            {'='*50}
            Total Courses: {len(grades)}
            Total Credits Attempted: {total_credits}
            Total Credits Earned: {earned_credits}
            Grade Point Average (GPA): {gpa:.2f}
            
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
            self.text_widget.insert(tk.END, summary)
            
            # Statistics
            stats = f"""
            TRANSCRIPT ANALYSIS
            ===================
            Student: {student_info.firstName} {student_info.lastName}
            GPA: {gpa:.2f}
            
            Grade Distribution:
            """
            
            grade_dist = {}
            for grade in grades:
                g = grade.grade or "No Grade"
                grade_dist[g] = grade_dist.get(g, 0) + 1
            
            for g, count in sorted(grade_dist.items()):
                stats += f"- {g}: {count}\n"
            
            stats += f"\nCompletion Rate: {(earned_credits/total_credits*100):.1f}%"
            self.stats_text.insert(1.0, stats)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate transcript:\n{str(e)}")
    
    def grade_to_points(self, grade):
        """Convert letter grade to grade points"""
        grade_map = {
            'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0,
            'F': 0.0
        }
        return grade_map.get(str(grade).upper(), 0.0)
    
    def generate_top_performers(self):
        """Generate report of top performing students"""
        try:
            query = """
                SELECT s.studentID, s.firstName, s.lastName, s.major,
                       AVG(CASE 
                           WHEN g.grade = 'A' THEN 4.0
                           WHEN g.grade = 'B' THEN 3.0
                           WHEN g.grade = 'C' THEN 2.0
                           WHEN g.grade = 'D' THEN 1.0
                           ELSE 0
                       END) as avg_gpa,
                       COUNT(g.gradeID) as courses_taken
                FROM tblStudent s
                LEFT JOIN tblGrade g ON s.studentID = g.studentID
                WHERE s.status = 'Active'
                GROUP BY s.studentID, s.firstName, s.lastName, s.majorHAVING COUNT(g.gradeID) >= 1
                ORDER BY avg_gpa DESC
                LIMIT 10
            """
            rows = self.db.fetch_all(query)
            
            self.clear_treeview()
            self.text_widget.delete(1.0, tk.END)
            
            self.tree["columns"] = ("Rank", "Student ID", "Name", "Major", "GPA", "Courses")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
            
            for i, row in enumerate(rows, 1):
                self.tree.insert("", "end", values=(
                    i, row.studentID, f"{row.firstName} {row.lastName}",
                    row.major, f"{row.avg_gpa:.2f}", row.courses_taken
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate top performers report:\n{str(e)}")
            def generate_course_stats(self):
                """Generate statistics for courses"""
        # Similar structure to other reports
        messagebox.showinfo("Coming Soon", "Course statistics feature coming soon!")
    
    def generate_at_risk_students(self):
        """Identify students at risk (failing grades)"""
        # Similar structure to other reports
        messagebox.showinfo("Coming Soon", "At-risk students feature coming soon!")
    
    def export_to_text(self):
        """Export current report to text file"""
        try:
            # Get text from text widget
            content = self.text_widget.get(1.0, tk.END)
            if len(content.strip()) == 0:
                messagebox.showwarning("No Data", "Generate a report first.")
                return
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Report exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    def print_preview(self):
        """Show print preview (simplified)"""
        content = self.text_widget.get(1.0, tk.END)
        if len(content.strip()) > 0:
            preview_window = tk.Toplevel(self.parent)
            preview_window.title("Print Preview")
            preview_window.geometry("600x800")
            
            text_widget = tk.Text(preview_window, wrap="word", font=("Courier New", 10))
            text_widget.insert(1.0, content)
            text_widget.config(state="disabled")
            
            scrollbar = tk.Scrollbar(preview_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="right", fill="y")
            text_widget.pack(fill="both", expand=True)
            
            tk.Button(preview_window, text="Close", 
                     command=preview_window.destroy).pack(pady=10)
        else:
            messagebox.showwarning("No Data", "Generate a report first.")
    
    def clear_results(self):
        """Clear all results"""
        self.clear_treeview()
        self.text_widget.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
    
    def clear_treeview(self):
        """Clear treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Clear columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")