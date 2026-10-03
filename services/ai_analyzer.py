import os
import re

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# RESUME ANALYSIS
# =========================================================

def analyze_resume(resume_text):

    prompt = f"""
You are an expert technical recruiter.

Analyze ONLY the resume provided below.

Provide:

1. Resume ATS Score: X/100
2. Skills
3. Strengths
4. Weaknesses
5. Prioritized Improvements to Increase the Resume ATS Score

IMPORTANT:

Do not invent skills, technologies, projects, companies,
experience, certifications, or education that are not present
in the resume.

Calculate a general resume ATS-readiness score based on machine-readable
text, standard section headings, simple organization, consistent dates,
relevant skills explicitly present in the resume, and concise achievements.
This is not a comparison to a specific job description or a guarantee from
any employer's ATS.

Give 3-5 prioritized, concrete edits the candidate can make to improve the
resume's ATS readiness. For each, describe what section or wording to improve
and give an example structure where useful. Never invent a skill, result,
metric, credential, or experience; ask the candidate to add only truthful
details. Mention that matching keywords should come from the actual target
job description and only be included when accurate.
Format section 5 as plain text, not Markdown or HTML. Start each suggestion on
its own line in this exact three-cell format:
P1 | Focus area | Specific truthful improvement and optional example
Use one row per suggestion, with priorities P1 through P5. Do not add other
columns, pipe characters within a cell, Markdown separators, or HTML tags.

Return the score in the exact form "Resume ATS Score: X/100" so the
application can read it reliably.

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )

    return response.choices[0].message.content


# =========================================================
# GENERATE RESUME-BASED QUESTIONS
# =========================================================

def generate_questions(resume_text):

    prompt = f"""
You are a strict technical interviewer.

Your job is to create interview questions ONLY from the
candidate's resume.

Read the resume carefully.

Generate EXACTLY 10 questions.

Question distribution:

1. 4 Technical questions
2. 3 Project / Experience questions
3. 2 Problem-solving questions
4. 1 HR / behavioral question

IMPORTANT RULES:

- Every technical question MUST use a technology,
  programming language, framework, database, tool, or
  technical skill that actually appears in the resume.

- Every project question MUST be based on a project,
  application, company, internship, or experience actually
  mentioned in the resume.

- Problem-solving questions must be related to technologies
  or projects mentioned in the resume.

- The HR/behavioral question should be related to the
  candidate's actual experience.

- DO NOT ask about technologies that are not present in
  the resume.

- DO NOT invent projects.

- DO NOT invent skills.

- DO NOT introduce unrelated technologies.

- If the resume mentions Java, ask about Java.

- If the resume mentions Spring Boot, ask about Spring Boot.

- If the resume mentions MySQL, ask about MySQL.

- If the resume mentions React, ask about React.

- If the resume does NOT mention a technology, DO NOT ask
  about that technology.

- Questions must be personalized to THIS resume.

- Do not give generic interview questions.

Return ONLY the 10 questions.

Number them:

1. ...
2. ...
3. ...

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    return response.choices[0].message.content


# =========================================================
# EXTRACT CANDIDATE NAME
# =========================================================

def _clean_candidate_name(value):
    if not value:
        return None

    name = value.strip().splitlines()[0].strip()
    name = re.sub(
        r"^(?:candidate\s+)?name\s*[:\-]\s*",
        "",
        name,
        flags=re.IGNORECASE,
    )
    name = re.split(r"\s+(?:\||•|·|—|–|-)\s+", name, maxsplit=1)[0]
    name = name.strip(" \t\r\n#*`\"'.,:;|•·—–-")

    words = name.split()
    if not 1 <= len(words) <= 5:
        return None

    ignored_names = {
        "unknown candidate",
        "candidate",
        "resume",
        "curriculum vitae",
        "professional summary",
        "contact",
    }
    ignored_words = {
        "engineer",
        "developer",
        "manager",
        "analyst",
        "designer",
        "architect",
        "consultant",
        "scientist",
        "specialist",
        "student",
        "intern",
        "experience",
        "education",
        "skills",
        "profile",
        "summary",
        "contact",
        "details",
        "phone",
        "email",
        "address",
        "linkedin",
        "github",
        "portfolio",
        "objective",
        "references",
        "certifications",
        "projects",
        "technical",
    }
    if name.casefold() in ignored_names or "@" in name or re.search(r"\d", name):
        return None
    if any(word.casefold().strip(".,") in ignored_words for word in words):
        return None

    if any(
        not re.fullmatch(
            r"[^\W\d_](?:[^\W\d_]|[.'’\-])*",
            word,
            flags=re.UNICODE,
        )
        for word in words
    ):
        return None

    return name


def _find_candidate_name_in_header(resume_text):
    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ][:20]

    for line in lines:
        if re.match(r"^(?:candidate\s+)?name\s*[:\-]", line, re.IGNORECASE):
            name = _clean_candidate_name(line)
            if name:
                return name

    for line in lines:
        name = _clean_candidate_name(line)
        if name and len(name.split()) >= 2:
            return name

    return None


def extract_candidate_name(resume_text):
    header_name = _find_candidate_name_in_header(resume_text)
    if header_name:
        return header_name

    prompt = f"""
Read the following resume.

Find the candidate's name, especially in the resume heading or contact section.
Return ONLY the candidate's full name.

Do not return:
- explanations
- labels
- extra text
- punctuation

If no name is found, return:

Unknown Candidate

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    extracted_name = _clean_candidate_name(
        response.choices[0].message.content
    )
    return extracted_name or "Unknown Candidate"


# =========================================================
# EXTRACT RESUME SCORE
# =========================================================

def extract_ats_score(analysis):

    match = re.search(
        r'ATS(?:\s+Compatibility)?\s+Score\s*[:\-]?\s*(-?\d{1,3})\s*(?:/\s*100)?',
        analysis,
        re.IGNORECASE,
    )

    if match:
        score = int(match.group(1))
        return max(0, min(score, 100))

    match = re.search(
        r'(?:Resume\s+)?Score\s*[:\-]?\s*(-?\d{1,3})\s*/\s*100',
        analysis
    )

    if match:

        score = int(
            match.group(1)
        )

        return max(
            0,
            min(score, 100)
        )

    match = re.search(r'(-?\d{1,3})\s*/\s*100', analysis)
    if match:
        return max(0, min(int(match.group(1)), 100))

    return 0


def extract_resume_score(analysis):
    return extract_ats_score(analysis)