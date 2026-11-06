"""Bridge pre-generated sentence audio to Manim Voiceover's actual timing."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from manim_voiceover.services.base import SpeechService

ROOT = Path(__file__).resolve().parent.parent


class KokoroService(SpeechService):
    def __init__(self, lines):
        super().__init__()
        subprocess.run([os.environ["TALOTRACE_TTS_PYTHON"], str(ROOT / "app" / "synthesize.py"), str(self.cache_dir)],
                       input=json.dumps(lines), text=True, check=True)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        name = hashlib.sha256(text.encode("utf-8")).hexdigest()[:20] + ".wav"
        audio = Path(self.cache_dir) / name
        if not audio.is_file() or audio.stat().st_size == 0:
            raise RuntimeError("Missing Kokoro narration sentence")
        return {"input_text": text, "input_data": {"input_text": text, "service": "kokoro", "voice": "af_heart"},
                "original_audio": name}
