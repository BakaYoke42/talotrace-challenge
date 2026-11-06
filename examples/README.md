# Latest generated examples

These are the latest selected versions produced through the HTTP API. Their
scientific scripts and visual direction match the final source; the version number
advances because each request produces a fresh render. Earlier iterations remain in
the ignored local `artifacts/` directory and are not included here.

| Learner question | File |
| --- | --- |
| How does the pH scale work? | [ph-scale-v06.mp4](ph-scale-v06.mp4) |
| Why do atoms form covalent bonds? | [covalent-bonds-v05.mp4](covalent-bonds-v05.mp4) |
| What is the difference between ionic and covalent bonding? | [ionic-vs-covalent-v05.mp4](ionic-vs-covalent-v05.mp4) |

`manifest.json` records the question, concept, originating job ID, byte count and SHA-256
for each included file. `demo-report.json` preserves the original three-question run;
its pH v05 was subsequently replaced by the latest pH v06 from the live walkthrough.
`ph-walkthrough-report.json` records that later request, observed states, not-ready
response and MP4 download. Hashes verify file identity; they do not assess video
or audio quality. All automated checks were limited to code, process and file behavior.
The candidate is responsible for watching and listening to the examples.

The generator never reads this directory. It renders into a new per-job directory for
every request. Output was configured as 1920 × 1080, 30 FPS, with Kokoro `af_heart` and
Manim Voiceover. Runtime metadata and intermediate renders are excluded from Git.

The scientific narration and Manim diagrams are original project work. OpenMoji
illustrations are credited in the end cards and main README under CC BY-SA 4.0.
Keep the applicable attribution and share-alike obligations when redistributing.

Verify the included copies from the repository root without inspecting media streams:

```powershell
Get-FileHash examples\ph-scale-v06.mp4 -Algorithm SHA256
Get-FileHash examples\covalent-bonds-v05.mp4 -Algorithm SHA256
Get-FileHash examples\ionic-vs-covalent-v05.mp4 -Algorithm SHA256
```

Compare these hashes with `manifest.json`.
