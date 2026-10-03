# Registration and Gmail password reset

The application is branded as **Interview GPT**. Its Resume ATS Score estimates
general ATS readiness and provides truthful, prioritized suggestions to improve
resume readability and organization. It is not an employer ATS guarantee or a
match against a specific job description.

## Configure the application

1. If `.env` does not exist, copy `.env.example` to `.env` and set the MySQL
   and Groq values. If you already have a `.env`, keep it and add the missing
   settings below; do not overwrite your existing database configuration.
2. Create a strong session key, for example:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Put the output in `SESSION_SECRET_KEY`. Do not commit `.env`.
3. For Gmail sending, enable 2-Step Verification on the sending Google account
   and create a Google **App Password**. Put the Gmail address in
   `SMTP_USERNAME` and `SMTP_FROM`; put the App Password (not the normal Gmail
   password) in `SMTP_PASSWORD`. Keep `SMTP_PORT=587`.
4. Set `APP_BASE_URL` to the URL users open in their browser. Use
   `http://127.0.0.1:8000` for local testing. Use the public HTTPS URL when
   deployed. Set `SESSION_COOKIE_SECURE=true` when the app is served over HTTPS.
5. Create the new reset-token table:

   ```powershell
   python create_tables.py
   ```

   Then start the FastAPI application.

## User flow

- The home page guides new visitors to register or existing users to sign in.
  Both paths return users to the page they intended to open after authentication.
- Register at `/register`; passwords must be at least 12 characters and are
  stored using the existing bcrypt password hashing.
- Use **Forgot your password?** on `/login`, submit the account email, and open
  the emailed link within 30 minutes. The return destination is preserved
  through the email link and password-reset form.
- Use **Forgot which email you used?** for safe account-email recovery guidance.
  The application does not disclose account email addresses; users who cannot
  identify or access their account email should contact the system administrator.
- Context-specific **Back to dashboard** and **Back to reports** links are
  provided where they help users return to the appropriate prior screen.
- Account deletion requires the current password and entering `DELETE MY ACCOUNT`
  (capitalization and surrounding spaces do not matter).
  It removes the login and password-reset tokens; interview sessions and reports
  are retained but detached from the deleted account and are no longer visible
  to that user.
- Resume analysis now produces a general Resume ATS Score and specific
  improvement suggestions, shown on the authenticated **Resume ATS Score**
  navigation page, separately from interview reports. Apply
  `migrations/20261003_add_ats_scores.sql` and
  `migrations/20261003_add_resume_feedback.sql` to existing databases before
  starting the updated application.
- Reset links are single-use. Only a SHA-256 digest of each random token is
  stored in MySQL, and reset requests are limited to three per account per hour.
- The forgot-password page returns the same confirmation whether or not an
  account exists, to reduce account enumeration.

If sending fails, the failure is logged by the server while the page retains
the generic confirmation. Check the application log and verify the Gmail App
Password, SMTP settings, and `APP_BASE_URL`; do not put credentials in chat or
source control.
