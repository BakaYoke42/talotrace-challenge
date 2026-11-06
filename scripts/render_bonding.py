"""Submit both bonding topics through the API and report their output files."""
import time

from fastapi.testclient import TestClient

from app.main import app, QUESTIONS

with TestClient(app) as client:
    jobs = []
    for question in list(QUESTIONS)[1:]:
        response = client.post("/videos", json={"question": question})
        response.raise_for_status()
        job = response.json()
        jobs.append(job)
        print(f"Queued {job['concept']}: {job['job_id']}", flush=True)
    pending = {job["job_id"] for job in jobs}
    failed = False
    while pending:
        for job_id in list(pending):
            response = client.get(f"/videos/{job_id}")
            response.raise_for_status()
            job = response.json()
            if job["status"] == "failed":
                print(f"{job['concept']}: {job_id} FAILED: {job['error']}", flush=True)
                failed = True
                pending.remove(job_id)
            elif job["status"] == "completed":
                artifact = client.get(job["artifact_url"])
                print(f"{job['concept']}: {job_id} HTTP {artifact.status_code}, {len(artifact.content)} bytes", flush=True)
                failed |= artifact.status_code != 200 or not artifact.content
                pending.remove(job_id)
        time.sleep(1)
    if failed:
        raise SystemExit(1)
