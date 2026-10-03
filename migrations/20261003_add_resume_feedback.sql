ALTER TABLE interview_sessions
    ADD COLUMN resume_feedback TEXT NULL;

ALTER TABLE interview_results
    ADD COLUMN resume_feedback TEXT NULL;
