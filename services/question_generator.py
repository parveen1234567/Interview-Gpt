import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_questions(resume_text):

    prompt = f"""
You are an expert HR and technical interviewer.

Analyze the candidate's resume and generate exactly 10
personalized interview questions.

Question distribution:

HR QUESTIONS:
- Generate 3 HR/behavioral questions.
- Focus on the candidate's background, career goals,
  strengths, weaknesses, and experience.

TECHNICAL QUESTIONS:
- Generate 4 technical questions.
- Questions must be based on technologies, skills,
  tools, and concepts mentioned in the resume.

PROJECT QUESTIONS:
- Generate 3 project-based questions.
- Ask about projects, implementation, challenges,
  decisions, and the candidate's contribution.

IMPORTANT RULES:
- Questions must be based on the resume.
- Avoid generic questions when resume-specific questions
  are possible.
- Do not provide answers.
- Do not provide explanations.
- Return exactly 10 questions.
- Keep each question clear and interview-ready.

Return the questions in this exact format:

HR:
1. question
2. question
3. question

TECHNICAL:
4. question
5. question
6. question
7. question

PROJECT:
8. question
9. question
10. question

Candidate Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
    )

    result = response.choices[0].message.content

    questions = [
        line.strip()
        for line in result.split("\n")
        if line.strip()
    ]

    return questions