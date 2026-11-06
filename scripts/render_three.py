"""Submit all three topics to the same local API and report process outcomes."""
import time

from fastapi.testclient import TestClient
from app.main import app, QUESTIONS

with TestClient(app) as client:
    jobs = []
    for question in QUESTIONS:
        response = client.post("/videos", json={"question": question})
        response.raise_for_status()
        job = response.json()
        jobs.append(job)
        print(f"Queued {job['concept']}: {job['job_id']}", flush=True)
    pending = {job["job_id"] for job in jobs}
    failed = False
    while pending:
        for job_id in list(pending):
            job = client.get(f"/videos/{job_id}").json()
            if job["status"] in ("completed", "failed"):
                if job["status"] == "completed":
                    response = client.get(job["artifact_url"])
                    print(f"{job['concept']}: {job_id} HTTP {response.status_code}, {len(response.content)} bytes", flush=True)
                    failed |= response.status_code != 200 or not response.content
                else:
                    print(f"{job['concept']}: {job_id} FAILED: {job['error']}", flush=True)
                    failed = True
                pending.remove(job_id)
        time.sleep(1)
    if failed:
        raise SystemExit(1)
