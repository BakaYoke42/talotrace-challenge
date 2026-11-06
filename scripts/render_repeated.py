"""Exercise two real queued renders of the same question through the API."""
import time

from fastapi.testclient import TestClient

from app.main import app

question = "How does the pH scale work?"
with TestClient(app) as client:
    jobs = []
    for _ in range(2):
        response = client.post("/videos", json={"question": question})
        response.raise_for_status()
        job = response.json()
        jobs.append(job)
        print(f"Queued {job['job_id']}: {job['status']}", flush=True)
    assert jobs[0]["job_id"] != jobs[1]["job_id"]
    pending = {job["job_id"] for job in jobs}
    failed = False
    while pending:
        for job_id in list(pending):
            response = client.get(f"/videos/{job_id}")
            response.raise_for_status()
            job = response.json()
            if job["status"] == "failed":
                print(f"{job_id}: failed: {job['error']}", flush=True)
                failed = True
                pending.remove(job_id)
            elif job["status"] == "completed":
                artifact = client.get(job["artifact_url"])
                print(f"{job_id}: HTTP {artifact.status_code}, {len(artifact.content)} bytes", flush=True)
                failed |= artifact.status_code != 200 or not artifact.content
                pending.remove(job_id)
        time.sleep(1)
    if failed:
        raise SystemExit(1)
