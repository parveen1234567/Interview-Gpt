ALTER TABLE interview_sessions
    ADD COLUMN user_id INT NULL,
    ADD INDEX ix_interview_sessions_user_id (user_id),
    ADD CONSTRAINT fk_interview_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE interview_results
    ADD COLUMN user_id INT NULL,
    ADD INDEX ix_interview_results_user_id (user_id),
    ADD CONSTRAINT fk_interview_results_user
        FOREIGN KEY (user_id) REFERENCES users(id);
