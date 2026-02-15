import streamlit as st
from utils import extract_text_from_pdf, clean_text, ats_score, extract_keywords, skill_match, grammar_readability_suggestions
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import time
import re
import random

# -------------------------
# Helpers
# -------------------------
def rewrite_bullet_point(bullet: str) -> str:
    bullet = bullet.strip()
    if not bullet:
        return ""

    templates = [
        "Designed and implemented {} using modern Python practices, improving performance and maintainability.",
        "Collaborated with cross-functional teams to deliver {}, resulting in measurable improvements.",
        "Built and optimized {} leveraging Python and data-driven techniques.",
        "Developed end-to-end solutions for {}, enhancing usability and scalability."
    ]

    core = bullet.lower()
    if core.startswith("worked on"):
        core = core.replace("worked on", "").strip()
    elif core.startswith("did"):
        core = core.replace("did", "").strip()

    core = core if core else "key project features"
    return random.choice(templates).format(core)

def highlight_keywords(text, keywords):
    def repl(match):
        return (
            "<mark style='background:linear-gradient(135deg,#22c55e,#3b82f6);"
            "color:black;padding:2px 6px;border-radius:6px'>"
            f"{match.group(0)}</mark>"
        )

    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
        text = pattern.sub(repl, text)
    return text

def generate_bullets_for_skill(skill: str):
    ideas = [
        f"Implemented {skill} in production environments to improve system reliability and scalability.",
        f"Applied {skill} to solve real-world problems, improving application performance and maintainability.",
        f"Worked hands-on with {skill} as part of end-to-end feature development and deployment.",
        f"Utilized {skill} in building and optimizing data-driven solutions."
    ]
    return random.sample(ideas, 2)

# -------------------------
# Step 6 helpers
# -------------------------
def section_score(section_text, jd_keywords):
    section_text_clean = clean_text(section_text)
    section_keywords = extract_keywords(section_text_clean)
    if not jd_keywords:
        return 0, "No job description keywords to compare."
    match_count = len(section_keywords & jd_keywords)
    percent = round((match_count / len(jd_keywords)) * 100, 2)
    if percent >= 60:
        feedback = "Strong alignment with job requirements."
    elif percent >= 30:
        feedback = "Moderate alignment. Consider adding more relevant keywords."
    else:
        feedback = "Low alignment. Add more relevant skills/projects matching the JD."
    return percent, feedback

def extract_section(text, section_names):
    text_lower = text.lower()
    for name in section_names:
        idx = text_lower.find(name)
        if idx != -1:
            return text[idx: idx + 800]
    return ""

