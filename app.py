import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
import base64

# ---------- PDF Report Generator ----------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills, job_title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Job Title: {job_title}", ln=True)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Skills: {', '.join(skills)}", ln=True)
    pdf.cell(200, 10, txt=f"Matched Skills: {', '.join(matched_skills)}", ln=True)
    pdf.cell(200, 10, txt=f"Missing Skills: {', '.join(missing_skills)}", ln=True)

    file_name = f"{name.replace(' ', '_')}_screening_report.pdf"
    pdf.output(file_name)
    return file_name

# ---------- Skill Set ----------
COMMON_SKILLS = {
    'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js',
    'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql', 'git',
    'github', 'flask', 'django', 'tensorflow', 'keras', 'api', 'data analysis',
    'data visualization', 'communication', 'problem solving', 'cloud', 'aws',
    'azure', 'docker', 'kubernetes'
}

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Resume Screener", layout="centered")
st.title("📄 AI Resume Screening Tool")
st.markdown("Upload PDF resumes and job description (JD) to get a match score.")

# ---------- Sidebar Filters ----------
st.sidebar.header("🔍 Filter Settings")
min_exp = st.sidebar.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0)
must_have_skills = st.sidebar.text_input("Must-Have Skills (comma-separated)", value="")
must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]

# ---------- Inputs ----------
job_title = st.text_input("🧑‍💼 Enter Job Title", value="e.g. Software Engineer")
uploaded_files = st.file_uploader("📎 Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
jd_input = st.text_area("📄 Paste the Job Description here", height=200)

# ---------- Helper Functions ----------
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()

def extract_skills(text):
    found_skills = set()
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text):
            found_skills.add(skill)
    return found_skills

# ---------- Resume Processing ----------
if st.button("🔍 Analyze Resumes") and uploaded_files and jd_input:
    jd_text = jd_input.lower()
    jd_skills = extract_skills(jd_text)

    for uploaded_file in uploaded_files:
        with st.spinner(f"Analyzing {uploaded_file.name}..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            resume_skills = extract_skills(resume_text)

            matched_skills = resume_skills & jd_skills
            missing_skills = jd_skills - resume_skills
            match_percent = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0

            # Dummy parsed resume data
            parsed_data = {
                "name": "John Doe",
                "email": "john@example.com",
                "experience_years": 2,
                "skills": list(resume_skills)
            }

            st.subheader(f