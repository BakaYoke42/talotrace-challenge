"""Demonstrate all three questions against a running HTTP server, generating fresh media."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import httpx

from app.scenarios import CONCEPTS
from scripts.render_review import save_review


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--wait-seconds", type=int, default=2100)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    report = {"transport": "HTTP", "base_url": base_url, "jobs": []}
    states = {}
    pending = set()
    with httpx.Client(base_url=base_url, timeout=30) as client:
        assert client.get("/docs").status_code == 200
        assert client.post("/videos", json={"question": "unsupported question"}).status_code == 422
        for concept, (question, _, _) in CONCEPTS.items():
            before = time.monotonic()
            response = client.post("/videos", json={"question": question})
            response.raise_for_status()
            assert response.status_code == 202
            job = response.json()
            elapsed = round(time.monotonic() - before, 3)
            assert job["status"] == "queued" and job["concept"] == concept
            pending.add(job["job_id"])
            report["jobs"].append({"job_id": job["job_id"], "question": question, "concept": concept,
                                    "post_status": 202, "post_seconds": elapsed, "states": ["queued"]})
            print(f"POST /videos -> 202 in {elapsed}s: {concept} ({job['job_id']})", flush=True)
        listed = client.get("/videos")
        listed.raise_for_status()
        assert pending.issubset({job["job_id"] for job in listed.json()})
        print("GET /videos -> 200; all three requests are listed", flush=True)
        deadline = time.monotonic() + args.wait_seconds
        try:
            while pending:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Demonstration exceeded its waiting limit; server jobs may still be running")
                for item in report["jobs"]:
                    job_id = item["job_id"]
                    if job_id not in pending:
                        continue
                    response = client.get(f"/videos/{job_id}")
                    response.raise_for_status()
                    job = response.json()
                    if states.get(job_id) != job["status"]:
                        print(f"GET /videos/{job_id} -> {job['status']}", flush=True)
                        states[job_id] = job["status"]
                        if item["states"][-1] != job["status"]:
                            item["states"].append(job["status"])
                    if job["status"] == "failed":
                        item["error"] = job["error"]
                        raise RuntimeError(f"{item['concept']} failed: {job['error']}")
                    if job["status"] != "completed":
                        assert client.get(f"/videos/{job_id}/file").status_code == 409
                        continue
                    artifact = client.get(job["artifact_url"])
                    artifact.raise_for_status()
                    assert artifact.headers["content-type"].startswith("video/mp4") and artifact.content
                    path = save_review(job, artifact.content)
                    item.update({"file": path.name, "file_status": artifact.status_code,
                                 "bytes": len(artifact.content), "sha256": hashlib.sha256(artifact.content).hexdigest()})
                    print(f"GET {job['artifact_url']} -> 200; {path.name} ({len(artifact.content)} bytes)", flush=True)
                    pending.remove(job_id)
                time.sleep(1)
        finally:
            report_path = Path(__file__).resolve().parent.parent / "artifacts" / "final-demo-report.json"
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Report: {report_path}", flush=True)
    print("All three fresh renders completed and were downloaded through HTTP.", flush=True)


if __name__ == "__main__":
    main()
