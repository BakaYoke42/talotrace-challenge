import subprocess
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.generator import VideoGenerator
from app.main import QUESTIONS, create_app
from tests.test_api import wait_for


def test_subprocess_success_and_artifact_endpoint(tmp_path, monkeypatch):
    def render(command, **kwargs):
        output = command[command.index("-o") + 1]
        from pathlib import Path
        Path(output).write_bytes(b"test artifact")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", render)
    root = tmp_path / "artifacts"
    with TestClient(create_app(tmp_path / "jobs.db", artifact_root=root)) as client:
        job = client.post("/videos", json={"question": next(iter(QUESTIONS))}).json()
        done = wait_for(client, job["job_id"], "completed")
        assert done["artifact_url"] == f"/videos/{job['job_id']}/file"
        response = client.get(done["artifact_url"])
        assert response.status_code == 200 and response.content == b"test artifact"


@pytest.mark.parametrize("behavior", ["failure", "timeout", "missing", "empty"])
def test_render_failure_does_not_publish(tmp_path, monkeypatch, behavior):
    def render(command, **kwargs):
        if behavior == "timeout":
            raise subprocess.TimeoutExpired(command, 1)
        if behavior == "empty":
            from pathlib import Path
            Path(command[command.index("-o") + 1]).touch()
        return subprocess.CompletedProcess(command, 1 if behavior == "failure" else 0)

    monkeypatch.setattr(subprocess, "run", render)
    root = tmp_path / "artifacts"
    job_id = str(uuid4())
    with pytest.raises((RuntimeError, subprocess.TimeoutExpired)):
        VideoGenerator(root)({"job_id": job_id, "concept": "ph_scale"})
    assert not (root / job_id / "video.mp4").exists()
