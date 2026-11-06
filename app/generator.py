import logging
import os
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self, artifact_root: Path, timeout: int = 600):
        self.artifact_root = artifact_root
        self.timeout = timeout

    def __call__(self, job: dict) -> bool:
        job_dir = self.artifact_root / job["job_id"]
        job_dir.mkdir(parents=True, exist_ok=True)
        temporary = job_dir / "render.mp4"
        env = os.environ.copy()
        env.update({"TALOTRACE_CONCEPT": job["concept"],
                    "TALOTRACE_TTS_PYTHON": str(ROOT / ".venv-tts" / "Scripts" / "python.exe"),
                    "TALOTRACE_FFMPEG": imageio_ffmpeg.get_ffmpeg_exe(),
                    "HF_HUB_OFFLINE": "1"})
        command = [sys.executable, "-m", "manim", "--disable_caching", "-r", "854,480", "--fps", "30",
                   "--media_dir", str(job_dir / "media"), "-o", str(temporary),
                   str(ROOT / "scenes" / "intro.py"), "ChemistryIntro"]
        with (job_dir / "render.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=self.timeout, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Manim exited with code {result.returncode}; see render.log")
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("Manim did not produce a nonempty video")
        temporary.replace(job_dir / "video.mp4")
        return True
