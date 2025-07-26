import streamlit as st
import fitz  # PyMuPDF
import re
import base64
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="SmartHire Resume Screener", layout="centered")

# ----------------- DARK MODE -----------------
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🤖 SmartHire Resume Screener</h1>
    <p style='text-align: center;'>Upload multiple resumes, rank by match, and download PDF reports</p>
    <hr style='border: 1px solid #4CAF50;'>
""", unsafe_allow_html=True)

# ----------------- PDF PARSING FUNCTION -----------------
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# ----------------- PDF REPORT GENERATION -----------------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills, match_percent):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_text_color(0, 102, 204)
    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")  
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience}", ln=True)
    pdf.cell(200, 10, txt=f"Match Percentage: {match_percent}%", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, txt=f"Matched Skills: {', '.join(matched_skills)}")
    pdf.multi_cell(0, 10, txt=f"Missing Skills: {', '.join(missing_skills)}")

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

# ----------------- SKILL MATCHING FUNCTION -----------------
def analyze_resume(text, job_description):
    jd_skills = re.findall(r"\b[A-Za-z\+\#]{2,}\b", job_description)
    resume_skills = re.findall(r"\b[A-Za-z\+\#]{2,}\b", text)

    jd_skills_set = set(skill.lower() for skill in jd_skills)
    resume_skills_set = set(skill.lower() for skill in resume_skills)

    matched = jd_skills_set & resume_skills_set
    missing = jd_skills_set - resume_skills_set
    match_percent = round((len(matched) / len(jd_skills_set)) * 100, 2) if jd_skills_set else 0

    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    email = email_match.group() if email_match else "Not Found"

    name_match = re.search(r"(?i)(Name)[:\- ]+([A-Za-z ]+)", text)
    name = name_match.group(2).strip() if name_match else "Not Found"

    exp_match = re.search(r"(\d+)\+?\s*(years|yrs)", text, re.I)
    experience = exp_match.group(1) + " years" if exp_match else "Not Found"

    return name, email, experience, resume_skills_set, matched, missing, match_percent

# ----------------- INPUT SECTION -----------------
st.subheader("📑 Upload Resumes")
uploaded_files = st.file_uploader("Upload one or more resumes (PDF)", type="pdf", accept_multiple_files=True)

job_description = st.text_area("💼 Paste Job Description", height=200)

# ----------------- ANALYSIS -----------------
if uploaded_files and job_description:
    results = []

    for uploaded_file in uploaded_files:
        resume_text = extract_text_from_pdf(uploaded_file)
        name, email, experience, skills, matched, missing, match_percent = analyze_resume(resume_text, job_description)

        results.append({
            "name": name,
            "email": email,
            "experience": experience,
            "skills": skills,
            "matched": matched,
            "missing": missing,
            "match_percent": match_percent,
            "filename": uploaded_file.name
        })

    # ----------------- RANKING -----------------
    sorted_results = sorted(results, key=lambda x: x["match_percent"], reverse=True)

    st.subheader("🏆 Resume Rankings")
    for i, res in enumerate(sorted_results):
        st.markdown(f"### {i+1}. {res['name']} ({res['match_percent']}%)")
        st.markdown(f"📧 **Email:** {res['email']} | 🧠 **Experience:** {res['experience']}")

        st.progress(res['match_percent'] / 100)

        st.markdown(f"✅ **Matched Skills:** {', '.join(res['matched']) if res['matched'] else 'None'}")
        st.markdown(f"❌ **Missing Skills:** {', '.join(res['missing']) if res['missing'] else 'None'}")

        pdf_bytes = generate_pdf(
            res['name'], res['email'], res['experience'], list(res['skills']),
            res['matched'], res['missing'], res['match_percent']
        )
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{res["name"]}_SmartHire_Report.pdf">📥 Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)

        st.markdown("---")

else:
    st.info("👆 Please upload at least one resume and paste the job description to begin analysis.")
