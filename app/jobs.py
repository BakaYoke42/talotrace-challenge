import sqlite3
from contextlib import contextmanager
from pathlib import Path


class JobStore:
    def __init__(self, path: str | Path):
        self.path = str(path)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL, question TEXT NOT NULL, concept TEXT NOT NULL,
                status TEXT NOT NULL, stage TEXT, error TEXT, artifact_url TEXT
            )""")
            db.execute("UPDATE jobs SET status='failed', stage=NULL, error=? WHERE status='processing'",
                       ("Processing interrupted by a restart",))

    def create(self, job: dict):
        with self.connect() as db:
            db.execute("""INSERT INTO jobs (job_id, question, concept, status, stage, error, artifact_url)
                          VALUES (:job_id, :question, :concept, :status, :stage, :error, :artifact_url)""", job)

    def get(self, job_id: str):
        with self.connect() as db:
            row = db.execute("SELECT job_id, question, concept, status, stage, error, artifact_url FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            return dict(row) if row else None

    def list_jobs(self):
        with self.connect() as db:
            rows = db.execute("SELECT job_id, question, concept, status, stage, error, artifact_url FROM jobs ORDER BY sequence DESC").fetchall()
            return [dict(row) for row in rows]

    def claim_next(self):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT job_id FROM jobs WHERE status='queued' ORDER BY sequence LIMIT 1").fetchone()
            if row is None:
                return None
            db.execute("UPDATE jobs SET status='processing', stage='rendering' WHERE job_id=?", (row["job_id"],))
            job_id = row["job_id"]
        return self.get(job_id)

    def finish(self, job_id: str, error: str | None = None, artifact_url: str | None = None):
        with self.connect() as db:
            db.execute("UPDATE jobs SET status=?, stage=?, error=?, artifact_url=? WHERE job_id=? AND status='processing'",
                       ("failed" if error else "completed", None if error else ("published" if artifact_url else "simulated"), error, artifact_url, job_id))
