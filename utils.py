import re
import nltk
import spacy
from sklearn.feature_extraction.text import CountVectorizer
import pdfplumber
from collections import Counter

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    return text

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return text.lower()

def ats_score(resume_text, job_desc):
    vectorizer = CountVectorizer().fit_transform([resume_text, job_desc])
    vectors = vectorizer.toarray()
    score = (vectors[0] @ vectors[1]) / ((vectors[0] @ vectors[0])**0.5 * (vectors[1] @ vectors[1])**0.5)
    return round(score * 100, 2)

def extract_keywords(text):
    doc = nlp(text)
    keywords = set([token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]])
    return keywords

def skill_match(resume_text, jd_text):
    resume_keys = extract_keywords(resume_text)
    jd_keys = extract_keywords(jd_text)

    matched = resume_keys & jd_keys
    total_required = len(jd_keys) if len(jd_keys) > 0 else 1
    percentage = round((len(matched) / total_required) * 100, 2)

    return matched, jd_keys, percentage

def grammar_readability_suggestions(text):
    doc = nlp(text)
    long_sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 25]

    suggestions = []
    if long_sentences:
        suggestions.append("Your resume has very long sentences. Try breaking them into shorter ones.")

    passive_voice = [token.text for token in doc if token.dep_ == "auxpass"]
    if passive_voice:
        suggestions.append("Try to reduce passive voice. Use active voice to sound more confident.")

    if not suggestions:
        suggestions.append("Your resume readability looks good. Minor improvements can enhance clarity.")

    return suggestions
