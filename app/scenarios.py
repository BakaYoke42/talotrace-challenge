import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parent.parent


def narration_lines(text: str) -> list[str]:
    """Storyboards use complete sentences without abbreviations or decimal numbers."""
    return re.split(r"(?<=[.!?])\s+", text.strip())
CONCEPTS = {
    "ph_scale": ("How does the pH scale work?", "ph_scale.json", ["hydronium", "ph_scale", "logarithmic", "activity_comparison", "ph_recap"]),
    "covalent": ("Why do atoms form covalent bonds?", "covalent_bonds.json", ["hydrogen_atoms", "electron_density", "energy_curve", "hydrogen_molecule", "covalent_recap"]),
    "ionic_vs_covalent": ("What is the difference between ionic and covalent bonding?", "ionic_vs_covalent.json", ["salt_and_water", "ionic_lattice", "polar_water", "bond_comparison", "bond_recap"]),
}


class Segment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str = Field(min_length=1)
    visual: str = Field(min_length=1)
    narration: str = Field(min_length=1)
    parameters: dict[str, str | int | float | bool] = Field(default_factory=dict)


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: Literal[1]
    concept_id: Literal["ph_scale", "covalent", "ionic_vs_covalent"]
    question: str = Field(min_length=1)
    scene_type: Literal["ph_scale", "covalent", "ionic_vs_covalent"]
    segments: list[Segment] = Field(min_length=1)

    @model_validator(mode="after")
    def check_sequence(self):
        question, _, visuals = CONCEPTS[self.concept_id]
        if self.question != question or self.scene_type != self.concept_id:
            raise ValueError("Scenario question or scene type does not match concept")
        if [segment.visual for segment in self.segments] != visuals:
            raise ValueError("Unsupported or out-of-order visual sequence")
        if len({segment.id for segment in self.segments}) != len(self.segments):
            raise ValueError("Segment IDs must be unique")
        return self


def load_scenario(concept: str, directory: Path | None = None) -> Scenario:
    if concept not in CONCEPTS:
        raise ValueError("Unknown concept")
    directory = directory or ROOT / "knowledge"
    data = json.loads((directory / CONCEPTS[concept][1]).read_text(encoding="utf-8"))
    scenario = Scenario.model_validate(data)
    if scenario.concept_id != concept:
        raise ValueError("Scenario concept does not match requested concept")
    return scenario
