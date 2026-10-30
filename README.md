# 🎤 Interview GPT

<p align="center">
  <strong>An AI-powered Resume-Based Interview Preparation Platform that helps users analyze resume ATS scores, generate personalized interview questions, practice mock interviews, receive AI-driven feedback, and download detailed interview reports.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="MySQL" src="https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/ORM-SQLAlchemy-red">
  <img alt="Groq" src="https://img.shields.io/badge/AI-Groq-orange">
  <img alt="Deployment" src="https://img.shields.io/badge/Deployment-Render-46E3B7">
</p>

<p align="center">
  <a href="YOUR_RENDER_DEPLOY_LINK">🌐 Live Demo</a> •
  <a href="https://github.com/parveen1234567/Interview-Gpt">💻 Source Code</a>
</p>

---

# 🚀 Project Overview

Interview GPT is a resume-based AI interview preparation platform designed to help job seekers improve their interview performance through personalized practice sessions and resume analysis.

The application leverages Artificial Intelligence to analyze candidate resumes, generate role-specific interview questions, evaluate responses, provide actionable feedback, and generate downloadable performance reports.

Rather than practicing generic interview questions, users receive questions tailored to their actual resume, skills, and experience.

---

# 💡 Problem Statement

Many job seekers face challenges such as:

- Lack of interview preparation
- Generic mock interview resources
- Poor understanding of ATS optimization
- Limited access to personalized feedback
- Difficulty identifying resume weaknesses

This project solves these challenges by creating an intelligent interview preparation platform that combines ATS evaluation and AI-powered interview coaching.

---

# 🎯 Product Value

Interview GPT provides practical career support for students, freshers, and professionals.

### For Students

- Practice technical and HR interviews
- Improve communication skills
- Understand ATS requirements
- Increase placement readiness

### For Job Seekers

- Receive personalized interview questions
- Get AI-generated feedback
- Improve resume quality
- Track interview performance

### For Recruiters & Trainers

- Assess candidate readiness
- Review performance reports
- Identify skill gaps

---

# ✨ Core Features

## 👤 User Authentication

Supports:

- Account Registration
- User Login
- Password Recovery
- Profile Management

Ensures secure access to interview data and reports.

---

## 📄 Resume Upload

Users can upload resumes for:

- ATS analysis
- Skill extraction
- Interview question generation
- Resume evaluation

---

## 🎯 Resume-Based Interview Questions

The platform generates personalized questions based on:

- Skills
- Projects
- Technologies
- Experience
- Education

This creates realistic interview experiences.

---

## 📊 ATS Resume Score Analysis

Provides:

- ATS compatibility score
- Resume improvement recommendations
- Optimization suggestions
- Keyword enhancement guidance

---

## 🤖 AI-Powered Feedback

After each interview:

- Performance evaluation
- Strength analysis
- Improvement recommendations
- Detailed feedback generation

---

## 📑 Downloadable Reports

Users can download:

- Interview assessments
- Feedback reports
- Performance summaries

---

## 🔒 Secure Session Management

Includes:

- Session-based authentication
- Secure user accounts
- Environment-based secret management

---

# 🏗️ System Architecture

## High-Level Architecture

```text
User
 │
 ▼
FastAPI Web Application
 │
 ├── Authentication Module
 ├── Resume Processing
 ├── ATS Evaluation
 ├── Interview Engine
 ├── Feedback Generator
 └── Report Management
 │
 ▼
MySQL Database
 │
 ▼
Groq AI Services
```

---

## Interview Workflow

```text
User Registration
        │
        ▼
Resume Upload
        │
        ▼
Resume Analysis
        │
        ▼
Question Generation
        │
        ▼
Interview Practice
        │
        ▼
AI Feedback
        │
        ▼
Download Report
```

---

# 📂 Project Structure

```text
Interview-GPT/
│
├── app.py
│   └── FastAPI application entry point
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── ats_score.html
│   └── interview.html
│
├── static/
│   ├── css/
│   ├── javascript/
│   └── assets/
│
├── database/
│   ├── models.py
│   ├── connection.py
│   └── schema.py
│
├── migrations/
│   └── Database migration scripts
│
├── uploads/
│   └── Uploaded resumes
│
├── reports/
│   └── Generated PDF reports
│
├── .env.example
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

---

# 🧰 Technology Stack

## Backend

| Technology | Purpose |
|------------|----------|
| Python 3.11 | Core Development |
| FastAPI | Web Framework |
| Uvicorn | ASGI Server |
| SQLAlchemy | ORM |
| PyMySQL | Database Connectivity |

---

## Artificial Intelligence

| Technology | Purpose |
|------------|----------|
| Groq API | AI Resume Analysis |
| Groq API | Question Generation |
| Groq API | Feedback Generation |

---

## Frontend

| Technology | Purpose |
|------------|----------|
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript | Interactivity |
| Jinja2 Templates | Dynamic Rendering |

---

## Database

| Technology | Purpose |
|------------|----------|
| MySQL | Data Storage |
| SQLAlchemy | Database Models |

---

# 🔄 Application Workflow

## Step 1: User Authentication

```text
Register / Login
```

---

## Step 2: Resume Upload

```text
Upload Resume
```

---

## Step 3: ATS Evaluation

```text
Resume Analysis
      │
      ▼
