import streamlit as st
from utils import extract_text_from_pdf, clean_text, ats_score, extract_keywords, skill_match, grammar_readability_suggestions
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import time

st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

# -------------------------
# Colorful Professional UI + Animations
# -------------------------
st.markdown("""
<style>
.stApp {
  background: radial-gradient(1200px 800px at 10% 10%, #0b1220 0%, #020617 40%, #020617 100%);
}
.fade-in { animation: fadeInUp 0.8s ease-in-out both; }
@keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 10px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
.metric-card {
  background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(16,185,129,0.12));
  border: 1px solid rgba(148,163,184,0.15);
  border-radius: 14px;
  padding: 14px 10px;
}
.metric-card:hover {
  transform: translateY(-2px) scale(1.01);
  transition: 0.2s ease-in-out;
  box-shadow: 0 12px 24px rgba(59,130,246,0.25);
}
.panel {
  background: linear-gradient(180deg, rgba(15,23,42,0.75), rgba(2,6,23,0.85));
  border: 1px solid rgba(148,163,184,0.12);
  border-radius: 16px;
  padding: 14px 16px;
  margin: 8px 0 16px 0;
}
button {
  background: linear-gradient(135deg, #3b82f6, #22c55e) !important;
  color: white !important;
  border-radius: 10px !important;
  border: none !important;
}
button:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
  transition: 0.15s ease-in-out;
}
div[role="progressbar"] > div {
  background: linear-gradient(90deg, #22c55e, #3b82f6) !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🤖 AI Resume Analyzer Pro")
st.sidebar.info("Upload resume & JD to get ATS score, skill match, and AI suggestions.")

st.title("📄 AI Resume Analyzer – Pro Version")

# -------------------------
# Role Templates
# -------------------------
st.subheader("⚡ Try with Role Templates")
colA, colB, colC = st.columns(3)

python_jd = """We are looking for a Python Developer with experience in building web applications using Streamlit or Flask.
Requirements include strong knowledge of Python, REST APIs, SQL databases, Git, and basic ML concepts. Experience with cloud deployment is a plus."""

data_analyst_jd = """We are hiring a Data Analyst with strong skills in Python, Pandas, NumPy, SQL, and data visualization.
The role involves cleaning data, building dashboards, and generating insights. Knowledge of statistics and Excel is required."""

ml_engineer_jd = """Looking for a Machine Learning Engineer with experience in Python, scikit-learn, NLP, and model deployment.
The candidate should have hands-on experience with data preprocessing, feature engineering, and ML pipelines."""

if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""

with colA:
    if st.button("🧑‍💻 Python Developer"):
        st.session_state.job_desc = python_jd

with colB:
    if st.button("📊 Data Analyst"):
        st.session_state.job_desc = data_analyst_jd

with colC:
    if st.button("🤖 ML Engineer"):
        st.session_state.job_desc = ml_engineer_jd

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_desc = st.text_area("Paste Job Description", value=st.session_state.job_desc)

if uploaded_file and job_desc:
    progress = st.progress(0)
    status = st.empty()

    status.info("🔍 Extracting resume text...")
    resume_text = extract_text_from_pdf(uploaded_file)
    progress.progress(25)
    time.sleep(0.15)

    status.info("🧹 Cleaning text & preparing vectors...")
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_desc)
    progress.progress(50)
    time.sleep(0.15)

    status.info("🤖 Running ATS scoring & NLP analysis...")
    score = ats_score(resume_clean, job_clean)
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_desc)
    missing = jd_keywords - resume_keywords

    matched_skills, total_skills, skill_percent = skill_match(resume_text, job_desc)
    grammar_tips = grammar_readability_suggestions(resume_text)

    # -------------------------
    # ATS Score Breakdown (NEW FEATURE)
    # -------------------------
    total_jd_keywords = len(jd_keywords) if len(jd_keywords) > 0 else 1
    matched_keyword_count = len(resume_keywords & jd_keywords)
    keyword_overlap_percent = round((matched_keyword_count / total_jd_keywords) * 100, 2)

    readability_percent = 80 if len(grammar_tips) <= 1 else 50

    progress.progress(90)
    time.sleep(0.15)

    status.success("✅ Analysis complete!")
    progress.progress(100)

    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.success("Analysis Complete ✅")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ATS Score", f"{score}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Skill Match", f"{skill_percent}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Missing Skills", len(missing))
        st.markdown('</div>', unsafe_allow_html=True)

    st.progress(min(int(score), 100))

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📈 ATS Score Breakdown (Explainable AI)")
    st.write(f"🔑 Keyword Overlap Contribution: {keyword_overlap_percent}%")
    st.write(f"🧩 Skill Match Contribution: {skill_percent}%")
    st.write(f"📖 Readability Contribution: {readability_percent}%")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🔍 Missing Keywords")
    if missing:
        st.write(", ".join(list(missing)[:40]))
    else:
        st.write("Great! Your resume matches most of the required keywords 🎯")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧠 Grammar & Readability Suggestions")
    for tip in grammar_tips:
        st.info(tip)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📊 Skill Match Details")
    st.write(f"Matched Skills ({len(matched_skills)}): ", ", ".join(list(matched_skills)[:30]))
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Download Full AI Report (PDF)"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        text = c.beginText(40, 750)

        text.textLine(f"ATS Score: {score}%")
        text.textLine(f"Skill Match: {skill_percent}%")
        text.textLine(" ")

        text.textLine("Missing Keywords:")
        for word in list(missing)[:30]:
            text.textLine(word)

        text.textLine(" ")
        text.textLine("AI Suggestions:")
        for tip in grammar_tips:
            text.textLine(f"- {tip}")

        c.drawText(text)
        c.showPage()
        c.save()
        buffer.seek(0)

        st.download_button(
            label="Download Report",
            data=buffer,
            file_name="ai_resume_report.pdf",
            mime="application/pdf"
        )

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Upload resume PDF and paste job description to start AI analysis.")
