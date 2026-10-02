import streamlit as st
import matplotlib
matplotlib.use("Agg")   # FIX main thread error
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data Models

class Student:
    def __init__(self, student_id, name, email):
        self.student_id = student_id
        self.name = name
        self.email = email

class Course:
    def __init__(self, course_code, course_name, credits):
        self.course_code = course_code
        self.course_name = course_name
        self.credits = credits

class Result:
    def __init__(self, student_id, course_code, grade, semester):
        self.student_id = student_id
        self.course_code = course_code
        self.grade = grade
        self.semester = semester

# Session State

if 'students' not in st.session_state:
    st.session_state.students = []
if 'courses' not in st.session_state:
    st.session_state.courses = []
if 'results' not in st.session_state:
    st.session_state.results = []

# Data Management

def add_student(student_id, name, email):
    if any(s.student_id == student_id for s in st.session_state.students):
        return "Student ID already exists."
    st.session_state.students.append(Student(student_id, name, email))
    return "Student added successfully."

def add_course(course_code, course_name, credits):
    if any(c.course_code == course_code for c in st.session_state.courses):
        return "Course code already exists."
    st.session_state.courses.append(Course(course_code, course_name, credits))
    return "Course added successfully."

def add_result(student_id, course_code, grade, semester):
    if not any(s.student_id == student_id for s in st.session_state.students):
        return "Student not found."
    if not any(c.course_code == course_code for c in st.session_state.courses):
        return "Course not found."
    st.session_state.results.append(Result(student_id, course_code, grade, semester))
    return "Result added successfully."

def get_student_results(student_id):
    return [r for r in st.session_state.results if r.student_id == student_id]

# Visualization Logic

GRADE_MAP = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
    "F": 1
}

def plot_grade_distribution():
    grades = [r.grade for r in st.session_state.results]
    if not grades:
        st.warning("No results to visualize.")
        return

    grade_counts = pd.Series(grades).value_counts()

    fig, ax = plt.subplots()
    ax.bar(grade_counts.index, grade_counts.values)
    ax.set_title('Grade Distribution')
    ax.set_xlabel('Grade')
    ax.set_ylabel('Count')
    st.pyplot(fig)
    plt.close(fig)

def plot_average_grades_per_course():
    course_grades = {}

    for r in st.session_state.results:
        if r.course_code not in course_grades:
            course_grades[r.course_code] = []
        course_grades[r.course_code].append(GRADE_MAP[r.grade])

    if not course_grades:
        st.warning("No results to visualize.")
        return

    averages = {course: np.mean(grades) for course, grades in course_grades.items()}

    fig, ax = plt.subplots()
    ax.bar(averages.keys(), averages.values())
    ax.set_title('Average Grades per Course')
    ax.set_xlabel('Course Code')
    ax.set_ylabel('Average Grade Score')
    st.pyplot(fig)
    plt.close(fig)

# CSV Export Function

def generate_results_csv():
    if not st.session_state.results:
        return None

    data = []

    for r in st.session_state.results:
        student = next((s for s in st.session_state.students if s.student_id == r.student_id), None)
        course = next((c for c in st.session_state.courses if c.course_code == r.course_code), None)

        if student and course:
            data.append({
                "Student ID": student.student_id,
                "Student Name": student.name,
                "Course Name": course.course_name,
                "Grade": r.grade,
                "Semester": r.semester
            })

    df = pd.DataFrame(data)
    return df

# Streamlit UI
st.title("🎓 College Result Management & Visualization System")

menu = st.sidebar.selectbox("Menu", [
    "Add Student",
    "Add Course",
    "Add Result",
    "View Results",
    "Visualizations"
])

# Add Student
if menu == "Add Student":
    st.header("Add Student")
    student_id = st.text_input("Student ID")
    name = st.text_input("Name")
    email = st.text_input("Email")

    if st.button("Add Student"):
        if student_id and name and email:
            message = add_student(student_id, name, email)
            st.success(message)
        else:
            st.error("Please fill all fields")

# Add Course
elif menu == "Add Course":
    st.header("Add Course")
    course_code = st.text_input("Course Code")
    course_name = st.text_input("Course Name")
    credits = st.number_input("Credits", min_value=1, step=1)

    if st.button("Add Course"):
        if course_code and course_name:
            message = add_course(course_code, course_name, credits)
            st.success(message)
        else:
            st.error("Please fill all fields")

# Add Result

elif menu == "Add Result":
    st.header("Add Result")

    if not st.session_state.students or not st.session_state.courses:
        st.warning("Please add students and courses first.")
    else:
        student_id = st.selectbox("Student ID", [s.student_id for s in st.session_state.students])
        course_code = st.selectbox("Course Code", [c.course_code for c in st.session_state.courses])
        grade = st.selectbox("Grade", ['A', 'B', 'C', 'D', 'F'])
        semester = st.text_input("Semester")

        if st.button("Add Result"):
            if semester:
                message = add_result(student_id, course_code, grade, semester)
                st.success(message)
            else:
                st.error("Please enter semester")

# View Results

elif menu == "View Results":
    st.header("View Results")

    if not st.session_state.students:
        st.warning("No students available.")
    else:
        student_id = st.selectbox("Select Student ID", [s.student_id for s in st.session_state.students])

        if student_id:
            student_results = get_student_results(student_id)

            if student_results:
                table_data = []
                for r in student_results:
                    table_data.append({
                        "Course": r.course_code,
                        "Grade": r.grade,
                        "Semester": r.semester
                    })
                st.table(table_data)
            else:
                st.info("No results found for this student.")

# Visualizations 

elif menu == "Visualizations":
    st.header("Visualizations")

    if not st.session_state.results:
        st.warning("No data available for visualization.")
    else:
        viz_type = st.selectbox("Select Option", [
            "Grade Distribution",
            "Average Grades per Course",
            "Export CSV"
        ])

        if viz_type == "Grade Distribution":
            plot_grade_distribution()

        elif viz_type == "Average Grades per Course":
            plot_average_grades_per_course()

        elif viz_type == "Export CSV":
            st.subheader("📁 Download All Students Results CSV")

            df = generate_results_csv()

            if df is not None:
                csv = df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="📥 Download CSV File",
                    data=csv,
                    file_name="all_students_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results available.")


# streamlit run python_project_v2.1.py

