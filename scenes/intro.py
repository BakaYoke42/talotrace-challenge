"""Manim diagrams for the reviewed, ordered JSON storyboards."""
import os
from pathlib import Path
import subprocess

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService
from pydub import AudioSegment

from app.scenarios import Scenario

ROOT = Path(__file__).resolve().parent.parent
AudioSegment.converter = os.environ["TALOTRACE_FFMPEG"]
BLUE = "#70C9F0"
PINK = "#F48FB1"
GOLD = "#FFD166"


class KokoroService(SpeechService):
    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_data = {"input_text": text, "service": "kokoro", "voice": "af_heart"}
        audio_name = path or self.get_audio_basename(input_data) + ".wav"
        subprocess.run([os.environ["TALOTRACE_TTS_PYTHON"], str(ROOT / "app" / "synthesize.py"), str(cache_dir / audio_name)],
                       input=text, text=True, check=True)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_name)}


def label(text, size=28, color=WHITE):
    return Text(text, font_size=size, color=color)


def atom(text, color=BLUE, radius=0.48):
    return VGroup(Circle(radius=radius, color=color, fill_color=color, fill_opacity=0.23, stroke_width=3),
                  label(text, 26)).move_to(ORIGIN)


def icon(filename, fallback):
    path = ROOT / "images_pour_videos" / filename
    if path.is_file():
        return SVGMobject(str(path), height=1.1)
    return VGroup(Circle(radius=0.5, color=GOLD), label(fallback, 19))


def heading(title, content):
    content.scale_to_fit_width(min(content.width, 11.5))
    if content.height > 4.5:
        content.scale_to_fit_height(4.5)
    content.move_to(DOWN * 0.35)
    return VGroup(label(title, 33, BLUE).to_edge(UP, buff=0.45), content)


def ion_comparison():
    left = VGroup(atom("H₃O⁺", BLUE, 0.52), label("hydronium", 22)).arrange(DOWN, buff=0.25)
    right = VGroup(atom("H₂O", "#A8DADC", 0.52), label("water", 22)).arrange(DOWN, buff=0.25)
    return VGroup(left, label("in water", 23), right).arrange(RIGHT, buff=0.65)


def ph_scale():
    colors = ["#F05D5E", "#F58E62", "#F9C66B", "#73C991", "#56A5D8", "#8474C2", "#A16FB2"]
    blocks = VGroup(*[Rectangle(width=1.15, height=0.75, fill_color=c, fill_opacity=0.95, stroke_width=0) for c in colors]).arrange(RIGHT, buff=0)
    numbers = VGroup(*[label(str(n), 21) for n in (0, 2, 4, 7, 10, 12, 14)]).arrange(RIGHT, buff=0.8)
    names = VGroup(label("ACIDIC", 24, PINK), label("NEUTRAL", 24, "#73C991"), label("BASIC", 24, BLUE)).arrange(RIGHT, buff=0.65)
    examples = VGroup(icon("final_lemon.svg", "lemon"), label("lemon", 19), label("water ≈ 7 at 25°C", 20)).arrange(RIGHT, buff=0.35)
    return VGroup(names, blocks, numbers, examples, label("Common range, not a hard limit", 19)).arrange(DOWN, buff=0.28)


def two_hydrogens(shared=False):
    first = atom("H", BLUE).shift(LEFT * (0.8 if shared else 1.6))
    second = atom("H", BLUE).shift(RIGHT * (0.8 if shared else 1.6))
    parts = [first, second]
    if shared:
        cloud = Ellipse(width=2.55, height=1.3, color=GOLD, fill_color=GOLD, fill_opacity=0.17)
        electrons = VGroup(Dot(LEFT * 0.13, color=GOLD, radius=0.07), Dot(RIGHT * 0.13, color=GOLD, radius=0.07))
        parts = [cloud, first, second, electrons]
    else:
        parts += [Dot(LEFT * 1.6 + UP * 0.8, color=GOLD), Dot(RIGHT * 1.6 + UP * 0.8, color=GOLD)]
    return VGroup(*parts)


def energy_curve():
    axes = Axes(x_range=[0, 5, 1], y_range=[-2, 2, 1], x_length=7.2, y_length=3.3,
                axis_config={"include_numbers": False, "include_tip": True})
    curve = axes.plot(lambda x: 1.5 * ((1.7 / x) ** 4 - 2 * (1.7 / x) ** 2), x_range=[1.05, 5], color=GOLD)
    dot = Dot(axes.c2p(1.7, -1.5), color=PINK)
    return VGroup(axes, curve, dot, label("Energy", 21).next_to(axes, UP),
                  label("Distance between nuclei →", 21).next_to(axes, DOWN),
                  label("minimum", 21, PINK).next_to(dot, RIGHT))


