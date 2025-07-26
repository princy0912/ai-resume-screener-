import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
import base64

---------- PDF Report Generator ----------

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

file_name = f"{name.replace(' ', '_')}_screening_report.pdf"  
pdf.output(file_name)  
return file_name

---------- Skill Set ----------

COMMON_SKILLS = {
'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js',
'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql',
'git', 'github', 'flask', 'django', 'tensorflow', 'keras', 'api',
'data analysis', 'data visualization', 'communication', 'problem solving',
'cloud', 'aws', 'azure', 'docker', 'kubernetes'
}

---------- Page Setup ----------

st.set_page_config(page_title="AI Resume Screener", layout="centered")
st.title("📄 AI Resume Screening Tool")
st.markdown("Upload your resume (PDF) and job description (JD) to get a match score.")

---------- Sidebar Filters ----------

st.sidebar.header("🔍 Filter Settings")
min_exp = st.sidebar.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0)
must_have_skills = st.sidebar.text_input("Must-Have Skills (comma-separated)", value="")

must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]

resume_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"])
jd_input = st.text_area("📄 Paste the Job Description here", height=200)

---------- Helper Functions ----------

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

---------- Analysis ----------

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
    st.write(f"**Match Score:** {match_percent}%")  
    st.write(f"**Skills in JD:** {', '.join(sorted(jd_skills))}")  
    st.write(f"**Matched Skills:** {', '.join(sorted(matched_skills)) or 'None'}")  
    st.write(f"**Missing Skills:** {', '.join(sorted(missing_skills)) or 'None'}")

---------- Dummy Parsed Resume Data ----------

resume_skills = resume_skills if 'resume_skills' in locals() else set()
parsed_data = {
"name": "John Doe",
"email": "john@example.com",
"experience_years": 2,
"skills": list(resume_skills)
}

---------- Experience Check ----------

if parsed_data['experience_years'] < min_exp:
st.warning(f"❌ This candidate has only {parsed_data['experience_years']} years of experience. Minimum required: {min_exp}")
else:
st.success(f"✅ Experience requirement met: {parsed_data['experience_years']} years")

---------- Must-Have Skills Check ----------

must_have_matched = [s for s in must_have_skills_list if s in parsed_data['skills']]
must_have_missing = [s for s in must_have_skills_list if s not in parsed_data['skills']]

st.subheader("⭐ Must-Have Skills Match:")
st.write("✅ Matched:", must_have_matched)
st.write("❌ Missing:", must_have_missing)

---------- Download Button ----------

if st.button(f"📥 Download Report for {parsed_data['name']}", key=f"download_{parsed_data['name']}"):
pdf_file = generate_pdf(
parsed_data['name'],
parsed_data['email'],
parsed_data['experience_years'],
parsed_data['skills'],
must_have_matched,
must_have_missing
)

with open(pdf_file, "rb") as f:  
    base64_pdf = base64.b64encode(f.read()).decode('utf-8')  
    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{pdf_file}">👉 Click here to download {pdf_file}</a>'  
    st.markdown(href, unsafe_allow_html=True)  

# Optional recommendation based on score  
if match_percent >= 70:  
    st.success("Great match! 🎯 You are ready to apply.")  
elif match_percent >= 40:  
    st.warning("Decent match. You may want to improve your resume.")  
else:  
    st.error("Low match. Consider adding more relevant skills.")

