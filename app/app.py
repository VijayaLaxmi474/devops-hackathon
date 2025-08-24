from flask import Flask, request, render_template, redirect, url_for
from PyPDF2 import PdfReader
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

KEYWORDS = ["python","aws","docker","kubernetes","sql","ci/cd","ansible","cloud","api","git"]

def extract_text_from_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        f = request.files.get("resume")
        if not f:
            return redirect(url_for("index"))
        filename = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(filename)

        # If PDF
        text = ""
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(filename)
        else:
            with open(filename, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()

        text_lower = text.lower()
        found = []
        missing = []
        for kw in KEYWORDS:
            if kw.lower() in text_lower:
                found.append(kw)
            else:
                missing.append(kw)

        score = int((len(found) / len(KEYWORDS)) * 100)

        suggestions = []
        if score < 50:
            suggestions.append("Add more technical keywords and skills.")
        if len(text.split()) < 150:
            suggestions.append("Resume seems short — add relevant details / projects.")
        if len(text.split()) > 900:
            suggestions.append("Resume is long — try to keep it under 2 pages.")

        return render_template("index.html",
                               found=found, missing=missing, score=score,
                               suggestions=suggestions, text=text[:2000])
    return render_template("index.html")
