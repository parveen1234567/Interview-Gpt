# Deploy the existing website on Render

Render builds the included Dockerfile and runs the existing FastAPI website
with its Jinja templates, static CSS, and JavaScript. It does not replace the
website UI with Streamlit.

## 1. Prepare an external MySQL database

This project uses MySQL. Render does not provide a managed MySQL database, so
create one with a MySQL provider that permits connections from Render. For
example, Aiven provides hosted MySQL; review its current plans and configure
network access and TLS according to the provider's instructions.

Collect the database host, port, username, password, and database name. If you
already have a MySQL database and want to keep its users and reports, use that
database or migrate its data before directing users to the deployed site.
Never commit database credentials or exports.

## 2. Deploy the GitHub repository

1. Sign in to the [Render Dashboard](https://dashboard.render.com/) using
   GitHub, then select **New → Blueprint**.
2. Connect the `parveen1234567/Interview-Gpt` repository and its `main` branch.
   Render reads the root `render.yaml` Blueprint and builds the web service
   from the included `Dockerfile`.
3. Enter the database values and application secrets when Render prompts for
   the Blueprint's unsynced environment variables. They are runtime settings;
   do not add real values to `render.yaml` or GitHub.
4. Deploy the Blueprint. The web service uses `/healthz` as its health check.

You can also create a **Web Service** directly from the repository and select
**Docker** as the runtime. In that case, set the health check path to
`/healthz` and enter the same environment variables below under the service's
**Environment** settings.

## 3. Configure environment variables

Set these required variables on the Render web service:

| Variable | Value |
| --- | --- |
| `DB_HOST` | Hostname from your external MySQL provider |
| `DB_PORT` | Port from your external MySQL provider |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | MySQL database name |
| `GROQ_API_KEY` | Your Groq API key |
| `SESSION_SECRET_KEY` | A fresh, long, randomly generated secret |
| `SESSION_COOKIE_SECURE` | `true` |

Generate a session secret locally with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep it private and paste it directly into Render's environment settings.
After Render assigns a public HTTPS URL, add `APP_BASE_URL` with that URL. To
enable password-reset email, configure `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM` as well. These SMTP settings
are optional for deployment, but email-based password reset needs them.

If the database provider requires a TLS certificate, follow its instructions
for securely providing its CA certificate to the Render service. Set
`DB_SSL_CA` to the certificate's mounted file path in Render. The app verifies
the certificate and database hostname when this setting is present. Do not
disable database TLS verification to work around connection errors.

## 4. Check database schema and deploy

For a new, empty MySQL database, the application creates its tables at startup.
For an existing database, table creation does not add new columns. Review and
apply relevant SQL files under `migrations/` before deploying, including the
ATS score and resume feedback migrations if those columns are missing.

Once Render shows the service as live:

1. Open the service's **Settings** and create or copy its public `onrender.com`
   URL. Add it as `APP_BASE_URL` and redeploy.
2. Visit `/healthz` on the deployed URL and confirm it returns `{"status":"ok"}`.
3. Check the homepage, static styles, login, resume upload, ATS Score page,
   interviews, report PDFs, and password-reset email if SMTP is configured.
4. If the CSS looks stale, hard-refresh the browser.

## Important

- Render hosting and external database usage may incur charges. Review current
  pricing and usage limits before deployment.
- Render's free web services can spin down when idle, so the next request may
  take longer to respond. Free instances are intended for testing and hobby
  projects, not production.
- The application uses a signed session cookie. Keep `SESSION_SECRET_KEY`
  private and stable between deploys; use `SESSION_COOKIE_SECURE=true` for
  HTTPS.
- Render's local filesystem is ephemeral. Do not rely on uploaded resumes or
  generated PDFs remaining available after restarts or deploys. Reports stored
  in MySQL can be used to regenerate PDFs. Arrange backups with your database
  provider.
- Set up MySQL backups before using the site with important user data.
