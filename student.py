import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font

class StudentManager:
    def __init__(self, parent_frame, db_connection):
        self.parent = parent_frame
        self.db = db_connection
        self.all_items_cache = []  # Keep track of all tree items
        self.create_widgets()
    
    def create_widgets(self):
        """Create the student management interface with Treeview"""
        # Clear parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.parent, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="STUDENT MANAGEMENT", 
                font=("Arial", 16, "bold"), 
                bg="#2c3e50", fg="white").pack(side="left", padx=20, pady=10)
        
        # ========== ACTION BUTTONS ==========
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=(0, 10))
        
        # Button styles
        btn_style = {"width": 12, "height": 1, "font": ("Arial", 10)}
        
        tk.Button(btn_frame, text="Add", command=self.show_add_form,
                 bg="#27ae60", fg="white", **btn_style).grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Update", command=self.show_update_form,
                 bg="#2980b9", fg="white", **btn_style).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Search", command=self.show_search_form,
                 bg="#f39c12", fg="white", **btn_style).grid(row=0, column=2, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.show_delete_form,
                 bg="#e74c3c", fg="white", **btn_style).grid(row=0, column=3, padx=2)
        tk.Button(btn_frame, text="Sort ID", command=self.sort_by_id,
                 bg="#9b59b6", fg="white", **btn_style).grid(row=0, column=4, padx=2)
        tk.Button(btn_frame, text="Refresh", command=self.load_all_students,
                 bg="#3498db", fg="white", **btn_style).grid(row=0, column=5, padx=2)
        
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
        
        # Create vertical scrollbar
        tree_scroll_y = tk.Scrollbar(table_frame)
        tree_scroll_y.pack(side="right", fill="y")
        
        # Create horizontal scrollbar
        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Create Treeview
        self.tree = ttk.Treeview(table_frame,
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set,
                                selectmode="browse",
                                height=15)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
                
        # Define columns
        self.tree["columns"] = ("ID", "First Name", "Last Name", "Gender", 
                                "DOB", "Contact", "Address", "Major", "Status")
        
        # Format columns (widths in pixels)
        column_widths = {
            "ID": 60, "First Name": 120, "Last Name": 120, 
            "Gender": 80, "DOB": 100, "Contact": 120,
            "Address": 150, "Major": 120, "Status": 100
        }
        
        self.tree.column("#0", width=0, stretch=False)
        for col in self.tree["columns"]:
            self.tree.column(col, width=column_widths[col], minwidth=50)
            self.tree.heading(col, text=col, anchor="center")
                
                # Pack treeview
        self.tree.pack(fill="both", expand=True)
                
                # Bind double-click event
        self.tree.bind("<Double-1>", self.on_tree_double_click)
                
                # ========== STATUS BAR ==========
        self.status_frame = tk.Frame(self.parent, bg="#ecf0f1", height=30)
        self.status_frame.pack(fill="x", pady=(5, 0))
        self.status_frame.pack_propagate(False)
                
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                            bg="#ecf0f1", fg="#2c3e50")
        self.status_label.pack(side="left", padx=10)
        
        # ========== LOAD INITIAL DATA ==========
        self.load_all_students()
    
    def load_all_students(self):
        """Load all students into the Treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear cache and selection
        self.all_items_cache = []
        self.tree.selection_remove(self.tree.selection())
        
        # Fetch from database
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                    contact, address, major, status
                FROM tblStudent
                ORDER BY lastName, firstName
            """
            rows = self.db.fetch_all(query)
            
            if not rows:
                # Show empty message
                item_id = self.tree.insert("", "end", values=("No data", "", "", "", "", "", "", "", ""))
                self.all_items_cache.append(item_id)
                self.update_status("No students found in database")
                return
            
            # Insert into treeview
            for row in rows:
                # Format date
                dob = ""
                if row.dateOfbirth:
                    if hasattr(row.dateOfbirth, 'strftime'):
                        dob = row.dateOfbirth.strftime("%Y-%m-%d")
                    else:
                        dob = str(row.dateOfbirth)
                
                item_id = self.tree.insert("", "end", values=(
                    row.studentID, 
                    row.firstName or "",
                    row.lastName or "",
                    row.gender or "",
                    dob,
                    row.contact or "",
                    row.address or "",
                    row.major or "",
                    row.status or ""
                ))
                self.all_items_cache.append(item_id)
            
            # Update status
            self.update_status(f"Loaded {len(rows)} student(s)")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load students:\n{str(e)}")
            self.update_status("Error loading students", error=True)
    
    def update_status(self, message, error=False):
        """Update status bar"""
        color = "#e74c3c" if error else "#27ae60"
        self.status_label.config(text=message, fg=color)
    
    def sort_by_id(self):
        """Sort students by ID (small to big)"""
        try:
            items_data = []
            for item_id in self.all_items_cache:
                values = self.tree.item(item_id)["values"]
                if values and values[0] != "No data":
                    try:
                        student_id = int(values[0])
                        items_data.append((student_id, item_id, values))
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
        
        # Detach all items first
        for item in self.all_items_cache:
            self.tree.detach(item)
        
        if not search_term:
            # If search is empty, reattach all items
            for item in self.all_items_cache:
                self.tree.reattach(item, '', 'end')
            return
        
        # Reattach only matching items
        for item in self.all_items_cache:
            values = self.tree.item(item)["values"]
            # Convert all values to string for searching
            all_text = " ".join(str(v) for v in values).lower()
            
            if search_term in all_text:
                self.tree.reattach(item, '', 'end')
            
    def on_tree_double_click(self, event):
        """When user double-clicks a row"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            if values and values[0] != "No data":
                student_id = values[0]
                self.show_student_details(student_id)
    
    def show_student_details(self, student_id):
        """Show student details in a message box"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, major, status
                FROM tblStudent WHERE studentID=?
            """
            row = self.db.fetch_one(query, (student_id,))
            
            if row:
                # Format details
                details = f"""
                STUDENT DETAILS:
                ─────────────────
                ID: {row.studentID}
                Name: {row.firstName} {row.lastName}
                Gender: {row.gender}
                Date of Birth: {row.dateOfbirth}
                Contact: {row.contact}
                Address: {row.address}
                Major: {row.major}
                Status: {row.status}
                ─────────────────
                """
                messagebox.showinfo("Student Details", details)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get details:\n{str(e)}")
    
    # ========== FORM METHODS ==========
    
    def show_add_form(self):
        """Show form to add a new student"""
        self.show_student_form("Add New Student", self.insert_student)
    
    def show_update_form(self):
        """Show form to update a student"""
        # Get selected student from treeview
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a student from the table first.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            student_id = values[0]
            # Pre-fill form with current data
            self.show_student_form("Update Student", self.update_student, 
                                  student_id=student_id, current_values=values)
        else:
            messagebox.showwarning("Invalid Selection", "Please select a valid student.")
    
    def show_search_form(self):
        """Show advanced search form"""
        search_window = tk.Toplevel(self.parent)
        search_window.title("Search Student")
        search_window.geometry("400x300")
        search_window.transient(self.parent)
        search_window.grab_set()
    
        tk.Label(search_window, text="Search Student", 
            font=("Arial", 14, "bold")).pack(pady=10)
    
        # Search options
        search_frame = tk.Frame(search_window)
        search_frame.pack(pady=10, padx=20)
        
        tk.Label(search_frame, text="Search by:").grid(row=0, column=0, sticky="w", pady=5)
        
        search_type = tk.StringVar(value="id")
        tk.Radiobutton(search_frame, text="Student ID", variable=search_type, value="id").grid(row=1, column=0, sticky="w")
        tk.Radiobutton(search_frame, text="Name", variable=search_type, value="name").grid(row=2, column=0, sticky="w")
        
        tk.Label(search_frame, text="Search term:").grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        # Create the entry widget - THIS IS THE IMPORTANT PART
        search_entry = tk.Entry(search_frame, width=30)
        search_entry.grid(row=4, column=0, pady=5)
        
        def perform_search():
            """Inner function that can access search_entry"""
            search_text = search_entry.get().strip()  # Get text from the entry
            
            if not search_text:
                messagebox.showwarning("Empty Search", "Please enter a search term.")
                return
            
            if search_type.get() == "id":
                try:
                    sid = int(search_text)
                    result = self.search_student_by_id(sid)
                    if result:
                        messagebox.showinfo("Student Found", result)
                    else:
                        messagebox.showinfo("Not Found", "No student found with that ID.")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid numeric ID.")
            else:
                # Search by name
                self.search_student_by_name(search_text)
        
        tk.Button(search_window, text="Search", command=perform_search, width=15, bg="#3498db", fg="white").pack(pady=20)
    
    def show_delete_form(self):
        """Show delete confirmation"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a student to delete.")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        
        if values and values[0] != "No data":
            student_id = values[0]
            student_name = f"{values[1]} {values[2]}"
            
            response = messagebox.askyesno("Confirm Delete", 
                                          f"Are you sure you want to delete student:\n"
                                          f"{student_name} (ID: {student_id})?")
            if response:
                self.delete_student(student_id)
        else:
            messagebox.showwarning("Invalid Selection", "Cannot delete this row.")
    
    def show_student_form(self, title, submit_func, student_id=None, current_values=None):
        """Generic form for add/update"""
        form_window = tk.Toplevel(self.parent)
        form_window.title(title)
        form_window.geometry("500x600")
        form_window.transient(self.parent)
        form_window.grab_set()
        
        # Title
        tk.Label(form_window, text=title, 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(form_window, padx=20, pady=10)
        form_frame.pack()
        
        # Define dropdown options
        major_options = ["Computer Science", "Mathematics", "Physics", "Chemistry", 
                         "Biology", "Engineering", "Business", "History", "English", "Arts"]
        status_options = ["Active", "Inactive"]
        
        # Fields with labels and entries
        fields = [
            ("First Name:", "fname", "entry"),
            ("Last Name:", "lname", "entry"),
            ("Gender (M/F):", "gender", "entry"),
            ("Date of Birth (YYYY-MM-DD):", "dob", "entry"),
            ("Contact:", "contact", "entry"),
            ("Address:", "address", "entry"),
            ("Major:", "major", "dropdown"),
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
                if key == "major":
                    combo = ttk.Combobox(form_frame, values=major_options, width=32, state="readonly")
                else:  # status
                    combo = ttk.Combobox(form_frame, values=status_options, width=32, state="readonly")
                
                combo.grid(row=i, column=1, pady=8, padx=(10, 0))
                
                # Pre-fill if updating
                if current_values and student_id:
                    if key == "major" and len(current_values) > 7:
                        combo.set(current_values[7] or "")
                    elif key == "status" and len(current_values) > 8:
                        combo.set(current_values[8] or "")
                
                entries[key] = combo
            else:
                entry = tk.Entry(form_frame, width=35)
                entry.grid(row=i, column=1, pady=8, padx=(10, 0))
                
                # Pre-fill if updating
                if current_values and student_id:
                    if key == "fname" and len(current_values) > 1:
                        entry.insert(0, current_values[1] or "")
                    elif key == "lname" and len(current_values) > 2:
                        entry.insert(0, current_values[2] or "")
                    elif key == "gender" and len(current_values) > 3:
                        entry.insert(0, current_values[3] or "")
                    elif key == "dob" and len(current_values) > 4:
                        entry.insert(0, current_values[4] or "")
                    elif key == "contact" and len(current_values) > 5:
                        entry.insert(0, current_values[5] or "")
                    elif key == "address" and len(current_values) > 6:
                        entry.insert(0, current_values[6] or "")
                        
                entries[key] = entry
        
        # Submit button
        def submit():
            if student_id:  # Update
                submit_func(student_id, entries)
            else:  # Add
                submit_func(entries)
            form_window.destroy()
            self.load_all_students()  # Refresh the list
        
        tk.Button(form_window, text="Submit", command=submit,
                 width=15, bg="#27ae60", fg="white").pack(pady=20)
    
    # ========== DATABASE OPERATIONS ==========
    
    def insert_student(self, entries):
        """Add a new student"""
        try:
            query = """
                INSERT INTO tblStudent (firstName, lastName, gender, dateOfbirth, 
                                       contact, address, major, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                entries["fname"].get().strip(),
                entries["lname"].get().strip(),
                entries["gender"].get().strip().upper(),
                entries["dob"].get().strip(),
                entries["contact"].get().strip(),
                entries["address"].get().strip(),
                entries["major"].get().strip(),
                entries["status"].get().strip()
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Student added successfully!")
                self.update_status("Student added successfully")
            else:
                messagebox.showerror("Error", "Failed to add student")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def update_student(self, student_id, entries):
        """Update existing student"""
        try:
            query = """
                UPDATE tblStudent
                SET firstName=?, lastName=?, gender=?, dateOfbirth=?, 
                    contact=?, address=?, major=?, status=?
                WHERE studentID=?
            """
            values = (
                entries["fname"].get().strip(),
                entries["lname"].get().strip(),
                entries["gender"].get().strip().upper(),
                entries["dob"].get().strip(),
                entries["contact"].get().strip(),
                entries["address"].get().strip(),
                entries["major"].get().strip(),
                entries["status"].get().strip(),
                student_id
            )
            
            if self.db.execute_query(query, values):
                messagebox.showinfo("Success", "Student updated successfully!")
                self.update_status("Student updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update student")
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_student(self, student_id):
        """Delete a student by ID"""
        try:
            query = "DELETE FROM tblStudent WHERE studentID=?"
            if self.db.execute_query(query, (student_id,)):
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.update_status("Student deleted successfully")
                self.load_all_students()  # Refresh
            else:
                messagebox.showerror("Error", "Failed to delete student")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def search_student_by_id(self, student_id):
        """Search for a student by ID"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, major, status
                FROM tblStudent WHERE studentID=?
                """
            row = self.db.fetch_one(query, (student_id,))
            
            if row:
                return (f"ID: {row.studentID}\n"
                       f"Name: {row.firstName} {row.lastName}\n"
                       f"Gender: {row.gender}\n"
                       f"DOB: {row.dateOfbirth}\n"
                       f"Contact: {row.contact}\n"
                       f"Address: {row.address}\n"
                       f"Major: {row.major}\n"
                       f"Status: {row.status}")
            return None
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return None
    
    def search_student_by_name(self, name):
        """Search for students by name"""
        try:
            query = """
                SELECT studentID, firstName, lastName, gender, dateOfbirth, 
                       contact, address, major, status
                FROM tblStudent 
                WHERE firstName LIKE ? OR lastName LIKE ?
                ORDER BY lastName, firstName
            """
            search_pattern = f"%{name}%"
            rows = self.db.fetch_all(query, (search_pattern, search_pattern))
            
            if not rows:
                messagebox.showinfo("Search Results", "No students found with that name.")
                return
            
            # Highlight matching rows in treeview
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
            
            # Show all rows first
            self.load_all_students()
            
            # Highlight matches
            for row in rows:
                for item in self.tree.get_children():
                    values = self.tree.item(item)["values"]
                    if values and values[0] == row.studentID:
                        self.tree.selection_add(item)
                        self.tree.see(item)  # Scroll to item
                        break
            
            messagebox.showinfo("Search Results", 
                              f"Found {len(rows)} student(s) matching '{name}'")
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

