"""Generate job-specific narration sentences with one local Kokoro model instance."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline


def audio_name(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20] + ".wav"


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    lines = json.loads(sys.stdin.read())
    torch.set_num_threads(4)
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    for line in dict.fromkeys(lines):
        chunks = [audio for _, _, audio in pipeline(line, voice="af_heart")]
        if not chunks:
            raise RuntimeError("Kokoro produced no audio")
        sf.write(output / audio_name(line), np.concatenate(chunks), 24000)


if __name__ == "__main__":
    main()
