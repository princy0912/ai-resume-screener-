# SmartHire: AI-Powered Resume Screener 💼🤖

**SmartHire** is an AI-based resume screening tool that parses resumes and intelligently matches them against job descriptions using NLP techniques. It calculates a match score and highlights key skill overlaps, helping recruiters shortlist candidates efficiently.

🔗 **Live Demo**: [Visit the deployed app](https://your-streamlit-app-link.streamlit.app)  
📁 **GitHub**: [https://github.com/princy0912/smarthire-resume-screener](https://github.com/princy0912/smarthire-resume-screener)

---

## 🚀 Features
- 📄 Upload Resume (PDF/DOCX/Plain Text)
- 📝 Upload Job Description (JD)
- 🔍 Resume & JD Parsing (skills, experience, contact)
- 📊 Match Score Calculation (0–100)
- ✅ Highlights Matching & Missing Skills
- ⚡ Clean and fast UI with Streamlit

---

## 🧠 Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **Libraries**: 
  - `PyMuPDF`, `docx2txt` – Resume parsing
  - `spaCy`, `difflib`, `re` – NLP for matching
- **Hosting**: Streamlit Cloud

---

## 📸 Demo Screenshot

![Screenshot](screenshot.png)

---

## 🛠️ How to Run Locally

```bash
git clone https://github.com/princy0912/smarthire-resume-screener.git
cd smarthire-resume-screener
pip install -r requirements.txt
streamlit run app.py
---

## 📬 Contact

👩‍💻 Created with ❤️ by [Princy Chauhan](https://www.linkedin.com/in/princy-chauhan)  
📧 princy.chauhan0912@gmail.com

---

## 📌 Project Status

✅ Basic Version Complete  
🔜 Coming Soon: ATS-style filtering, PDF Export, Semantic Analysis Boost