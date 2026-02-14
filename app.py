import streamlit as st
from utils import extract_text_from_pdf, clean_text, ats_score, extract_keywords, skill_match, grammar_readability_suggestions
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

st.sidebar.title("🤖 AI Resume Analyzer Pro")
st.sidebar.info("Upload resume & JD to get ATS score, skill match, and AI suggestions.")

st.title("📄 AI Resume Analyzer – Pro Version")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_desc = st.text_area("Paste Job Description")

if uploaded_file and job_desc:
    with st.spinner("Analyzing your resume with AI..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_clean = clean_text(resume_text)
        job_clean = clean_text(job_desc)

        score = ats_score(resume_clean, job_clean)
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(job_desc)
        missing = jd_keywords - resume_keywords

        matched_skills, total_skills, skill_percent = skill_match(resume_text, job_desc)
        grammar_tips = grammar_readability_suggestions(resume_text)

    st.success("Analysis Complete ✅")

    col1, col2, col3 = st.columns(3)
    col1.metric("ATS Score", f"{score}%")
    col2.metric("Skill Match", f"{skill_percent}%")
    col3.metric("Missing Skills", len(missing))

    st.progress(min(int(score), 100))

    st.subheader("🔍 Missing Keywords")
    if missing:
        st.write(", ".join(list(missing)[:40]))
    else:
        st.write("Great! Your resume matches most of the required keywords 🎯")

    st.subheader("🧠 Grammar & Readability Suggestions")
    for tip in grammar_tips:
        st.info(tip)

    st.subheader("📊 Skill Match Details")
    st.write(f"Matched Skills ({len(matched_skills)}): ", ", ".join(list(matched_skills)[:30]))

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
