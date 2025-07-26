import streamlit as st
import fitz  # PyMuPDF
import re
import base64
from fpdf import FPDF
from io import BytesIO

# ---------- PDF Report Generator ----------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills, match_percent):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
    pdf.cell(200, 10, txt=f"Match Score: {match_percent}%", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Skills: {', '.join(skills)}")
    pdf.multi_cell(0, 10, txt=f"Matched Skills: {', '.join(matched_skills)}")
    pdf.multi_cell(0, 10, txt=f"Missing Skills: {', '.join(missing_skills)}")
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer

# ---------- Skill Set ----------
COMMON_SKILLS = {
    'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js',
    'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql',
    'git', 'github', 'flask', 'django', 'tensorflow', 'keras', 'api',
    'data analysis', 'data visualization', 'communication', 'problem solving',
    'cloud', 'aws', 'azure', 'docker', 'kubernetes'
}

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.title("📄 SmartHire: AI Resume Screener")
st.markdown("Upload **multiple resumes** and a **job description** to get detailed skill match reports, ranking, and PDF downloads.")

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.header("🔍 Filter Settings")
    min_exp = st.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0)
    must_have_skills = st.text_input("Must-Have Skills (comma-separated)", value="")
    must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]

# ---------- Upload Section ----------
uploaded_resumes = st.file_uploader("📎 Upload Resume PDFs (Multiple allowed)", type="pdf", accept_multiple_files=True)
jd_input = st.text_area("🧾 Paste the Job Description Here", height=200)

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

# ---------- Analysis ----------
if st.button("🚀 Analyze All Resumes") and uploaded_resumes and jd_input:
    jd_text = jd_input.lower()
    jd_skills = extract_skills(jd_text)
    all_results = []

    for resume_file in uploaded_resumes:
        resume_text = extract_text_from_pdf(resume_file)
        resume_skills = extract_skills(resume_text)
        matched_skills = resume_skills & jd_skills
        missing_skills = jd_skills - resume_skills
        match_percent = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0

        parsed_data = {
            "name": resume_file.name.replace(".pdf", ""),
            "email": "not_found@example.com",
            "experience_years": 2,
            "skills": list(resume_skills),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "match_percent": match_percent
        }

        must_have_matched = [s for s in must_have_skills_list if s in resume_skills]
        must_have_missing = [s for s in must_have_skills_list if s not in resume_skills]
        parsed_data["must_have_matched"] = must_have_matched
        parsed_data["must_have_missing"] = must_have_missing

        all_results.append(parsed_data)

    # ---------- Ranking and Display ----------
    all_results.sort(key=lambda x: x["match_percent"], reverse=True)

    st.subheader("🏆 Resume Match Rankings")
    for idx, result in enumerate(all_results, start=1):
        with st.expander(f"#{idx}: {result['name']} ({result['match_percent']}% match)"):
            st.progress(result["match_percent"])
            st.markdown(f"**📧 Email:** {result['email']}")
            st.markdown(f"**🧠 Experience:** {result['experience_years']} years")
            st.markdown(f"**✅ Matched Skills:** {', '.join(sorted(result['matched_skills'])) or 'None'}")
            st.markdown(f"**❌ Missing Skills:** {', '.join(sorted(result['missing_skills'])) or 'None'}")
            st.markdown(f"**⭐ Must-Have Matched:** {', '.join(result['must_have_matched']) or 'None'}")
            st.markdown(f"**🚫 Must-Have Missing:** {', '.join(result['must_have_missing']) or 'None'}")

            pdf_buffer = generate_pdf(
                result['name'], result['email'], result['experience_years'],
                result['skills'], result['matched_skills'], result['missing_skills'], result['match_percent']
            )
            b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{result["name"]}_report.pdf">📥 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

    st.success("✅ All resumes analyzed and ranked successfully!")