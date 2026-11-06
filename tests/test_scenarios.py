import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.generator import VideoGenerator
from app.scenarios import CONCEPTS, Scenario, load_scenario


@pytest.mark.parametrize("concept", CONCEPTS)
def test_scenario_loads_and_matches_mapping(concept):
    scenario = load_scenario(concept)
    question, _, visuals = CONCEPTS[concept]
    assert scenario.question == question
    assert [segment.visual for segment in scenario.segments] == visuals
    assert all(segment.narration for segment in scenario.segments)


@pytest.mark.parametrize("change", ["unknown_visual", "reordered", "empty_narration", "wrong_question", "duplicate_id", "extra_field"])
def test_invalid_scenarios_are_rejected(change):
    data = load_scenario("ph_scale").model_dump()
    if change == "unknown_visual":
        data["segments"][0]["visual"] = "unknown"
    elif change == "reordered":
        data["segments"].reverse()
    elif change == "empty_narration":
        data["segments"][0]["narration"] = "   "
    elif change == "wrong_question":
        data["question"] = "Another question"
    elif change == "duplicate_id":
        data["segments"][1]["id"] = data["segments"][0]["id"]
    else:
        data["segments"][0]["script"] = "bad"
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


def test_scenario_must_match_requested_concept(tmp_path):
    filename = CONCEPTS["ph_scale"][1]
    (tmp_path / filename).write_text(load_scenario("covalent").model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError, match="requested concept"):
        load_scenario("ph_scale", tmp_path)
    with pytest.raises(ValueError, match="Unknown concept"):
        load_scenario("unknown", tmp_path)


def test_invalid_scenario_prevents_render(tmp_path, monkeypatch):
    import app.generator as generator
    data = load_scenario("ph_scale").model_dump()
    data["segments"][0]["visual"] = "not_supported"
    (tmp_path / "ph_scale.json").write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(generator, "load_scenario", lambda concept: load_scenario(concept, tmp_path))
    monkeypatch.setattr(generator.subprocess, "run", lambda *a, **k: pytest.fail("Render must not start"))
    with pytest.raises(ValidationError):
        VideoGenerator(tmp_path / "artifacts")({"job_id": str(uuid4()), "concept": "ph_scale", "question": CONCEPTS["ph_scale"][0]})
