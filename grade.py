# create_tables.py
import pyodbc

def create_database_tables():
    # Connect to your Access database
    db_path = r"D:\Documents\DBMS\Assignment-Python.accdb"
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Creating tables...")
        
        # ===== CREATE COURSE TABLE =====
        try:
            cursor.execute("DROP TABLE tblCourse")
            print("Dropped existing tblCourse")
        except:
            pass
        
        cursor.execute("""
            CREATE TABLE tblCourse (
                courseID AUTOINCREMENT PRIMARY KEY,
                courseCode TEXT(20) NOT NULL,
                courseName TEXT(100) NOT NULL,
                credits INTEGER,
                department TEXT(50),
                description MEMO,
                academicYear TEXT(10)
            )
        """)
        print("Created tblCourse")
        
        # ===== CREATE GRADE TABLE =====
        try:
            cursor.execute("DROP TABLE tblGrade")
            print("Dropped existing tblGrade")
        except:
            pass
        
        cursor.execute("""
            CREATE TABLE tblGrade (
                gradeID AUTOINCREMENT PRIMARY KEY,
                studentID INTEGER NOT NULL,
                courseID INTEGER NOT NULL,
                grade TEXT(5),
                gradePoints NUMBER,
                semester TEXT(20),
                enrollmentDate DATETIME,
                completionDate DATETIME,
                status TEXT(20)
            )
        """)
        print("Created tblGrade")
        
        # ===== ADD SAMPLE COURSES =====
        sample_courses = [
            ("CS101", "Introduction to Programming", 3, "Computer Science"),
            ("CS102", "Data Structures", 4, "Computer Science"),
            ("MATH101", "Calculus I", 4, "Mathematics"),
            ("MATH102", "Calculus II", 4, "Mathematics"),
            ("ENG101", "English Composition", 3, "English"),
            ("PHYS101", "Physics I", 4, "Physics"),
            ("CHEM101", "Chemistry I", 4, "Chemistry"),
            ("HIST101", "World History", 3, "History"),
            ("BUS101", "Introduction to Business", 3, "Business"),
            ("ART101", "Art Appreciation", 3, "Arts")
        ]
        
        for course in sample_courses:
            cursor.execute("""
                INSERT INTO tblCourse (courseCode, courseName, credits, department)
                VALUES (?, ?, ?, ?)
            """, course)
        print(f"Added {len(sample_courses)} sample courses")
        
        conn.commit()
        print("All tables created successfully!")
        
        # Show what was created
        cursor.execute("SELECT courseCode, courseName, credits FROM tblCourse")
        courses = cursor.fetchall()
        print("\nCourses in database:")
        for course in courses:
            print(f"  {course.courseCode}: {course.courseName} ({course.credits} credits)")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_database_tables()