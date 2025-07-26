import streamlit as st
import fitz  # PyMuPDF
import re
import base64
from fpdf import FPDF
from io import BytesIO
import os
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from PIL import Image

# ------------------ Branding: Logo & Theme ------------------
st.set_page_config(page_title="SmartHire Resume Screener", layout="wide")

# Add custom logo
logo_path = "logo.png"  # You can upload your own logo.png
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=150)

# Add theme toggle
theme = st.sidebar.selectbox("Choose Theme", ["Default", "Light", "Dark", "Blue"])

if theme == "Light":
    st.markdown("""
        <style>
        body { background-color: #f9f9f9; color: #000; }
        .stButton button { background-color: #4CAF50; color: white; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #1E1E1E; color: #f1f1f1; }
        .stButton button { background-color: #333; color: white; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""
        <style>
        body { background-color: #e8f0fe; color: #000; }
        .stButton button { background-color: #4285F4; color: white; }
        </style>
    """, unsafe_allow_html=True)

st.title("📄 SmartHire Resume Screener")
st.markdown("""
A smart AI-powered app to screen multiple resumes and match them with a job description.
Upload resumes, filter by skills/experience/title/location, view matching percentage, and download report.
""")

# ---------------------- Branding Header ----------------------
st.set_page_config(page_title="SmartHire Resume Screener", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }
    .reportview-container .markdown-text-container {
        padding-top: 0rem;
    }
    .logo {
        width: 100px;
        margin-bottom: 10px;
    }
    </style>
    <div style='display: flex; align-items: center;'>
        <img class='logo' src='https://i.imgur.com/YOUR_LOGO_URL.png'>
        <h2 style='margin-left: 20px;'>SmartHire Resume Screener</h2>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("Filters")

# ------------------ File Uploads ------------------
job_description = st.text_area("Paste the Job Description")
resume_files = st.file_uploader("Upload Resume PDFs", type="pdf", accept_multiple_files=True)

must_have_skills_input = st.sidebar.text_input("Must-Have Skills (comma-separated)")
must_have_skills = [skill.strip().lower() for skill in must_have_skills_input.split(",") if skill.strip()]

min_experience = st.sidebar.slider("Minimum Experience (Years)", 0, 20, 0)
filter_job_title = st.sidebar.text_input("Filter by Job Title (optional)")
filter_location = st.sidebar.text_input("Filter by Location (optional)")

# ------------------ Extract Resume Text ------------------
def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

# ------------------ Skill Matching ------------------
def get_match_percentage(jd, resume):
    vectorizer = TfidfVectorizer().fit_transform([jd, resume])
    vectors = vectorizer.toarray()
    score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return round(score * 100, 2)

# ------------------ Skill Extraction ------------------
def extract_skills(text):
    words = re.findall(r"\b\w+\b", text.lower())
    return list(set(words))

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group() if match else "Not Found"

def extract_experience(text):
    match = re.search(r"(\d+)(\+)?\s+(years|yrs)\s+(of)?\s+(experience)?", text.lower())
    return int(match.group(1)) if match else 0

# ------------------ PDF Report Generator ------------------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
    pdf.ln(5)
    pdf.multi_cell(200, 10, txt=f"Skills: {', '.join(skills)}")
    pdf.multi_cell(200, 10, txt=f"Matched Skills: {', '.join(matched_skills)}")
    pdf.multi_cell(200, 10, txt=f"Missing Skills: {', '.join(missing_skills)}")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# ------------------ Screening Logic ------------------
results = []
if resume_files and job_description:
    for resume in resume_files:
        resume_text = extract_text_from_pdf(resume)
        email = extract_email(resume_text)
        experience = extract_experience(resume_text)
        skills = extract_skills(resume_text)

        matched_skills = [skill for skill in must_have_skills if skill in skills]
        missing_skills = [skill for skill in must_have_skills if skill not in skills]

        if experience >= min_experience:
            if filter_job_title and filter_job_title.lower() not in resume_text.lower():
                continue
            if filter_location and filter_location.lower() not in resume_text.lower():
                continue

            match_score = get_match_percentage(job_description, resume_text)
            result = {
                "Name": resume.name.replace(".pdf", ""),
                "Email": email,
                "Experience": experience,
                "Score": match_score,
                "Matched Skills": matched_skills,
                "Missing Skills": missing_skills,
                "Skills": skills,
                "Report": generate_pdf(resume.name, email, experience, skills, matched_skills, missing_skills)
            }
            results.append(result)

# ------------------ Display Results ------------------
if results:
    st.success(f"{len(results)} Resumes matched the criteria.")

    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    st.dataframe(df[["Name", "Email", "Experience", "Score"]])

    for res in results:
        with st.expander(f"{res['Name']} - {res['Score']}% Match"):
            st.markdown(f"**Email:** {res['Email']}")
            st.markdown(f"**Experience:** {res['Experience']} years")
            st.markdown(f"**Matched Skills:** {', '.join(res['Matched Skills'])}")
            st.markdown(f"**Missing Skills:** {', '.join(res['Missing Skills'])}")
            st.download_button(
                label="Download PDF Report",
                data=res['Report'],
                file_name=f"{res['Name']}_report.pdf",
                mime="application/pdf"
            )
else:
    st.info("Upload resumes and job description to begin screening.") 