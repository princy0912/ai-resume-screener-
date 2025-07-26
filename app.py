import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
import base64
from io import BytesIO

# ----------------- Logo & Header Styling ------------------
st.markdown(
    """
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .title {
            font-size: 36px;
            color: #0e4d92;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #333333;
            margin-bottom: 30px;
        }
        .box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .matched {
            color: green;
        }
        .missing {
            color: red;
        }
    </style>
    """, unsafe_allow_html=True
)

# ---------- Placeholder Logo ----------
st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
st.markdown('<div class="title">🎯 SmartHire – AI Resume Screener</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Get job-fit analysis in seconds</div>', unsafe_allow_html=True)

# -------------- PDF Report Generator -------------------
def generate_pdf(name, email, experience, skills, matched_skills, missing_skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="SmartHire Resume Screening Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Experience: {experience} years", ln=True)
    pdf.cell(200, 10, txt=f"Skills: {', '.join(skills)}", ln=True)
    pdf.ln(10)

    pdf.set_text_color(0, 100, 0)
    pdf.multi_cell(200, 10, txt="Matched Skills:\n" + ', '.join(matched_skills))
    pdf.set_text_color(220, 50, 50)
    pdf.multi_cell(200, 10, txt="Missing Skills:\n" + ', '.join(missing_skills))

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()

# ---------------- Resume Text Extractor ------------------
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ---------------------- Skill Matcher ---------------------
def match_skills(resume_text, job_desc):
    resume_text = resume_text.lower()
    job_desc = job_desc.lower()

    skills_in_jd = set(re.findall(r'\b[a-zA-Z]+\b', job_desc))
    skills_in_resume = set(re.findall(r'\b[a-zA-Z]+\b', resume_text))

    matched = list(skills_in_jd & skills_in_resume)
    missing = list(skills_in_jd - skills_in_resume)

    return matched, missing

# ----------------------- App Layout -----------------------
with st.sidebar:
    st.header("Upload & Input")
    uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])
    job_desc = st.text_area("Paste the Job Description")

if uploaded_file and job_desc:
    with st.spinner("Analyzing..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        matched_skills, missing_skills = match_skills(resume_text, job_desc)

        name_match = re.search(r'Name[:\- ]*([A-Za-z ]+)', resume_text)
        name = name_match.group(1).strip() if name_match else "Not Found"

        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        email = email_match.group(0) if email_match else "Not Found"

        exp_match = re.search(r'([0-9]+)\+?\s+years?', resume_text)
        experience = exp_match.group(1) if exp_match else "0"

        skills = re.findall(r'\b[A-Za-z]+\b', resume_text)

        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.subheader("📄 Resume Summary:")
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Experience:** {experience} years")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.subheader("✅ Matched Skills:")
        st.markdown(f"<div class='matched'>{', '.join(matched_skills) if matched_skills else 'No matches found.'}</div>", unsafe_allow_html=True)

        st.subheader("❌ Missing Skills:")
        st.markdown(f"<div class='missing'>{', '.join(missing_skills) if missing_skills else 'None!'}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("📥 Download Report as PDF"):
            pdf_bytes = generate_pdf(name, email, experience, skills, matched_skills, missing_skills)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="SmartHire_Report.pdf">Click here to download</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("📤 Please upload a resume and paste the job description to get started.")