# AI Resume Analyzer – Pro 🤖📄

🔗 **Live Demo:**  
https://ai-resume-analyzer-rrmqbswqbsfbwt9i8mzprx.streamlit.app/

An AI-powered web application that analyzes resumes against job descriptions to estimate ATS (Applicant Tracking System) compatibility, identify missing skills, and provide grammar & readability suggestions. Built with Python, NLP (spaCy), and Streamlit, and deployed on Streamlit Cloud.

---

## 🚀 Features

- Upload resume (PDF)
- Paste job description
- ATS match score using cosine similarity
- Skill match percentage & missing keywords
- Grammar & readability suggestions (NLP-based)
- Downloadable AI analysis report (PDF)
- Clean UI with Streamlit
- Cloud deployment on Streamlit Community Cloud

---

## 🛠 Tech Stack

- **Language:** Python  
- **Framework/UI:** Streamlit  
- **NLP:** spaCy, NLTK  
- **ML:** scikit-learn (cosine similarity)  
- **PDF Processing:** pdfplumber  
- **Report Generation:** ReportLab  
- **Deployment:** Streamlit Cloud  
- **Version Control:** GitHub  

---

## ⚙️ How It Works (High Level)

1. The resume text is extracted from PDF using `pdfplumber`.  
2. Resume and job description are cleaned and vectorized using `CountVectorizer`.  
3. ATS match score is calculated using **cosine similarity**.  
4. NLP is used to extract keywords and identify missing skills.  
5. Grammar and readability suggestions are generated using NLP heuristics.  
6. A downloadable PDF report is generated for the user.

---

## 🧪 Run Locally

```bash
git clone https://github.com/tejasmnaidu/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
