"""Submit one actual rendering job through the API and report process status."""
import argparse
import time

from fastapi.testclient import TestClient

from app.main import QUESTIONS, app

parser = argparse.ArgumentParser()
parser.add_argument("--concept", choices=list(QUESTIONS.values()), default="ph_scale")
args = parser.parse_args()
question = next(question for question, concept in QUESTIONS.items() if concept == args.concept)

with TestClient(app) as client:
    response = client.post("/videos", json={"question": question})
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
