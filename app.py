import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
import base64
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO

# ------------------ PDF Report Generator ------------------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
    pdf.cell(200, 10, txt=f"Skills: {skills}", ln=True)
    pdf.ln(5)

    pdf.set_text_color(0, 128, 0)
    pdf.cell(200, 10, txt=f"Matched Skills: {', '.join(matched_skills)}", ln=True)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(200, 10, txt=f"Missing Skills: {', '.join(missing_skills)}", ln=True)
    pdf.set_text_color(0, 0, 0)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# ------------------ Helper Functions ------------------
def extract_text_from_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else "N/A"

def extract_name(text):
    lines = text.strip().split('\n')
    return lines[0] if lines else "N/A"

def extract_experience(text):
    match = re.search(r"(\d+)\+?\s+years", text.lower())
    return int(match.group(1)) if match else 0

def match_skills(resume_text, jd_text):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()
    jd_skills = re.findall(r"[a-zA-Z0-9\+\#\.]+", jd_text)
    matched = [skill for skill in jd_skills if skill in resume_text]
    missing = [skill for skill in jd_skills if skill not in resume_text]
    return matched, missing

def get_match_score(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

# ------------------ Streamlit App ------------------
st.set_page_config(page_title="SmartHire Resume Screener", layout="wide")
st.title("🧠 SmartHire: AI Resume Screener")

with st.sidebar:
    st.header("⚙️ Settings")
    dark_mode = st.checkbox("🌙 Dark Mode")
    st.markdown("---")
    must_have_skills = st.text_input("Must-Have Skills (comma-separated)").lower().split(',')
    min_experience = st.slider("Minimum Experience (years)", 0, 20, 0)
    st.markdown("---")
    jd_input = st.text_area("Paste Job Description (JD)", height=200)

if dark_mode:
    st.markdown("""<style>body { background-color: #0e1117; color: white; }</style>""", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload Resume PDFs (1 or more)", type="pdf", accept_multiple_files=True)

if uploaded_files and jd_input:
    results = []
    for uploaded_file in uploaded_files:
        resume_text = extract_text_from_pdf(uploaded_file)
        email = extract_email(resume_text)
        name = extract_name(resume_text)
        experience = extract_experience(resume_text)
        matched_skills, missing_skills = match_skills(resume_text, jd_input)
        match_score = get_match_score(resume_text, jd_input)

        if experience >= min_experience and all(skill in resume_text for skill in must_have_skills if skill):
            results.append({
                "Name": name,
                "Email": email,
                "Experience": experience,
                "Match %": match_score,
                "Matched Skills": matched_skills,
                "Missing Skills": missing_skills,
                "Resume Text": resume_text,
                "PDF": uploaded_file
            })

    if results:
        st.subheader("📊 Ranked Results")
        sorted_results = sorted(results, key=lambda x: x["Match %"], reverse=True)
        for i, res in enumerate(sorted_results):
            with st.expander(f"{i+1}. {res['Name']} ({res['Match %']}%)"):
                st.markdown(f"**Email:** {res['Email']}")
                st.markdown(f"**Experience:** {res['Experience']} years")
                st.markdown(f"**Matched Skills:** {', '.join(res['Matched Skills'])}")
                st.markdown(f"**Missing Skills:** {', '.join(res['Missing Skills'])}")

                st.markdown("**Visual Match %:**")
                st.progress(res['Match %'] / 100)

                if st.button(f"📥 Download Report - {res['Name']}", key=f"btn_{i}"):
                    pdf_bytes = generate_pdf(res['Name'], res['Email'], res['Experience'], ', '.join(res['Matched Skills'] + res['Missing Skills']), res['Matched Skills'], res['Missing Skills'])
                    b64 = base64.b64encode(pdf_bytes.read()).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{res["Name"]}_report.pdf">Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("No resumes met the criteria.")
else:
    st.info("Please upload at least one resume and paste the job description.")