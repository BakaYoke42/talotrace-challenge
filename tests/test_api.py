import time
from threading import Event
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.jobs import JobStore
from app.main import QUESTIONS, create_app
from app.worker import simulated_executor


def wait_for(client, job_id, status):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        job = client.get(f"/videos/{job_id}").json()
        if job["status"] == status:
            return job
        time.sleep(0.01)
    pytest.fail(f"Job {job_id} did not reach {status}: {job}")


@pytest.mark.parametrize("question,concept", QUESTIONS.items())
def test_contract(tmp_path, question, concept):
    with TestClient(create_app(tmp_path / "jobs.db", simulated_executor)) as client:
        response = client.post("/videos", json={"question": question})
        assert response.status_code == 202
        job = response.json()
        assert job["status"] == "queued" and job["concept"] == concept
        done = wait_for(client, job["job_id"], "completed")
        assert done["stage"] == "simulated" and done["artifact_url"] is None
        assert client.get(f"/videos/{job['job_id']}/file").status_code == 409
        assert client.get("/videos").json() == [done]
        assert client.get("/docs").status_code == 200


def test_invalid_requests(tmp_path):
    with TestClient(create_app(tmp_path / "jobs.db", simulated_executor)) as client:
        assert client.post("/videos", json={"question": "Other question"}).status_code == 422
        assert client.post("/videos", json={}).status_code == 422
        assert client.get("/videos/not-a-uuid").status_code == 422
        assert client.get(f"/videos/{uuid4()}").status_code == 404
        assert client.get(f"/videos/{uuid4()}/file").status_code == 404
        assert client.get("/videos").json() == []


def test_fifo_and_responsive_api(tmp_path):
    started, release = Event(), Event()
    order = []

    def slow_executor(job):
        order.append(job["job_id"])
        if len(order) == 1:
            started.set()
            if not release.wait(5):
                raise TimeoutError("test timed out")

    with TestClient(create_app(tmp_path / "jobs.db", slow_executor)) as client:
        try:
            first = client.post("/videos", json={"question": list(QUESTIONS)[0]}).json()
            assert started.wait(3)
            before = time.monotonic()
            response = client.post("/videos", json={"question": list(QUESTIONS)[1]})
            assert time.monotonic() - before < 2
            assert response.status_code == 202
            second = response.json()
            assert client.get(f"/videos/{first['job_id']}").json()["status"] == "processing"
            assert client.get(f"/videos/{second['job_id']}").json()["status"] == "queued"
            assert order == [first["job_id"]]
        finally:
            release.set()
        wait_for(client, second["job_id"], "completed")
        assert order == [first["job_id"], second["job_id"]]
        assert wait_for(client, first["job_id"], "completed")


def test_failure_and_restart_recovery(tmp_path):
    path = tmp_path / "jobs.db"
    def failing(job):
        raise RuntimeError("sensitive internal detail")

    with TestClient(create_app(path, failing)) as client:
        job = client.post("/videos", json={"question": next(iter(QUESTIONS))}).json()
        failed = wait_for(client, job["job_id"], "failed")
        assert failed["error"] == "Job execution failed"
        assert client.get(f"/videos/{job['job_id']}/file").status_code == 409

    store = JobStore(path)
    interrupted = {"job_id": str(uuid4()), "question": next(iter(QUESTIONS)), "concept": "ph_scale",
                   "status": "processing", "stage": "simulated", "error": None, "artifact_url": None}
    pending = dict(interrupted, job_id=str(uuid4()), status="queued", stage=None)
    store.create(interrupted)
    store.create(pending)
    with TestClient(create_app(path, simulated_executor)) as client:
        assert client.get(f"/videos/{job['job_id']}").json()["status"] == "failed"
        recovered = client.get(f"/videos/{interrupted['job_id']}").json()
        assert recovered["status"] == "failed"
        assert recovered["error"] == "Processing interrupted by a restart"
        wait_for(client, pending["job_id"], "completed")
