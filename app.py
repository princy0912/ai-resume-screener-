
import streamlit as st
import fitz  # PyMuPDF
import re

# Sample skill set to match from (can be expanded or customized)
COMMON_SKILLS = {
    'python', 'java', 'c++', 'html', 'css', 'javascript', 'react', 'node.js',
    'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'sql',
    'git', 'github', 'flask', 'django', 'tensorflow', 'keras', 'api',
    'data analysis', 'data visualization', 'communication', 'problem solving',
    'cloud', 'aws', 'azure', 'docker', 'kubernetes'
}

st.set_page_config(page_title="AI Resume Screener", layout="centered")
st.title("📄 AI Resume Screening Tool")
# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Settings")

min_exp = st.sidebar.number_input("Minimum Experience (in years)", min_value=0, max_value=20, value=0)
must_have_skills = st.sidebar.text_input("Must-Have Skills (comma-separated)", value="")

# Convert skills to a clean list
must_have_skills_list = [s.strip().lower() for s in must_have_skills.split(",") if s.strip()]
st.markdown("Upload your **resume (PDF)** and **job description (JD)** to get a match score.")

resume_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"])
jd_input = st.text_area("📄 Paste the Job Description here", height=200)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()

def extract_skills(text):
    found_skills = set()
    for skill in COMMON_SKILLS:
        # Use word boundaries for accurate matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text):
            found_skills.add(skill)
    return found_skills

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

        if match_percent >= 70:
            st.success("Great match! 🎯 You are ready to apply.")
        elif match_percent >= 40:
            st.warning("Decent match. You may want to improve your resume.")
        else:
            st.error("Low match. Consider adding more relevant skills.")
