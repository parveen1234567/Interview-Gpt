ALTER TABLE interview_sessions
    ADD COLUMN ats_score INT NULL;

ALTER TABLE interview_results
    ADD COLUMN ats_score INT NULL;
