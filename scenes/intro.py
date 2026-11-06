"""Minimal narrated integration scene; full scientific scenarios come later."""
import os
from pathlib import Path
import subprocess
import sys

from manim import FadeIn, Text, VGroup
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parent.parent
AudioSegment.converter = os.environ["TALOTRACE_FFMPEG"]

TOPICS = {
    "ph_scale": ("The pH scale", "The pH scale describes how acidic or basic an aqueous solution is."),
    "covalent": ("Covalent bonds", "A covalent bond involves shared electron density between atoms."),
    "ionic_vs_covalent": ("Ionic and covalent bonding", "Ionic bonding involves attraction between ions. Covalent bonding involves shared electron density."),
}


class KokoroService(SpeechService):
    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_data = {"input_text": text, "service": "kokoro", "voice": "af_heart"}
        audio_name = path or self.get_audio_basename(input_data) + ".wav"
        subprocess.run([os.environ["TALOTRACE_TTS_PYTHON"], str(ROOT / "app" / "synthesize.py"), str(cache_dir / audio_name)],
                       input=text, text=True, check=True)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_name)}


class ChemistryIntro(VoiceoverScene):
    def construct(self):
        title, narration = TOPICS[os.environ["TALOTRACE_CONCEPT"]]
        self.set_speech_service(KokoroService())
        visuals = VGroup(Text("CHEMISTRY", font_size=24, color="#81D4FA"), Text(title, font_size=42)).arrange(direction=[0, -1, 0], buff=0.5)
        with self.voiceover(text=narration) as tracker:
            self.play(FadeIn(visuals), run_time=min(1, tracker.duration))
