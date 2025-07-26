import streamlit as st 
import fitz  # PyMuPDF 
import re 
from fpdf import FPDF 
import base64 
from io import BytesIO 
import matplotlib.pyplot as plt 
import numpy as np

------------------ PDF Report Generator ------------------

def generate_pdf(name, email, experience, skills, matched_skills, missing_skills): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
pdf.ln(10)
pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
pdf.ln(5)
pdf.cell(200, 10, txt=f"Skills: {', '.join(skills)}", ln=True)
pdf.cell(200, 10, txt=f"Matched Skills: {', '.join(matched_skills)}", ln=True)
pdf.cell(200, 10, txt=f"Missing Skills: {', '.join(missing_skills)}", ln=True)

pdf_output = BytesIO()
pdf.output(pdf_output)
return pdf_output.getvalue()

------------------ Common Skills ------------------

COMMON_SKILLS = { 'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js', 'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql', 'git', 'github', 'flask', 'django', 'tensorflow', 'keras', 'api', 'data analysis', 'data visualization', 'communication', 'problem solving', 'cloud', 'aws', 'azure', 'docker', 'kubernetes' }

------------------ Page Setup ------------------

st.set_page_config(page_title="SmartHire Resume Screener", layout="centered")

------------------ Dark Mode Toggle ------------------

dark_mode = st.sidebar.checkbox("🌙 Dark Mode") if dark_mode: st.markdown(""" <style> body { background-color: #1e1e1e; color: white; } .reportview-container .markdown-text-container { color: white; } .sidebar .sidebar-content { background-color: #2c2c2c; } </style> """, unsafe_allow_html=True)

st.markdown(""" <style> .block-container { padding-top: 2rem; padding-bottom: 2rem; } .stButton > button { background-color: #2e8b57; color: white; } </style> """, unsafe_allow_html=True)

------------------ Header ------------------

st.markdown("<h1 style='text-align: center; color: #2e8b57;'>🧠 SmartHire Resume Screener</h1>", unsafe_allow_html=True) st.markdown("<p style='text-align: center;'>Upload resume(s) & JD to get instant skill match insights</p>", unsafe_allow_html=True) st.markdown("---")

------------------ Sidebar Filters ------------------

st.sidebar.header("🔍 Filter Settings") min_exp = st.sidebar.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0) must_have_skills = st.sidebar.text_input("Must-Have Skills (comma-separated)", value="") must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]

------------------ Uploads ------------------

resume_files = st.file_uploader("📎 Upload one or more Resumes (PDF only)", type=["pdf"], accept_multiple_files=True) jd_input = st.text_area("📄 Paste the Job Description here", height=200)

------------------ Helper Functions ------------------

def extract_text_from_pdf(file): doc = fitz.open(stream=file.read(), filetype="pdf") text = "" for page in doc: text += page.get_text() return text.lower()

def extract_skills(text): found_skills = set() for skill in COMMON_SKILLS: pattern = r'\b' + re.escape(skill.lower()) + r'\b' if re.search(pattern, text): found_skills.add(skill) return found_skills

def extract_email(text): match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text) return match.group() if match else "not_found@example.com"

def plot_match_bar(score): fig, ax = plt.subplots(figsize=(4, 0.4)) ax.barh([""], [score], color="#2e8b57") ax.set_xlim(0, 100) ax.set_xticks([]) ax.set_yticks([]) for spine in ax.spines.values(): spine.set_visible(False) st.pyplot(fig)

------------------ Analysis ------------------

if st.button("🔍 Analyze Match") and resume_files and jd_input: with st.spinner("Analyzing all resumes..."): jd_text = jd_input.lower() jd_skills = extract_skills(jd_text)

all_results = []

    for uploaded_file in resume_files:
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_skills = extract_skills(resume_text)
        matched_skills = resume_skills & jd_skills
        missing_skills = jd_skills - resume_skills
        match_percent = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0
        email = extract_email(resume_text)

        all_results.append({
            "name": uploaded_file.name.replace(".pdf", ""),
            "email": email,
            "experience_years": 2,  # Placeholder
            "skills": list(resume_skills),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "score": match_percent
        })

    all_results.sort(key=lambda x: x["score"], reverse=True)

    st.subheader("📊 Ranked Resume Results")
    for res in all_results:
        st.markdown(f"### 🧾 {res['name']}")
        st.write(f"📧 Email: {res['email']}")
        st.write(f"🎯 Match Score: {res['score']}%")
        plot_match_bar(res['score'])
        st.success(f"✅ Matched Skills: {', '.join(res['matched_skills']) or 'None'}")
        st.warning(f"❌ Missing Skills: {', '.join(res['missing_skills']) or 'None'}")

        if res['experience_years'] < min_exp:
            st.error(f"❌ Only {res['experience_years']} years of experience. Required: {min_exp}")
        else:
            st.success(f"✅ Experience requirement met: {res['experience_years']} years")

        must_have_matched = [s for s in must_have_skills_list if s in res['skills']]
        must_have_missing = [s for s in must_have_skills_list if s not in res['skills']]
        st.info("⭐ Must-Have Skills Match:")
        st.write("✅ Matched:", must_have_matched)
        st.write("❌ Missing:", must_have_missing)

        if st.button(f"📥 Download Report for {res['name']}", key=f"download_{res['name']}"):
            pdf_bytes = generate_pdf(
                res['name'], res['email'], res['experience_years'], res['skills'], must_have_matched, must_have_missing
            )
            b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{res["name"].replace(" ", "_")}_SmartHire_Report.pdf">📄 Click here to download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

            if res['score'] >= 70:
                st.balloons()
                st.success("🎯 Great match! Ready to apply.")
            elif res['score'] >= 40:
                st.warning("⚠️ Decent match. Improve your resume.")
            else:
                st.error("❌ Low match. Align your resume with the JD.")

