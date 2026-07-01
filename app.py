from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import mysql.connector
from dotenv import load_dotenv
import google.generativeai as genai
import os

# ---------------- LOAD ENV ----------------

load_dotenv()

app = Flask(__name__)

# ---------------- GEMINI ----------------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- DATABASE ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vijju@123",
    database="resume_builder"
)

cursor = db.cursor()

resume_data = {}

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- RESUME ----------------

@app.route("/resume", methods=["POST"])
def resume():

    global resume_data

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    education = request.form["education"]
    projects = request.form["projects"]
    experience = request.form["experience"]
    certifications = request.form["certifications"]

    linkedin = request.form["linkedin"]
    github = request.form["github"]
    portfolio = request.form["portfolio"]

    skills = request.form["skills"]

    # -------- AI SUMMARY --------

    summary_prompt = f"""
Write a professional resume summary.

Name : {name}
Education : {education}
Projects : {projects}
Experience : {experience}
Skills : {skills}

Keep it within 4 lines.
"""

    ai_summary = model.generate_content(summary_prompt).text

    # -------- ATS REPORT --------

    ats_prompt = f"""
Act as an ATS Resume Checker.

Candidate Skills:
{skills}

Projects:
{projects}

Experience:
{experience}

Give:

ATS Score out of 100

Strengths

Weaknesses

Suggestions
"""

    ats_report = model.generate_content(ats_prompt).text

    # ---------------- SAVE TO MYSQL ----------------

    cursor.execute("""
    INSERT INTO resumes
    (
        name,
        email,
        phone,
        education,
        projects,
        experience,
        certifications,
        skills
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        name,
        email,
        phone,
        education,
        projects,
        experience,
        certifications,
        skills
    ))
    db.commit()

    # ---------------- STORE DATA ----------------

    resume_data = {

        "name": name,
        "email": email,
        "phone": phone,

        "education": education,
        "projects": projects,
        "experience": experience,
        "certifications": certifications,

        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,

        "skills": skills,

        "ai_summary": ai_summary,

        "ats_report": ats_report

    }

    return render_template(
        "resume.html",
        **resume_data
    )


# ---------------- DOWNLOAD PDF ----------------

@app.route("/download")
def download():

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial","B",18)

    pdf.cell(
        200,
        10,
        "AI Resume Builder",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font("Arial","",12)

    pdf.cell(200,10,f"Name : {resume_data['name']}",ln=True)

    pdf.cell(200,10,f"Email : {resume_data['email']}",ln=True)

    pdf.cell(200,10,f"Phone : {resume_data['phone']}",ln=True)

    pdf.cell(200,10,f"LinkedIn : {resume_data['linkedin']}",ln=True)

    pdf.cell(200,10,f"GitHub : {resume_data['github']}",ln=True)

    pdf.cell(200,10,f"Portfolio : {resume_data['portfolio']}",ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",14)

    pdf.cell(200,10,"Professional Summary",ln=True)

    pdf.set_font("Arial","",12)

    pdf.multi_cell(
        0,
        8,
        resume_data["ai_summary"]
    )

    pdf.ln(5)

    pdf.set_font("Arial","B",14)

    pdf.cell(200,10,"Education",ln=True)

    pdf.set_font("Arial","",12)

    pdf.multi_cell(
        0,
        8,
        resume_data["education"]
    )
    pdf.ln(5)
    pdf.set_font("Arial","B",14)
    pdf.cell(200,10,"Projects",ln=True)

    pdf.set_font("Arial","",12)
    pdf.multi_cell(
        0,
        8,
        resume_data["projects"]
    )

    pdf.ln(5)

    pdf.set_font("Arial","B",14)
    pdf.cell(200,10,"Experience",ln=True)

    pdf.set_font("Arial","",12)
    pdf.multi_cell(
        0,
        8,
        resume_data["experience"]
    )

    pdf.ln(5)

    pdf.set_font("Arial","B",14)
    pdf.cell(200,10,"Certifications",ln=True)

    pdf.set_font("Arial","",12)
    pdf.multi_cell(
        0,
        8,
        resume_data["certifications"]
    )

    pdf.ln(5)

    pdf.set_font("Arial","B",14)
    pdf.cell(200,10,"Technical Skills",ln=True)

    pdf.set_font("Arial","",12)
    pdf.multi_cell(
        0,
        8,
        resume_data["skills"]
    )

    pdf.ln(5)

    pdf.set_font("Arial","B",14)
    pdf.cell(200,10,"ATS Report",ln=True)

    pdf.set_font("Arial","",12)
    pdf.multi_cell(
        0,
        8,
        resume_data["ats_report"]
    )

    pdf.output("resume.pdf")

    return send_file(
        "resume.pdf",
        as_attachment=True
    )


# ---------------- MAIN ----------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)