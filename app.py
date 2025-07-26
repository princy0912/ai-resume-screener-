import streamlit as st 
import fitz  # PyMuPDF 
import re 
from fpdf import FPDF 
from io import BytesIO 
import base64 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import pdfminer 
from sklearn.feature_extraction.text import TfidfVectorizer from sklearn.metrics.pairwise import cosine_similarity

------------------ PDF Report Generator ------------------

def generate_pdf(name, email, experience, skills, matched_skills, missing_skills): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")  
pdf.ln(10)

pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
pdf.ln(5)

pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, txt="Matched Skills:", ln=True)
pdf.set_font("Arial", size=12)
for skill in matched_skills:
    pdf.cell(200, 10, txt=f"- {skill}", ln=True)

pdf.ln(5)
pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, txt="Missing Skills:", ln=True)
pdf.set_font("Arial", size=12)
for skill in missing_skills:
    pdf.cell(200, 10, txt=f"- {skill}", ln=True)

pdf_output = BytesIO()
pdf.output(pdf_output)
pdf_output.seek(0)
return pdf_output

------------------ Resume Text Extraction ------------------

def extract_text_from_pdf(uploaded_file): doc = fitz.open(stream=uploaded_file.read(), filetype="pdf") text = "" for page in doc: text += page.get_text() return text

------------------ Email Parser ------------------

def extract_email(text): match = re.search(r"[\w.-]+@[\w.-]+", text) return match.group(0) if match else "Not Found"

------------------ Skill Matching ------------------

def match_skills(jd_skills, resume_text): resume_text_lower = resume_text.lower() matched = [skill for skill in jd_skills if skill.lower() in resume_text_lower] missing = [skill for skill in jd_skills if skill.lower() not in resume_text_lower] return matched, missing

------------------ Experience Extraction ------------------

def extract_experience(text): exp_match = re.search(r'(\d+)\s*+?\s*(years|yrs)', text.lower()) if exp_match: return int(exp_match.group(1)) return 0

------------------ Skill Match Percentage ------------------

def get_match_percentage(matched_skills, total_skills): if not total_skills: return 0 return round(len(matched_skills) / len(total_skills) * 100)

------------------ Streamlit UI ------------------

st.set_page_config(page_title="SmartHire Resume Screener", layout="wide") st.title("🤖 SmartHire AI Resume Screener")

Dark mode toggle

is_dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False) if is_dark_mode: st.markdown(""" <style> body, .stApp { background-color: #121212; color: white; } .stTextInput>div>div>input { background-color: #333; color: white; } </style> """, unsafe_allow_html=True)

st.sidebar.header("Upload & JD") job_title = st.sidebar.text_input("Job Title") jd_input = st.sidebar.text_area("Paste Job Description") must_have_skills_input = st.sidebar.text_input("Must-Have Skills (comma-separated)") experience_required = st.sidebar.slider("Minimum Experience Required (years)", 0, 15, 1)

uploaded_files = st.sidebar.file_uploader("Upload Resume PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files and jd_input: jd_skills = [skill.strip() for skill in must_have_skills_input.split(",") if skill.strip()] resume_data = []

for uploaded_file in uploaded_files:
    resume_text = extract_text_from_pdf(uploaded_file)
    name = uploaded_file.name.replace(".pdf", "")
    email = extract_email(resume_text)
    experience = extract_experience(resume_text)
    matched_skills, missing_skills = match_skills(jd_skills, resume_text)
    match_percent = get_match_percentage(matched_skills, jd_skills)

    resume_data.append({
        "name": name,
        "email": email,
        "experience": experience,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percent": match_percent,
        "resume_text": resume_text
    })

# Rank by match percentage
ranked_data = sorted(resume_data, key=lambda x: x['match_percent'], reverse=True)

st.subheader("📊 Ranked Resume Matches")
for i, data in enumerate(ranked_data):
    with st.expander(f"{i+1}. {data['name']} ({data['match_percent']}% Match)"):
        st.markdown(f"**Email:** {data['email']}")
        st.markdown(f"**Experience:** {data['experience']} years")

        st.markdown("**Skill Match:**")
        fig, ax = plt.subplots(figsize=(5, 0.4))
        ax.barh([0], [data['match_percent']], color="#00c853")
        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xticks([0, 50, 100])
        ax.set_title(f"{data['match_percent']}%", fontsize=10, loc="left")
        st.pyplot(fig)

        st.markdown("**Matched Skills:** " + ", ".join(data['matched_skills']) if data['matched_skills'] else "None")
        st.markdown("**Missing Skills:** " + ", ".join(data['missing_skills']) if data['missing_skills'] else "None")

        pdf_report = generate_pdf(data['name'], data['email'], data['experience'], jd_skills, data['matched_skills'], data['missing_skills'])
        b64 = base64.b64encode(pdf_report.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{data["name"]}_report.pdf">📄 Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)

st.balloons()

else: st.info("👆 Upload resumes and paste job description to begin.")

