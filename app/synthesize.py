"""Run in the separate Kokoro environment; text arrives on standard input."""
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

text = sys.stdin.read()
pipeline = KPipeline(lang_code="a")
chunks = [audio for _, _, audio in pipeline(text, voice="af_heart")]
if not chunks:
    raise RuntimeError("Kokoro produced no audio")
sf.write(sys.argv[1], np.concatenate(chunks), 24000)
