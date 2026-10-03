# Deploy the existing website on Railway

Railway is configured to run the existing FastAPI application. It serves the
same Jinja templates and static CSS/JavaScript as the local website; it does
not replace the website UI with Streamlit.

## 1. Publish the project to GitHub

Create a private GitHub repository and push the project. Keep `.env`, database
exports, API keys, passwords, and other credentials out of GitHub. The existing
`.gitignore` excludes `.env` and local `uploads/` and `reports/` files.

## 2. Create the Railway services

1. Create a Railway project and deploy this GitHub repository as a service.
   Railway detects the included `Dockerfile`, installs the listed dependencies,
   and starts the existing FastAPI website.
2. In the same Railway project, add a **MySQL** database service.
3. In the web service's **Variables** page, add the variables below, using
   Railway's reference picker to select the corresponding values from the
   MySQL service:

   | Variable | Railway MySQL variable |
   | --- | --- |
   | `DB_HOST` | `MYSQLHOST` |
   | `DB_PORT` | `MYSQLPORT` |
   | `DB_USER` | `MYSQLUSER` |
   | `DB_PASSWORD` | `MYSQLPASSWORD` |
   | `DB_NAME` | `MYSQLDATABASE` |

   Reference format is `${{MySQL.MYSQLHOST}}`; replace `MySQL` with the exact
   service name shown on your Railway canvas. Use the private service values;
   do not expose the database publicly just to connect the web service.

4. Add these application secrets as Railway service variables:

   | Variable | Value |
   | --- | --- |
   | `GROQ_API_KEY` | Your valid Groq API key |
   | `SESSION_SECRET_KEY` | A fresh, long, randomly generated secret |
   | `SESSION_COOKIE_SECURE` | `true` |
   | `SMTP_HOST` | `smtp.gmail.com` |
   | `SMTP_PORT` | `587` |
   | `SMTP_USERNAME` | Your Gmail address |
   | `SMTP_PASSWORD` | Your Google App Password |
   | `SMTP_FROM` | Your sender Gmail address |
   | `APP_BASE_URL` | The public HTTPS URL assigned to the web service |

   Generate a session secret locally with:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Enter the value directly in Railway Variables; never add it to this
   repository. Set `APP_BASE_URL` after Railway generates the web domain.

## 3. Prepare the database

For a new, empty MySQL database, the application creates its tables at startup.
For an existing database, confirm it already includes the columns from both
migrations in `migrations/`. If not, apply the SQL migrations in date order
before routing production traffic:

1. `20261003_add_ats_scores.sql`
2. `20261003_add_resume_feedback.sql`

If you want to keep current accounts and reports, export the current database
and import it into Railway MySQL before switching users to the deployed site.
Do not share database dumps or credentials in chat.

## 4. Deploy and check the website

The included `Dockerfile` starts:

```text
uvicorn app:app --host 0.0.0.0 --port $PORT
```

The Docker image uses Python 3.11 and installs dependencies from
`requirements.txt`. In the Railway web service's **Settings → Deploy** section,
set the health check path to `/healthz`.

After Railway reports a successful deployment:

1. Generate a public domain under the web service's **Settings → Networking**.
2. Put that HTTPS address in `APP_BASE_URL` and redeploy.
3. Open the domain and verify the home page, static styles, login, resume upload,
   ATS Score navigation page, interviews, report PDFs, and password-reset email.
4. Confirm the browser address uses HTTPS. If stylesheet changes were recently
   made, hard-refresh once so the browser fetches the updated static CSS.

## Important

- Railway hosting and database usage may incur charges. Review current Railway
  pricing and usage limits before deployment.
- The application uses a database-backed session cookie signed by
  `SESSION_SECRET_KEY`; keep that key private and stable between deploys.
- Local uploaded files and generated PDFs are not durable application storage.
  Reports are stored in MySQL and their PDFs can be generated again. Do not rely
  on local container files surviving a redeploy.
- Set up MySQL backups before using the site with important user data.
