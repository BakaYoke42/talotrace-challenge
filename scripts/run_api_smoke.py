"""Submit one actual rendering job through the API and report process status."""
import time

from fastapi.testclient import TestClient

from app.main import app

with TestClient(app) as client:
    response = client.post("/videos", json={"question": "How does the pH scale work?"})
    response.raise_for_status()
    job_id = response.json()["job_id"]
    print(f"Submitted job {job_id}", flush=True)
    while True:
        response = client.get(f"/videos/{job_id}")
        response.raise_for_status()
        job = response.json()
        if job["status"] in ("completed", "failed"):
            print(job, flush=True)
            if job["status"] == "completed":
                file_response = client.get(job["artifact_url"])
                print(f"File endpoint: HTTP {file_response.status_code}, {len(file_response.content)} bytes", flush=True)
                file_response.raise_for_status()
            else:
                raise SystemExit(1)
            break
        time.sleep(1)
