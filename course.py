import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font

class CourseManager:
    def __init__(self, parent_frame, db_connection):
        self.parent = parent_frame
        self.db = db_connection
        self.all_items_cache = []
        self.create_widgets()
    
    def create_widgets(self):
        """Create the course management interface"""
        # Clear parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.parent, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="COURSE MANAGEMENT", 
                font=("Arial", 16, "bold"), 
                bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=10)
        
        # ========== ACTION BUTTONS ==========
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=(0, 10))
        
        btn_style = {"width": 12, "height": 1, "font": ("Arial", 10)}
        
        tk.Button(btn_frame, text="Add", command=self.show_add_form,
                 bg="#27ae60", fg="white", **btn_style).grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Update", command=self.show_update_form,
                 bg="#2980b9", fg="white", **btn_style).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.show_delete_form,
                 bg="#e74c3c", fg="white", **btn_style).grid(row=0, column=2, padx=2)
        tk.Button(btn_frame, text="Sort ID", command=self.sort_by_id,
                 bg="#9b59b6", fg="white", **btn_style).grid(row=0, column=3, padx=2)
        tk.Button(btn_frame, text="Refresh", command=self.load_all_courses,
                 bg="#3498db", fg="white", **btn_style).grid(row=0, column=4, padx=2)
        
        # Search entry
        search_frame = tk.Frame(self.parent)
        search_frame.pack(pady=(0, 10))
        
        tk.Label(search_frame, text="Quick Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left")
        
        # ========== TREEVIEW TABLE ==========
        table_frame = tk.Frame(self.parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=25,
                       font=("Arial", 10))
        style.configure("Treeview.Heading", 
                       font=("Arial", 11, "bold"),
                       background="#ecf0f1")
        
        # Create scrollbars
        tree_scroll_y = tk.Scrollbar(table_frame)
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Create Treeview
        self.tree = ttk.Treeview(table_frame,
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set,
                                selectmode="browse",
                                height=15)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Define columns
        self.tree["columns"] = ("ID", "Course Code", "Course Name", "Credits", 
                                "Department", "Academic Year", "Description")
        
        column_widths = {
            "ID": 60, "Course Code": 100, "Course Name": 150, 
            "Credits": 80, "Department": 120, "Academic Year": 120, "Description": 200
        }
        
        self.tree.column("#0", width=0, stretch=False)
        for col in self.tree["columns"]:
            self.tree.column(col, width=column_widths[col], minwidth=50)
            self.tree.heading(col, text=col, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # ========== STATUS BAR ==========
        self.status_frame = tk.Frame(self.parent, bg="#ecf0f1", height=30)
        self.status_frame.pack(fill="x", pady=(5, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                    bg="#ecf0f1", fg="#2c3e50")
        self.status_label.pack(side="left", padx=10)
        
        # ========== LOAD INITIAL DATA ==========
        self.load_all_courses()
    
    def load_all_courses(self):
        """Load all courses into the Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.all_items_cache = []
        self.tree.selection_remove(self.tree.selection())
        
        try:
            query = """
                SELECT courseID, courseCode, courseName, credits, 
                    department, academicYear, description
                FROM tblCourse
                ORDER BY courseCode
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                self.tree.insert("", "end", values=("No data", "", "", "", "", "", ""))
                self.all_items_cache.append(self.tree.get_children()[-1])
                self.update_status("No courses found")
                return
            
            for row in rows:
                item_id = self.tree.insert("", "end", values=(
                    row.courseID,
                    row.courseCode or "",
                    row.courseName or "",
                    row.credits or "",
                    row.department or "",
                    row.academicYear or "",
                    row.description or ""
                ))
                self.all_items_cache.append(item_id)
            
            self.update_status(f"Loaded {len(rows)} course(s)")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load courses:\n{str(e)}")
            self.update_status("Error loading courses", error=True)
    
    def update_status(self, message, error=False):
        """Update status bar"""
        color = "#e74c3c" if error else "#27ae60"
        self.status_label.config(text=message, fg=color)
    
    def sort_by_id(self):
        """Sort courses by ID (small to big)"""
        try:
            items_data = []
            for item_id in self.all_items_cache:
                values = self.tree.item(item_id)["values"]
                if values and values[0] != "No data":
                    try:
                        course_id = int(values[0])
                        items_data.append((course_id, item_id, values))
                    except ValueError:
                        pass
            
            items_data.sort(key=lambda x: x[0])
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for _, item_id, values in items_data:
                self.tree.insert("", "end", values=values)
            
            self.update_status("Sorted by ID (ascending)")
        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort: {str(e)}")
    
    def on_search_change(self, *args):
        """Handle search as user types"""
        search_term = self.search_var.get().lower()
        
        for item in self.all_items_cache:
            self.tree.detach(item)
        
        if not search_term:
            for item in self.all_items_cache:
                self.tree.reattach(item, '', 'end')
            return
        
        for item in self.all_items_cache:
            values = self.tree.item(item)["values"]
            if any(search_term in str(v).lower() for v in values):
                self.tree.reattach(item, '', 'end')
    
    def on_tree_double_click(self, event):
        """Double-click to edit"""
        selection = self.tree.selection()
        if selection:
            self.show_update_form()
    
    def show_add_form(self):
        """Show add course form"""
        self.show_course_form("Add Course", self.insert_course)
    
    def show_update_form(self):
        """Show update course form"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a course to update.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            course_id = values[0]
            self.show_course_form("Update Course", self.update_course, course_id, values)
    
    def show_delete_form(self):
        """Show delete confirmation"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            course_id = values[0]
            course_name = values[2]
            
            response = messagebox.askyesno("Confirm Delete", 
                                          f"Are you sure you want to delete:\n{course_name}?")
            if response:
                self.delete_course(course_id)
    
    def show_course_form(self, title, submit_func, course_id=None, current_values=None):
        """Generic form for add/update"""
        form_window = tk.Toplevel(self.parent)
        form_window.title(title)
        form_window.geometry("500x400")
        form_window.transient(self.parent)
        form_window.grab_set()
        
        tk.Label(form_window, text=title, 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(form_window, padx=20, pady=10)
        form_frame.pack()
        
        fields = [
            ("Course Code:", "code"),
            ("Course Name:", "name"),
            ("Credits:", "credits"),
            ("Department:", "department"),
            ("Academic Year:", "year"),
            ("Description:", "description")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, anchor="w").grid(row=i, column=0, 
                                                             sticky="w", pady=8)
            entry = tk.Entry(form_frame, width=35)
            entry.grid(row=i, column=1, pady=8, padx=(10, 0))
            
            if current_values and course_id:
                if key == "code" and len(current_values) > 1:
                    entry.insert(0, current_values[1] or "")
                elif key == "name" and len(current_values) > 2:
                    entry.insert(0, current_values[2] or "")
                elif key == "credits" and len(current_values) > 3:
                    entry.insert(0, current_values[3] or "")
                elif key == "department" and len(current_values) > 4:
                    entry.insert(0, current_values[4] or "")
                elif key == "year" and len(current_values) > 5:
                    entry.insert(0, current_values[5] or "")
                elif key == "description" and len(current_values) > 6:
                    entry.insert(0, current_values[6] or "")
            
            entries[key] = entry
        
        def submit():
            if course_id:
                submit_func(course_id, entries)
            else:
                submit_func(entries)
            form_window.destroy()
            self.load_all_courses()
        
        tk.Button(form_window, text="Submit", command=submit,
                 width=15, bg="#27ae60", fg="white").pack(pady=20)
    
    def insert_course(self, entries):
        """Add a new course"""
        try:
            # Validate required fields
            code = entries["code"].get().strip()
            name = entries["name"].get().strip()
            credits_str = entries["credits"].get().strip()
            
            if not code or not name:
                messagebox.showwarning("Missing Fields", "Please fill in Course Code and Course Name.")
                return
            
            # Convert credits to integer
            try:
                credits = int(credits_str) if credits_str else 3
            except ValueError:
                messagebox.showerror("Invalid Input", "Credits must be a number.")
                return
            
            query = """
                INSERT INTO tblCourse (courseCode, courseName, credits, 
                                      department, academicYear, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (
                code,
                name,
                credits,
                entries["department"].get().strip(),
                entries["year"].get().strip(),
                entries["description"].get().strip()
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Course added successfully!")
                self.update_status("Course added successfully")
            else:
                messagebox.showerror("Error", "Failed to add course")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def update_course(self, course_id, entries):
        """Update existing course"""
        try:
            # Validate required fields
            code = entries["code"].get().strip()
            name = entries["name"].get().strip()
            credits_str = entries["credits"].get().strip()
            
            if not code or not name:
                messagebox.showwarning("Missing Fields", "Please fill in Course Code and Course Name.")
                return
            
            # Convert credits to integer
            try:
                credits = int(credits_str) if credits_str else 3
            except ValueError:
                messagebox.showerror("Invalid Input", "Credits must be a number.")
                return
            
            query = """
                UPDATE tblCourse
                SET courseCode=?, courseName=?, credits=?, 
                    department=?, academicYear=?, description=?
                WHERE courseID=?
            """
            values = (
                code,
                name,
                credits,
                entries["department"].get().strip(),
                entries["year"].get().strip(),
                entries["description"].get().strip(),
                course_id
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Course updated successfully!")
                self.update_status("Course updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update course")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_course(self, course_id):
        """Delete a course"""
        try:
            query = "DELETE FROM tblCourse WHERE courseID=?"
            if self.db.execute_query(query, (course_id,)):
                messagebox.showinfo("Success", "Course deleted successfully!")
                self.update_status("Course deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete course")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


class GradeManager:
    def __init__(self, parent_frame, db_connection):
        self.parent = parent_frame
        self.db = db_connection
        self.all_items_cache = []
        self.create_widgets()
    
    def create_widgets(self):
        """Create the grade management interface"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.parent, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="GRADE MANAGEMENT", 
                font=("Arial", 16, "bold"), 
                bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=10)
        
        # ========== ACTION BUTTONS ==========
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=(0, 10))
        
        btn_style = {"width": 12, "height": 1, "font": ("Arial", 10)}
        
        tk.Button(btn_frame, text="Add", command=self.show_add_form,
                 bg="#27ae60", fg="white", **btn_style).grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Update", command=self.show_update_form,
                 bg="#2980b9", fg="white", **btn_style).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.show_delete_form,
                 bg="#e74c3c", fg="white", **btn_style).grid(row=0, column=2, padx=2)
        tk.Button(btn_frame, text="Sort ID", command=self.sort_by_id,
                 bg="#9b59b6", fg="white", **btn_style).grid(row=0, column=3, padx=2)
        tk.Button(btn_frame, text="Refresh", command=self.load_all_grades,
                 bg="#3498db", fg="white", **btn_style).grid(row=0, column=4, padx=2)
        
        # Search entry
        search_frame = tk.Frame(self.parent)
        search_frame.pack(pady=(0, 10))
        
        tk.Label(search_frame, text="Quick Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left")
        
        # ========== TREEVIEW TABLE ==========
        table_frame = tk.Frame(self.parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=25,
                       font=("Arial", 10))
        style.configure("Treeview.Heading", 
                       font=("Arial", 11, "bold"),
                       background="#ecf0f1")
        
        tree_scroll_y = tk.Scrollbar(table_frame)
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        self.tree = ttk.Treeview(table_frame,
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set,
                                selectmode="browse",
                                height=15)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        self.tree["columns"] = ("ID", "Student ID", "Course ID", "Grade", 
                                "Grade Points", "Semester", "Status")
        
        column_widths = {
            "ID": 60, "Student ID": 100, "Course ID": 100, 
            "Grade": 80, "Grade Points": 120, "Semester": 120, "Status": 100
        }
        
        self.tree.column("#0", width=0, stretch=False)
        for col in self.tree["columns"]:
            self.tree.column(col, width=column_widths[col], minwidth=50)
            self.tree.heading(col, text=col, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # ========== STATUS BAR ==========
        self.status_frame = tk.Frame(self.parent, bg="#ecf0f1", height=30)
        self.status_frame.pack(fill="x", pady=(5, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                    bg="#ecf0f1", fg="#2c3e50")
        self.status_label.pack(side="left", padx=10)
        
        self.load_all_grades()
    
    def load_all_grades(self):
        """Load all grades into the Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.all_items_cache = []
        self.tree.selection_remove(self.tree.selection())
        
        try:
            query = """
                SELECT gradeID, studentID, courseID, grade, gradePoints, 
                    semester, status
                FROM tblGrade
                ORDER BY studentID
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                self.tree.insert("", "end", values=("No data", "", "", "", "", "", ""))
                self.all_items_cache.append(self.tree.get_children()[-1])
                self.update_status("No grades found")
                return
            
            for row in rows:
                item_id = self.tree.insert("", "end", values=(
                    row.gradeID,
                    row.studentID or "",
                    row.courseID or "",
                    row.grade or "",
                    row.gradePoints or "",
                    row.semester or "",
                    row.status or ""
                ))
                self.all_items_cache.append(item_id)
            
            self.update_status(f"Loaded {len(rows)} grade(s)")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load grades:\n{str(e)}")
            self.update_status("Error loading grades", error=True)
    
    def update_status(self, message, error=False):
        color = "#e74c3c" if error else "#27ae60"
        self.status_label.config(text=message, fg=color)
    
    def sort_by_id(self):
        """Sort grades by ID (small to big)"""
        try:
            items_data = []
            for item_id in self.all_items_cache:
                values = self.tree.item(item_id)["values"]
                if values and values[0] != "No data":
                    try:
                        grade_id = int(values[0])
                        items_data.append((grade_id, item_id, values))
                    except ValueError:
                        pass
            
            items_data.sort(key=lambda x: x[0])
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for _, item_id, values in items_data:
                self.tree.insert("", "end", values=values)
            
            self.update_status("Sorted by ID (ascending)")
        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort: {str(e)}")
    
    def on_search_change(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.all_items_cache:
            self.tree.detach(item)
        
        if not search_term:
            for item in self.all_items_cache:
                self.tree.reattach(item, '', 'end')
            return
        
        for item in self.all_items_cache:
            values = self.tree.item(item)["values"]
            if any(search_term in str(v).lower() for v in values):
                self.tree.reattach(item, '', 'end')
    
    def on_tree_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            self.show_update_form()
    
    def show_add_form(self):
        self.show_grade_form("Add Grade", self.insert_grade)
    
    def show_update_form(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a grade to update.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            grade_id = values[0]
            self.show_grade_form("Update Grade", self.update_grade, grade_id, values)
    
    def show_delete_form(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a grade to delete.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            grade_id = values[0]
            response = messagebox.askyesno("Confirm Delete", 
                                          f"Are you sure you want to delete this grade?")
            if response:
                self.delete_grade(grade_id)
    
    def show_grade_form(self, title, submit_func, grade_id=None, current_values=None):
        form_window = tk.Toplevel(self.parent)
        form_window.title(title)
        form_window.geometry("500x400")
        form_window.transient(self.parent)
        form_window.grab_set()
        
        tk.Label(form_window, text=title, 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(form_window, padx=20, pady=10)
        form_frame.pack()
        
        # Get dropdown options
        grade_options = ["A", "B", "C", "D", "F", "A+", "A-", "B+", "B-", "C+", "C-"]
        status_options = ["Enrolled", "Completed", "Dropped"]
        
        # Load students and courses for dropdowns
        try:
            students = self.db.fetch_all("SELECT studentID, firstName, lastName FROM tblStudent ORDER BY lastName")
            student_options = [f"{s[0]} - {s[1]} {s[2]}" for s in students]
            
            courses = self.db.fetch_all("SELECT courseID, courseCode, courseName FROM tblCourse ORDER BY courseCode")
            course_options = [f"{c[0]} - {c[1]} {c[2]}" for c in courses]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students/courses:\n{str(e)}")
            form_window.destroy()
            return
        
        fields = [
            ("Student:", "student_id", "dropdown"),
            ("Course:", "course_id", "dropdown"),
            ("Grade:", "grade", "dropdown"),
            ("Grade Points:", "points", "entry"),
            ("Semester:", "semester", "entry"),
            ("Status:", "status", "dropdown")
        ]
        
        entries = {}
        for i, field_info in enumerate(fields):
            label = field_info[0]
            key = field_info[1]
            field_type = field_info[2]
            
            tk.Label(form_frame, text=label, anchor="w").grid(row=i, column=0, 
                                                             sticky="w", pady=8)
            
            if field_type == "dropdown":
                if key == "student_id":
                    combo = ttk.Combobox(form_frame, values=student_options, width=32, state="readonly")
                elif key == "course_id":
                    combo = ttk.Combobox(form_frame, values=course_options, width=32, state="readonly")
                elif key == "grade":
                    combo = ttk.Combobox(form_frame, values=grade_options, width=32, state="readonly")
                else:
                    combo = ttk.Combobox(form_frame, values=status_options, width=32, state="readonly")
                
                combo.grid(row=i, column=1, pady=8, padx=(10, 0))
                
                if current_values and grade_id:
                    if key == "student_id" and len(current_values) > 1:
                        # Find matching student
                        student_id = current_values[1]
                        for opt in student_options:
                            if opt.startswith(str(student_id)):
                                combo.set(opt)
                                break
                    elif key == "course_id" and len(current_values) > 2:
                        # Find matching course
                        course_id = current_values[2]
                        for opt in course_options:
                            if opt.startswith(str(course_id)):
                                combo.set(opt)
                                break
                    elif key == "grade" and len(current_values) > 3:
                        combo.set(current_values[3] or "")
                    elif key == "status" and len(current_values) > 6:
                        combo.set(current_values[6] or "")
                
                entries[key] = combo
            else:
                entry = tk.Entry(form_frame, width=35)
                entry.grid(row=i, column=1, pady=8, padx=(10, 0))
                
                if current_values and grade_id:
                    if key == "points" and len(current_values) > 4:
                        entry.insert(0, current_values[4] or "")
                    elif key == "semester" and len(current_values) > 5:
                        entry.insert(0, current_values[5] or "")
                
                entries[key] = entry
        
        def submit():
            if grade_id:
                submit_func(grade_id, entries)
            else:
                submit_func(entries)
            form_window.destroy()
            self.load_all_grades()
        
        tk.Button(form_window, text="Submit", command=submit,
                 width=15, bg="#27ae60", fg="white").pack(pady=20)
    
    def insert_grade(self, entries):
        try:
            # Extract student ID from dropdown (format: "ID - Name")
            student_selection = entries["student_id"].get().strip()
            student_id = student_selection.split(" - ")[0] if student_selection else ""
            
            # Extract course ID from dropdown (format: "ID - Code Name")
            course_selection = entries["course_id"].get().strip()
            course_id = course_selection.split(" - ")[0] if course_selection else ""
            
            query = """
                INSERT INTO tblGrade (studentID, courseID, grade, gradePoints, 
                                     semester, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (
                student_id,
                course_id,
                entries["grade"].get().strip(),
                entries["points"].get().strip(),
                entries["semester"].get().strip(),
                entries["status"].get().strip()
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Grade added successfully!")
                self.update_status("Grade added successfully")
            else:
                messagebox.showerror("Error", "Failed to add grade")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def update_grade(self, grade_id, entries):
        try:
            # Extract student ID from dropdown
            student_selection = entries["student_id"].get().strip()
            student_id = student_selection.split(" - ")[0] if student_selection else ""
            
            # Extract course ID from dropdown
            course_selection = entries["course_id"].get().strip()
            course_id = course_selection.split(" - ")[0] if course_selection else ""
            
            query = """
                UPDATE tblGrade
                SET studentID=?, courseID=?, grade=?, gradePoints=?, 
                    semester=?, status=?
                WHERE gradeID=?
            """
            values = (
                student_id,
                course_id,
                entries["grade"].get().strip(),
                entries["points"].get().strip(),
                entries["semester"].get().strip(),
                entries["status"].get().strip(),
                grade_id
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Grade updated successfully!")
                self.update_status("Grade updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update grade")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_grade(self, grade_id):
        try:
            query = "DELETE FROM tblGrade WHERE gradeID=?"
            if self.db.execute_query(query, (grade_id,)):
                messagebox.showinfo("Success", "Grade deleted successfully!")
                self.update_status("Grade deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete grade")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
