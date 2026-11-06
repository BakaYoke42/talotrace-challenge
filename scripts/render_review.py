"""Render selected topics through the API and save human-friendly numbered copies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time

from fastapi.testclient import TestClient

from app.main import QUESTIONS, app

NAMES = {"ph_scale": "ph-scale", "covalent": "covalent-bonds", "ionic_vs_covalent": "ionic-vs-covalent"}
ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"


def save_review(job, content):
    prefix = NAMES[job["concept"]]
    versions = [int(match.group(1)) for path in ARTIFACTS.glob(prefix + "-v*.mp4")
                if (match := re.fullmatch(re.escape(prefix) + r"-v(\d+)\.mp4", path.name))]
    version = max(versions, default=0) + 1
    while True:
        output = ARTIFACTS / f"{prefix}-v{version:02d}.mp4"
        try:
            with output.open("xb") as stream:
                stream.write(content)
            break
        except FileExistsError:
            version += 1
    record = {"file": output.name, "job_id": job["job_id"], "question": job["question"],
              "sha256": hashlib.sha256(content).hexdigest()}
    with (ARTIFACTS / "review-index.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept", choices=list(NAMES), action="append")
    args = parser.parse_args()
    requested = args.concept or list(NAMES)
    pending = set()
    failed = False
    with TestClient(app) as client:
        for question, concept in QUESTIONS.items():
            if concept in requested:
                response = client.post("/videos", json={"question": question})
                response.raise_for_status()
                job = response.json()
                pending.add(job["job_id"])
                print(f"Queued {concept}: {job['job_id']}", flush=True)
        while pending:
            for job_id in list(pending):
                response = client.get(f"/videos/{job_id}")
                response.raise_for_status()
                job = response.json()
                if job["status"] == "completed":
                    artifact = client.get(job["artifact_url"])
                    artifact.raise_for_status()
                    if not artifact.content:
                        raise RuntimeError("Empty video artifact")
                    output = save_review(job, artifact.content)
                    print(f"Completed: {output} ({len(artifact.content)} bytes, HTTP 200)", flush=True)
                    pending.remove(job_id)
                elif job["status"] == "failed":
                    print(f"FAILED {job_id}: {job['error']}", flush=True)
                    failed = True
                    pending.remove(job_id)
            time.sleep(1)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
