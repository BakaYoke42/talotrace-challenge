import imageio_ffmpeg
import pytest

from app.scenarios import CONCEPTS, load_scenario


def test_each_storyboard_visual_builds(monkeypatch):
    monkeypatch.setenv("TALOTRACE_FFMPEG", imageio_ffmpeg.get_ffmpeg_exe())
    from scenes.intro import diagram

    for concept in CONCEPTS:
        for segment in load_scenario(concept).segments:
            assert len(diagram(segment.visual, segment.parameters)) > 0
    with pytest.raises(ValueError):
        diagram("unknown", {})
