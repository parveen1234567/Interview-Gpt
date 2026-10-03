# Interview GPT

Interview GPT is a resume-based interview practice website. It helps users
review their resume's ATS score, practice personalized interview questions, and
review feedback and downloadable reports.

The project is a FastAPI website rendered with Jinja templates and static CSS
and JavaScript. Deployment serves the same website UI; it is not a Streamlit
application.

## Features

- Account registration, sign-in, password recovery, and profile management
- Resume upload and resume-based interview question generation
- Interview practice and feedback reports
- Separate Resume ATS Score page with practical improvement suggestions
- Downloadable interview reports

## Technology

- Python 3.11
- FastAPI and Uvicorn
- Jinja2 templates and static CSS/JavaScript
- MySQL with SQLAlchemy and PyMySQL
- Groq API for AI-powered resume and interview features

## Run locally on Windows

### Requirements

- Python 3.11
- MySQL
- A Groq API key for AI-powered features

### Setup

Open PowerShell in the project directory and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and provide your MySQL connection settings, Groq API key, and a
long, random `SESSION_SECRET_KEY`. Configure SMTP settings if you want email
password recovery to work. Keep `.env` private; it is excluded from Git.

Start the website:

```powershell
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The health endpoint is
available at [http://127.0.0.1:8000/healthz](http://127.0.0.1:8000/healthz).

## Deploy from GitHub

The repository includes a Dockerfile for deploying the existing website on
Railway. Connect this GitHub repository to a Railway service, add a MySQL
service, and configure the database and application environment variables in
Railway. Set the health check path to `/healthz` and generate a public HTTPS
domain.

Follow [DEPLOYMENT.md](DEPLOYMENT.md) for the complete Railway setup, required
variables, database migration notes, and post-deployment checks.

## Configuration

Use `.env.example` as the list of supported environment variables. In
particular, the application requires:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`
- `SESSION_SECRET_KEY`
- `GROQ_API_KEY` for AI-powered features
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM`
  for password-recovery email
- `SESSION_COOKIE_SECURE=true` when serving the site over HTTPS
- `APP_BASE_URL` set to the public site URL for deployment

Never commit real API keys, passwords, session secrets, or database exports.

## Database notes

The application creates missing tables when it starts. If you are updating an
existing database, table creation does not add new columns; review and apply
the relevant SQL files under [`migrations/`](migrations/) before deploying.
Back up important data before applying schema changes.

Uploaded files and generated PDFs are stored on the local filesystem. Do not
assume they persist across hosted redeployments; interview data and reports
stored in MySQL are separate from those local files.