# -------------------------
# Page + Theme
# -------------------------
st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

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
div[role="progressbar"] > div {
  background: linear-gradient(90deg, #22c55e, #3b82f6) !important;
}
mark { font-weight: 600; }
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

# -------------------------
# Analysis
# -------------------------
if uploaded_file and job_desc:
    progress = st.progress(0)
    status = st.empty()

    status.info("🔍 Extracting resume text...")
    resume_text = extract_text_from_pdf(uploaded_file)
    progress.progress(25)
    time.sleep(0.1)

    status.info("🧹 Cleaning text & preparing vectors...")
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_desc)
    progress.progress(50)
    time.sleep(0.1)

    status.info("🤖 Running ATS scoring & NLP analysis...")
    score = ats_score(resume_clean, job_clean)
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_desc)
    missing = jd_keywords - resume_keywords

    matched_skills, total_skills, skill_percent = skill_match(resume_text, job_desc)
    grammar_tips = grammar_readability_suggestions(resume_text)

    # ATS Breakdown
    total_jd_keywords = len(jd_keywords) if len(jd_keywords) > 0 else 1
    matched_keyword_count = len(resume_keywords & jd_keywords)
    keyword_overlap_percent = round((matched_keyword_count / total_jd_keywords) * 100, 2)
    readability_percent = 80 if len(grammar_tips) <= 1 else 50

    progress.progress(100)
    status.success("✅ Analysis complete!")

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

    # Job Readiness Summary
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧭 Job Readiness Summary")
    readiness = "Low" if score < 40 else "Medium" if score < 70 else "High"
    st.write(f"🔴 Overall Readiness: {readiness}")
    st.write("✅ Improve ATS score by adding missing keywords from JD.")
    st.write("✅ Work on improving skill alignment with the job role.")
    st.write("✅ Add 2–3 relevant skills or tools to your resume.")
    st.write("✅ Rewrite long sentences for better readability.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: Highlighted Resume (ATS View)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🔦 Highlighted Resume Preview (ATS View)")
    highlighted_resume = highlight_keywords(resume_text, resume_keywords & jd_keywords)
    st.markdown(f"<div style='line-height:1.7'>{highlighted_resume}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Missing Keywords
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🔍 Missing Keywords")
    if missing:
        st.write(", ".join(list(missing)[:40]))
    else:
        st.write("Great! Your resume matches most of the required keywords 🎯")
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 5: AI Resume Coach
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🎯 AI Resume Coach – Add Missing Skills")
    missing_list = sorted(list(missing))
    selected_skills = st.multiselect("Select skills you want resume bullets for:", missing_list[:12])

    if selected_skills:
        for skill in selected_skills:
            st.write(f"**Suggested bullets for _{skill}_:**")
            for idea in generate_bullets_for_skill(skill):
                st.code(idea, language="text")
    else:
        st.caption("Select 1–3 missing skills to generate ready-to-use resume bullets.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 6: Resume Section Scores
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧩 Resume Section Scores")

    projects_text = extract_section(resume_text, ["projects", "project"])
    skills_text = extract_section(resume_text, ["skills", "technical skills"])
    experience_text = extract_section(resume_text, ["experience", "work experience", "professional experience"])

    proj_score, proj_fb = section_score(projects_text, jd_keywords)
    skills_score, skills_fb = section_score(skills_text, jd_keywords)
    exp_score, exp_fb = section_score(experience_text, jd_keywords)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📁 Projects", f"{proj_score}%")
        st.caption(proj_fb)
    with c2:
        st.metric("🧰 Skills", f"{skills_score}%")
        st.caption(skills_fb)
    with c3:
        st.metric("💼 Experience", f"{exp_score}%")
        st.caption(exp_fb)

    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # Step 7: JD vs Resume – Side-by-Side Smart Diff (NEW)
    # -------------------------
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📑 JD vs Resume – Side-by-Side (Smart Diff)")

    left, right = st.columns(2)
    with left:
        st.markdown("**📄 Job Description (Highlighted Matches)**")
        jd_highlighted = highlight_keywords(job_desc, resume_keywords & jd_keywords)
        st.markdown(f"<div style='line-height:1.7; max-height:300px; overflow:auto'>{jd_highlighted}</div>", unsafe_allow_html=True)

    with right:
        st.markdown("**📝 Resume (Highlighted Matches)**")
        resume_highlighted = highlight_keywords(resume_text, resume_keywords & jd_keywords)
        st.markdown(f"<div style='line-height:1.7; max-height:300px; overflow:auto'>{resume_highlighted}</div>", unsafe_allow_html=True)

    st.caption("💡 Highlighted terms show overlap between your resume and the job description (ATS match).")
    st.markdown('</div>', unsafe_allow_html=True)

    # Grammar
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧠 Grammar & Readability Suggestions")
    for tip in grammar_tips:
        st.info(tip)
    st.markdown('</div>', unsafe_allow_html=True)

    # Skill Match Details
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📊 Skill Match Details")
    st.write(f"Matched Skills ({len(matched_skills)}): ", ", ".join(list(matched_skills)[:30]))
    st.markdown('</div>', unsafe_allow_html=True)

    # Bullet Rewriter
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("✍️ Resume Bullet Rewriter (AI Helper)")
    bullet_input = st.text_area("Paste a weak resume bullet point to improve:", key="bullet_rewriter")
    if st.button("✨ Rewrite Bullet Point"):
        improved_bullet = rewrite_bullet_point(bullet_input)
        if improved_bullet:
            st.success("Improved Version:")
            st.write(improved_bullet)
        else:
            st.warning("Please enter a bullet point to rewrite.")
    st.markdown('</div>', unsafe_allow_html=True)

    # PDF Download
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
else:
    st.info("Upload resume PDF and paste job description to start AI analysis.")
