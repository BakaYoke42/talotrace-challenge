import pytest

from app.scenarios import CONCEPTS, load_scenario, narration_lines


class SceneStub:
    def __init__(self):
        self.calls = 0

    def play(self, *animations, **kwargs):
        self.calls += 1
        assert animations
        assert kwargs.get("run_time", 1) > 0


def exercise_topic(concept, module, monkeypatch):
    spoken = []

    def say(scene, line, action):
        spoken.append(line)
        action(3)

    monkeypatch.setattr(module, "say", say)
    animate = module.animate_ph_segment if concept == "ph_scale" else module.animate_bond_segment
    for segment in load_scenario(concept).segments:
        scene = SceneStub()
        lines = narration_lines(segment.narration)
        spoken.clear()
        assert len(animate(scene, segment.visual, lines, segment.parameters)) > 0
        assert scene.calls >= len(lines)
        assert spoken == lines
    with pytest.raises(ValueError):
        animate(SceneStub(), "unknown", ["Unknown."])


def test_each_storyboard_visual_builds(monkeypatch):
    from scenes import ph
    exercise_topic("ph_scale", ph, monkeypatch)


def test_bonding_segments_construct_animations(monkeypatch):
    from scenes import bonding
    exercise_topic("covalent", bonding, monkeypatch)
    exercise_topic("ionic_vs_covalent", bonding, monkeypatch)


def test_ph_lemon_metaphor_is_explicit():
    from scenes.ph import comparison
    pair, notice = comparison()
    assert len(pair[0][1]) == 10
    assert "METAPHORONLY" in notice[0].text.replace(" ", "")
    assert "doesnotmeasurepH" in notice[1].text.replace(" ", "")
    narration = load_scenario("ph_scale").segments[3].narration.lower()
    assert "visual metaphor" in narration and "does not measure ph" in narration


def test_water_shared_electrons_and_crystal_pattern():
    from scenes.style import crystal_lattice, water_diagram
    water = water_diagram()
    assert len(water[0]) == 2
    assert len(water[4]) == 4
    assert len(water[5]) == 4
    lattice = crystal_lattice()
    assert len(lattice) == 12
    for row in range(3):
        for col in range(4):
            expected = "Na⁺" if (row + col) % 2 == 0 else "Cl⁻"
            assert lattice[row * 4 + col][1].text == expected


def test_changed_sentence_count_is_rejected():
    from scenes.ph import animate_ph_segment
    with pytest.raises(ValueError, match="expects 3 narrated sentences"):
        animate_ph_segment(SceneStub(), "hydronium", ["Only one sentence."])
