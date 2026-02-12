import sqlite3

from models import JobPosting
from storage.interface import JobStorage


class SQLiteJobStorage(JobStorage):

    def __init__(self, db_path="findmeajob.sqlite"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Get dicts instead of tuples
        #
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT primary key,
                company_name TEXT ot null,
                role_name  TEXT not null,
                location TEXT not null,
                job_link TEXT not null,
                source TEXT not null,
                description TEXT,
                stack TEXT,
                salary_range_posted TEXT not null,
                created_at TEXT default current_timestamp not null,
                session_id TEXT,
                seniority TEXT,
                skills TEXT,
                additional_info TEXT,
                fit_score INTEGER,
                fit_assessment_feedback text
                )
            """)
        self.conn.commit()

    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        pass

    def save_all(self, jobs: list[JobPosting]) -> None:
        with self.conn:
            self.conn.executemany("""
            INSERT OR REPLACE INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    job.job_id,
                    job.company_name,
                    job.role_name,
                    job.location,
                    job.job_link,
                    job.source,
                    job.description,
                    job.stack,
                    job.salary_range_posted,
                    job.seniority,
                    job.skills,
                    job.additional_info,
                    job.fit_score,
                    job.fit_assessment_feedback
                )
                for job in jobs
            ])
