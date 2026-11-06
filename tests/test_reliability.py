import subprocess
from pathlib import Path
from threading import Event
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.generator import VideoGenerator
from app.main import QUESTIONS, create_app
from tests.test_api import wait_for


def test_repeated_and_multiple_jobs_are_isolated_and_fifo(tmp_path, monkeypatch):
    calls = []
    first_started, release = Event(), Event()

    def render(command, **kwargs):
        output = Path(command[command.index("-o") + 1])
        calls.append(output.parent.name)
        if len(calls) == 1:
            first_started.set()
            assert release.wait(5)
        output.write_bytes(f"artifact for {output.parent.name}".encode())
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", render)
    root = tmp_path / "artifacts"
    with TestClient(create_app(tmp_path / "jobs.db", artifact_root=root)) as client:
        try:
            questions = list(QUESTIONS)
            requested = [questions[0], questions[0], questions[1], questions[2]]
            first = client.post("/videos", json={"question": requested[0]}).json()
            assert first_started.wait(3)
            jobs = [first] + [client.post("/videos", json={"question": q}).json() for q in requested[1:]]
            ids = [job["job_id"] for job in jobs]
            assert len(set(ids)) == len(ids)
            assert client.get(f"/videos/{ids[0]}").json()["status"] == "processing"
            for job_id in ids[1:]:
                assert client.get(f"/videos/{job_id}").json()["status"] == "queued"
                assert client.get(f"/videos/{job_id}/file").status_code == 409
        finally:
            release.set()
        for job_id in ids:
            done = wait_for(client, job_id, "completed")
            response = client.get(done["artifact_url"])
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("video/mp4")
            assert response.content == f"artifact for {job_id}".encode()
            assert (root / job_id / "video.mp4").read_bytes() == response.content
        assert calls == ids


@pytest.mark.parametrize("timeout", [False, True])
def test_failure_then_next_job_succeeds(tmp_path, monkeypatch, timeout):
    count = 0

    def render(command, **kwargs):
        nonlocal count
        count += 1
        if count == 1:
            if timeout:
                raise subprocess.TimeoutExpired(command, 1)
            return subprocess.CompletedProcess(command, 7)
        Path(command[command.index("-o") + 1]).write_bytes(b"second job")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", render)
    with TestClient(create_app(tmp_path / "jobs.db", artifact_root=tmp_path / "artifacts")) as client:
        first = client.post("/videos", json={"question": list(QUESTIONS)[0]}).json()
        second = client.post("/videos", json={"question": list(QUESTIONS)[1]}).json()
        failed = wait_for(client, first["job_id"], "failed")
        assert failed["error"] == ("Video rendering timed out" if timeout else "Job execution failed")
        assert failed["artifact_url"] is None
        assert client.get(f"/videos/{first['job_id']}/file").status_code == 409
        done = wait_for(client, second["job_id"], "completed")
        assert client.get(done["artifact_url"]).content == b"second job"


def test_reject_existing_job_directory_and_invalid_id(tmp_path, monkeypatch):
    root = tmp_path / "artifacts"
    job_id = str(uuid4())
    job_dir = root / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "render.mp4").write_bytes(b"old render")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: pytest.fail("must not run"))
    job = {"job_id": job_id, "concept": "ph_scale", "question": list(QUESTIONS)[0]}
    with pytest.raises(FileExistsError):
        VideoGenerator(root)(job)
    assert not (job_dir / "video.mp4").exists()
    with pytest.raises(ValueError):
        VideoGenerator(root)(dict(job, job_id="../outside"))


def test_file_route_rejects_traversal_and_missing_artifact(tmp_path, monkeypatch):
    def render(command, **kwargs):
        Path(command[command.index("-o") + 1]).write_bytes(b"artifact")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", render)
    root = tmp_path / "artifacts"
    with TestClient(create_app(tmp_path / "jobs.db", artifact_root=root)) as client:
        job = client.post("/videos", json={"question": list(QUESTIONS)[0]}).json()
        done = wait_for(client, job["job_id"], "completed")
        for path in ["/videos/%2e%2e/file", "/videos/%2e%2e%2fsecret/file", "/videos/not-a-uuid/file"]:
            assert client.get(path).status_code in (404, 422)
        assert client.get(f"/videos/{uuid4()}/file").status_code == 404
        (root / job["job_id"] / "video.mp4").unlink()
        assert client.get(done["artifact_url"]).status_code == 404
