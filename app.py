import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
import base64
from io import BytesIO

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
    pdf.cell(200, 10, txt=f"Skills: {', '.join(skills)}", ln=True)
    pdf.cell(200, 10, txt=f"Matched Skills: {', '.join(matched_skills)}", ln=True)
    pdf.cell(200, 10, txt=f"Missing Skills: {', '.join(missing_skills)}", ln=True)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()

# ------------------ Common Skills ------------------
COMMON_SKILLS = {
    'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js',
    'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql',
    'git', 'github', 'flask', 'django', 'tensorflow', 'keras', 'api',
    'data analysis', 'data visualization', 'communication', 'problem solving',
    'cloud', 'aws', 'azure', 'docker', 'kubernetes'
}

# ------------------ Page Setup ------------------
st.set_page_config(page_title="SmartHire Resume Screener", layout="centered")
st.markdown("""
    <style>
    .reportview-container {
        background-color: #f7f9fc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton > button {
        background-color: #2e8b57;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
st.markdown("<h1 style='text-align: center; color: #2e8b57;'>🧠 SmartHire Resume Screener</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload resume & JD to get instant skill match insights</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------ Sidebar Filters ------------------
st.sidebar.header("🔍 Filter Settings")
min_exp = st.sidebar.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0)
must_have_skills = st.sidebar.text_input("Must-Have Skills (comma-separated)", value="")
must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]

# ------------------ Uploads ------------------
resume_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"])
jd_input = st.text_area("📄 Paste the Job Description here", height=200)

# ------------------ Helper Functions ------------------
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

# ------------------ Analysis ------------------
resume_skills = set()
match_percent = 0
matched_skills = []
missing_skills = []

if st.button("🔍 Analyze Match") and resume_file and jd_input:
    with st.spinner("Extracting text and matching skills..."):
        resume_text = extract_text_from_pdf(resume_file)
        jd_text = jd_input.lower()

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched_skills = resume_skills & jd_skills
        missing_skills = jd_skills - resume_skills
        match_percent = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0

        st.subheader("✅ Match Results")
        st.success(f"**Match Score:** {match_percent}%")
        st.info(f"**Skills in JD:** {', '.join(sorted(jd_skills))}")
        st.success(f"**Matched Skills:** {', '.join(sorted(matched_skills)) or 'None'}")
        st.warning(f"**Missing Skills:** {', '.join(sorted(missing_skills)) or 'None'}")

# ------------------ Parsed Resume Data ------------------
resume_skills = resume_skills if 'resume_skills' in locals() else set()
parsed_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "experience_years": 2,
    "skills": list(resume_skills)
}

# ------------------ Experience & Must-Have Filters ------------------
if parsed_data['experience_years'] < min_exp:
    st.warning(f"❌ Candidate has only {parsed_data['experience_years']} years experience. Required: {min_exp}")
else:
    st.success(f"✅ Experience requirement met: {parsed_data['experience_years']} years")

must_have_matched = [s for s in must_have_skills_list if s in parsed_data['skills']]
must_have_missing = [s for s in must_have_skills_list if s not in parsed_data['skills']]

st.subheader("⭐ Must-Have Skills Match:")
st.success("✅ Matched: " + ", ".join(must_have_matched) if must_have_matched else "None")
st.error("❌ Missing: " + ", ".join(must_have_missing) if must_have_missing else "None")

# ------------------ Download PDF Report ------------------
if st.button(f"📥 Download Report for {parsed_data['name']}", key=f"download_{parsed_data['name']}"):
    pdf_bytes = generate_pdf(
        parsed_data['name'],
        parsed_data['email'],
        parsed_data['experience_years'],
        parsed_data['skills'],
        must_have_matched,
        must_have_missing
    )
    b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{parsed_data["name"].replace(" ", "_")}_SmartHire_Report.pdf">📄 Click here to download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Recommendation
    if match_percent >= 70:
        st.balloons()
        st.success("Great match! 🎯 You’re ready to apply.")
    elif match_percent >= 40:
        st.warning("Decent match. Consider improving your resume.")
    else:
        st.error("Low match. Try aligning your resume better with the JD.")