def lattice():
    items = VGroup()
    for row in range(3):
        for col in range(5):
            positive = (row + col) % 2 == 0
            items.add(atom("Na⁺" if positive else "Cl⁻", BLUE if positive else PINK, 0.32).move_to([col * 0.8, -row * 0.8, 0]))
    return VGroup(items, label("Alternating ions in a crystal lattice", 22).next_to(items, DOWN, buff=0.3))


def water_molecule():
    oxygen = atom("O", PINK, 0.6)
    left = atom("H", BLUE, 0.38).shift(LEFT * 1.5 + DOWN * 0.75)
    right = atom("H", BLUE, 0.38).shift(RIGHT * 1.5 + DOWN * 0.75)
    lines = VGroup(Line(oxygen.get_center(), left.get_center(), color=GOLD, stroke_width=7),
                   Line(oxygen.get_center(), right.get_center(), color=GOLD, stroke_width=7))
    molecule = VGroup(lines, oxygen, left, right)
    return VGroup(molecule, label("O–H bonds: polar covalent", 23).next_to(molecule, DOWN, buff=0.3))


def comparison(left_title, left_text, right_title, right_text):
    left = VGroup(label(left_title, 29, PINK), label(left_text, 23)).arrange(DOWN, buff=0.35)
    right = VGroup(label(right_title, 29, BLUE), label(right_text, 23)).arrange(DOWN, buff=0.35)
    return VGroup(left, right).arrange(RIGHT, buff=1.3)


def diagram(visual, parameters):
    if visual == "hydronium":
        return heading("Hydronium in solution", ion_comparison())
    if visual == "ph_scale":
        return heading("A common pH scale", ph_scale())
    if visual == "logarithmic":
        return heading("A logarithmic scale", VGroup(label("pH decreases by 1", 30), label("hydrogen ion activity × 10", 32, GOLD)).arrange(DOWN, buff=0.6))
    if visual == "activity_comparison":
        return heading("Compare hydrogen ion activity", comparison("pH 3", "10 × activity", "pH 4", "1 × activity"))
    if visual == "ph_recap":
        return heading("pH: key idea", VGroup(label("Lower pH → higher activity", 32), label("One pH unit → factor of 10", 28, GOLD)).arrange(DOWN, buff=0.55))
    if visual == "hydrogen_atoms":
        return heading("Two hydrogen atoms", two_hydrogens())
    if visual == "electron_density":
        return heading("Shared electron density", two_hydrogens(True))
    if visual == "energy_curve":
        return heading("An energetically favorable distance", energy_curve())
    if visual == "hydrogen_molecule":
        molecule = two_hydrogens(True)
        return heading("A hydrogen molecule", VGroup(molecule, label("H₂: shared electron pair", 25).next_to(molecule, DOWN, buff=0.5)))
    if visual == "covalent_recap":
        return heading("Covalent bonding", VGroup(label("Shared electron density", 31), label("A lower-energy bonded state", 27, GOLD)).arrange(DOWN, buff=0.5))
    if visual == "salt_and_water":
        salt = VGroup(icon("final_sel.svg", "salt"), label("NaCl · salt", 25)).arrange(DOWN)
        water = VGroup(icon("final_water.svg", "water"), label("H₂O · water", 25)).arrange(DOWN)
        return heading("Two familiar substances", VGroup(salt, water).arrange(RIGHT, buff=2))
    if visual == "ionic_lattice":
        transfer = VGroup(label("Na → Na⁺ + e⁻", 24), label("Cl + e⁻ → Cl⁻", 24)).arrange(RIGHT, buff=0.8)
        grid = lattice()
        return heading("Ionic bonding", VGroup(transfer, grid).arrange(DOWN, buff=0.4))
    if visual == "polar_water":
        return heading("Covalent bonding in water", water_molecule())
    if visual == "bond_comparison":
        return heading("Compare the models", comparison("IONIC", "attraction of ions", "COVALENT", "shared electrons"))
    if visual == "bond_recap":
        return heading("Two bonding models", comparison("NaCl", "ion lattice", "H₂O", "polar shared bonds"))
    raise ValueError(f"Unsupported visual: {visual}")


class ChemistryIntro(VoiceoverScene):
    def construct(self):
        scenario = Scenario.model_validate_json(Path(os.environ["TALOTRACE_SCENARIO"]).read_text(encoding="utf-8"))
        if scenario.concept_id != os.environ["TALOTRACE_CONCEPT"]:
            raise ValueError("Scenario does not match the requested concept")
        self.set_speech_service(KokoroService())
        for segment in scenario.segments:
            visuals = diagram(segment.visual, segment.parameters)
            with self.voiceover(text=segment.narration) as tracker:
                self.play(FadeIn(visuals), run_time=min(0.5, tracker.duration))
            self.play(FadeOut(visuals), run_time=0.3)
