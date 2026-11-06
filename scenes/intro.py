"""One backend entry point, with explicit diagrams and sentence-level voiceover cues."""
import os
from pathlib import Path

from manim import DOWN, FadeIn, FadeOut, Line, LEFT, RIGHT, VGroup, config
from manim_voiceover import VoiceoverScene
from pydub import AudioSegment

from app.scenarios import Scenario, narration_lines
from scenes.bonding import animate_bond_segment
from scenes.ph import animate_ph_segment
from scenes.speech import KokoroService
from scenes.style import BG, BLUE, MUTED, text

AudioSegment.converter = os.environ["TALOTRACE_FFMPEG"]


class ChemistryIntro(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG
        scenario = Scenario.model_validate_json(Path(os.environ["TALOTRACE_SCENARIO"]).read_text(encoding="utf-8"))
        if scenario.concept_id != os.environ["TALOTRACE_CONCEPT"]:
            raise ValueError("Scenario does not match the requested concept")
        lines = [line for segment in scenario.segments for line in narration_lines(segment.narration)]
        self.set_speech_service(KokoroService(lines))
        for index, segment in enumerate(scenario.segments):
            progress = Line(LEFT * 6 + DOWN * 3.7, (LEFT * 6 + RIGHT * (12 * (index + 1) / 5)) + DOWN * 3.7,
                            color=BLUE, stroke_width=3)
            self.add(progress)
            if scenario.concept_id == "ph_scale":
                visuals = animate_ph_segment(self, segment.visual, narration_lines(segment.narration), segment.parameters)
            else:
                visuals = animate_bond_segment(self, segment.visual, narration_lines(segment.narration), segment.parameters)
            self.play(FadeOut(visuals, shift=LEFT * 0.15), FadeOut(progress), run_time=0.35)
        credit = VGroup(text("CHEMISTRY, EXPLAINED", 26, BLUE),
                        text("Science: OpenStax Chemistry 2e · IUPAC pH definition", 16, MUTED),
                        text("Illustrations: OpenMoji · CC BY-SA 4.0 · openmoji.org", 16, MUTED)).arrange(DOWN, buff=0.3)
        self.play(FadeIn(credit), run_time=0.35)
        self.wait(1)