ATS Score Generation
```

---

## Step 4: Interview Preparation

```text
Skill Extraction
       │
       ▼
Question Generation
```

---

## Step 5: Mock Interview

```text
Question
   │
   ▼
User Response
   │
   ▼
AI Evaluation
```

---

## Step 6: Feedback Report

```text
Interview Summary
       │
       ▼
Download PDF Report
```

---

# 🚀 Running the Project

## Create Virtual Environment

```powershell
py -3.11 -m venv .venv
```

---

## Activate Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Run Application

```powershell
uvicorn app:app --reload
```

---

## Open Website

```text
http://127.0.0.1:8000
```

---

## Health Endpoint

```text
http://127.0.0.1:8000/healthz
```

---

# 🔒 Configuration

Required environment variables:

```env
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=

SESSION_SECRET_KEY=

GROQ_API_KEY=

SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=

APP_BASE_URL=
```

Never commit real API keys, passwords, or database credentials.

---

# 🗄️ Database Design

Major Data Modules:

- Users
- User Profiles
- Uploaded Resumes
- ATS Reports
- Interview Questions
- Interview Sessions
- Feedback Reports
- Downloadable PDFs

---

# 🚀 Deployment

## Live Application

🌐 YOUR_RENDER_DEPLOY_LINK

## Hosting Platform

Render

## Deployment Architecture

```text
GitHub Repository
        │
        ▼
      Render
        │
        ▼
 FastAPI Application
        │
 ┌──────┴──────┐
 ▼             ▼
MySQL       Groq API
Database      AI
```

The application is deployed using Render and integrates with an external MySQL database and Groq AI services.

---

# 🧪 Testing & Validation

Application testing includes:

✅ Resume Upload Validation

✅ User Authentication

✅ ATS Score Generation

✅ AI Question Generation

✅ Interview Practice Workflow

✅ Report Downloads

✅ Database Connectivity

✅ Password Recovery

---

# 🧩 Challenges Faced

## Resume Parsing

Extracting meaningful information from different resume formats.

### Learning

Resume structures vary significantly and require robust parsing logic.

---

## AI Question Generation

Generating relevant questions from user resumes.

### Learning

Context-aware prompting improves question quality.

---

## ATS Scoring Logic

Providing realistic ATS improvement suggestions.

### Learning

Resume optimization requires balancing keywords and readability.

---

## Secure Authentication

Managing user sessions and account security.

### Learning

Authentication is a critical part of production-ready applications.

---

# 📈 Future Enhancements

Future versions could include:

- 🎙️ AI Voice Interviews
- 📹 Video Interview Analysis
- 📊 Skill Gap Analytics
- 🤖 Multiple AI Interviewers
- 🌍 Multi-Language Support
- 📱 Mobile Application
- 📅 Interview Scheduling
- 🏢 Company-Specific Interview Kits
- 📈 Candidate Progress Dashboard
- 📄 Resume Builder Integration

---

# 📚 What I Learned

This project helped me gain practical experience in:

- FastAPI Development
- Database Design
- MySQL Integration
- SQLAlchemy ORM
- Resume Analysis
- Prompt Engineering
- AI-Powered Applications
- Authentication Systems
- Report Generation
- Full-Stack Deployment

---

# 🎯 Why This Project?

Interview GPT demonstrates how Artificial Intelligence can help job seekers improve their interview skills through personalized practice, resume optimization, and data-driven feedback.

Instead of relying on generic interview preparation, users receive customized guidance based on their actual resume and career profile.

> **Analyze. Practice. Improve. Get Interview Ready.**

---

# 📌 Project Highlights

- ✅ AI-Powered Interview Platform
- ✅ Resume-Based Questions
- ✅ ATS Score Analysis
- ✅ Personalized Feedback
- ✅ Downloadable Reports
- ✅ FastAPI Backend
- ✅ MySQL Database
- ✅ Groq AI Integration
- ✅ Authentication System
- ✅ Render Deployment Ready

---

# 🔗 Links

| Resource | Link |
|-----------|------|
| 🌐 Live Application | YOUR_RENDER_DEPLOY_LINK |
| 💻 GitHub Repository | https://github.com/parveen1234567/Interview-Gpt |
| 👨‍💻 GitHub Profile | https://github.com/parveen1234567 |
| 💼 LinkedIn | https://linkedin.com/in/shaik-chinthapalli-parveen-983668257 |

---

# 🙌 Final Note

Interview GPT represents my exploration of AI-powered career preparation tools, combining resume analysis, ATS optimization, personalized interview practice, and performance evaluation into one platform.

This project demonstrates how modern AI technologies can be integrated into real-world applications that help users prepare effectively for job opportunities and improve their professional growth.

> **Interview GPT — Practice Smarter. Interview Better. Get Hired.**
