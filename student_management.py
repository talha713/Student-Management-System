import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# Initialize session states
if 'students' not in st.session_state:
    st.session_state.students = []
if 'classes' not in st.session_state:
    st.session_state.classes = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
if 'filtered_students' not in st.session_state:
    st.session_state.filtered_students = []

# Function to generate unique ID
def generate_id():
    return uuid.uuid4().hex

# Function to download CSV
def download_csv(data):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f'students_{current_time}.csv',
        mime='text/csv',
    )

# Main App
st.title("Student Management System")

# Class Management
with st.expander("Manage Classes"):
    # Add Class Form
    with st.form("add_class"):
        cols = st.columns([4,1])
        new_class = cols[0].text_input("Add New Class")
        submitted = cols[1].form_submit_button("➕ Add")
        if submitted and new_class:
            new_class = new_class.strip()
            if new_class not in st.session_state.classes:
                st.session_state.classes.append(new_class)
                st.success(f"Class '{new_class}' added successfully!")
            else:
                st.error("Class already exists!")
    
    # Class List with Delete Buttons
    st.write("### Existing Classes")
    if not st.session_state.classes:
        st.info("No classes added yet")
    else:
        for cls in st.session_state.classes[:]:  # Iterate over copy of list
            cols = st.columns([6,1])
            cols[0].write(f"• {cls}")
            
            # Delete Class Button
            if cols[1].button("🗑️", key=f"del_cls_{cls}"):
                # Check if any student belongs to this class
                class_in_use = any(student["Class"] == cls for student in st.session_state.students)
                
                if class_in_use:
                    st.error(f"Cannot delete '{cls}' - students are enrolled in this class!")
                else:
                    st.session_state.classes.remove(cls)
                    st.rerun()

# Add Student Form
with st.expander("Add New Student"):
    with st.form("add_student", clear_on_submit=True):
        cols = st.columns(2)
        name = cols[0].text_input("Student Name*")
        father_name = cols[1].text_input("Father's Name*")
        
        if st.session_state.classes:
            student_class = cols[0].selectbox("Class*", st.session_state.classes)
        else:
            st.error("Please add classes first in the 'Manage Classes' section")
            
        phone = cols[1].text_input("Phone Number*")
        address = st.text_area("Address*")
        submitted = st.form_submit_button("Add Student")
        
        if submitted and st.session_state.classes:
            if name and father_name and student_class and phone and address:
                student = {
                    "ID": generate_id(),
                    "Name": name,
                    "Father's Name": father_name,
                    "Class": student_class,
                    "Phone": phone,
                    "Address": address,
                    "Added Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.students.append(student)
                st.success("Student added successfully!")
            else:
                st.error("Please fill all required fields (*)")

# Search Section
with st.expander("Search Students"):
    search_type = st.radio("Search by:", ["Name", "Class"])
    search_term = st.text_input(f"Enter {search_type} to search")
    
    if search_term:
        search_term = search_term.lower()
        if search_type == "Name":
            st.session_state.filtered_students = [s for s in st.session_state.students if search_term in s["Name"].lower()]
        else:
            st.session_state.filtered_students = [s for s in st.session_state.students if search_term in s["Class"].lower()]
    else:
        st.session_state.filtered_students = st.session_state.students.copy()

# Display Students
st.subheader("Student Records")

if not st.session_state.filtered_students:
    st.info("No students found")
else:
    download_csv(st.session_state.filtered_students)
    
    for student in st.session_state.filtered_students:
        cols = st.columns([3,3,2,2,3,1,1])  # Added column for Address
        cols[0].write(student["Name"])
        cols[1].write(student["Father's Name"])
        cols[2].write(student["Class"])
        cols[3].write(student["Phone"])
        cols[4].write(student["Address"])  # Address displayed directly
        
        # Edit Button
        edit_btn = cols[5].button("✏️", key=f"edit_{student['ID']}")
        if edit_btn:
            st.session_state.edit_id = student['ID']
        
        # Delete Button
        if cols[6].button("🗑️", key=f"delete_{student['ID']}"):
            st.session_state.students = [s for s in st.session_state.students if s['ID'] != student['ID']]
            st.rerun()

# Edit Student Form
if 'edit_id' in st.session_state:
    student_to_edit = next((s for s in st.session_state.students if s['ID'] == st.session_state.edit_id), None)
    if student_to_edit:
        with st.expander("Edit Student"):
            with st.form("edit_form"):
                cols = st.columns(2)
                new_name = cols[0].text_input("Name", value=student_to_edit["Name"])
                new_father_name = cols[1].text_input("Father's Name", value=student_to_edit["Father's Name"])
                
                if st.session_state.classes:
                    new_class = cols[0].selectbox(
                        "Class",
                        st.session_state.classes,
                        index=st.session_state.classes.index(student_to_edit["Class"])
                    )
                new_phone = cols[1].text_input("Phone", value=student_to_edit["Phone"])
                new_address = st.text_area("Address", value=student_to_edit["Address"])
                
                col1, col2, _ = st.columns([2,2,6])
                if col1.form_submit_button("💾 Save Changes"):
                    student_to_edit.update({
                        "Name": new_name,
                        "Father's Name": new_father_name,
                        "Class": new_class,
                        "Phone": new_phone,
                        "Address": new_address
                    })
                    del st.session_state.edit_id
                    st.rerun()
                
                if col2.form_submit_button("❌ Cancel"):
                    del st.session_state.edit_id
                    st.rerun()