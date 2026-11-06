# Chemistry Video Request Service

A backend-only FastAPI prototype that turns three exact chemistry questions into newly
rendered, narrated MP4 videos. Requests return HTTP 202 while a single FIFO worker runs
Manim Community Edition, Kokoro-82M (`af_heart`, English), and Manim Voiceover locally.
There is no runtime LLM, frontend, cloud rendering service, or prerecorded-video lookup.

## Scope and examples

| Exact learner question | Concept | Latest included example |
| --- | --- | --- |
| How does the pH scale work? | `ph_scale` | [ph-scale-v06.mp4](examples/ph-scale-v06.mp4) |
| Why do atoms form covalent bonds? | `covalent` | [covalent-bonds-v05.mp4](examples/covalent-bonds-v05.mp4) |
| What is the difference between ionic and covalent bonding? | `ionic_vs_covalent` | [ionic-vs-covalent-v05.mp4](examples/ionic-vs-covalent-v05.mp4) |

The examples come from the same API pipeline. They are review artifacts, not inputs to
new jobs. See [examples/README.md](examples/README.md) for provenance and verification.

## Install on Windows

The tested platform is Windows with Python 3.12.13. Use PowerShell from the repository
root. The commands below create two environments; the worker expects the narration
interpreter at `.venv-tts/Scripts/python.exe`. Other operating systems need that path
adapted. Segoe UI is the display font used on the tested Windows installation.

```powershell
git clone --branch feature/phase6-reliability https://github.com/BakaYoke42/talotrace-challenge.git
cd talotrace-challenge
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
py -3.12 -m venv .venv-tts
.\.venv-tts\Scripts\python.exe -m pip install --upgrade pip
.\.venv-tts\Scripts\python.exe -m pip install -r requirements-tts.txt
.\.venv-tts\Scripts\python.exe -m scripts.prepare_tts
```

If Python is managed by `uv` rather than the Windows `py` launcher, create each
environment with `uv venv --python 3.12 --seed .venv` and
`uv venv --python 3.12 --seed .venv-tts`, then use the same interpreter commands above.

Installation needs internet access. The last command caches Kokoro's configuration,
weights, and `af_heart` voice from `hexgrad/Kokoro-82M`. The TTS requirements also install
the English spaCy language model used by Misaki. Do this before rendering: the worker
sets Hugging Face offline mode. Model weights stay outside Git in the user's cache.

Check an existing installation without downloading:

```powershell
.\.venv-tts\Scripts\python.exe -m scripts.prepare_tts --check
.\.venv\Scripts\python.exe -c "import manim, manim_voiceover, imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
```

FFmpeg is supplied by `imageio-ffmpeg`; a separate executable on PATH is unnecessary for
this pipeline. The diagrams use text and vector shapes, so no LaTeX installation is
required. An optional SoX warning can appear when importing Voiceover; the current path
does not use recording or speed adjustment. A GPU is not required.

The final delivery is on `feature/phase6-reliability` until that branch is merged into
`main`; the clone command explicitly selects it.

The direct dependency versions reflect the working environments. The full workflow has
been exercised there; a fresh installation on another machine has not been verified.
Hugging Face assets are fetched from the model's current `main` revision during setup,
so this is not a byte-for-byte reproducibility guarantee.

## Start the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. Keep exactly one server process; avoid
reload mode while rendering. Start from the project root so the default database
`jobs.sqlite3` and `artifacts/` directory are created in the expected place.

## API

| Method | Route | Result |
| --- | --- | --- |
| POST | `/videos` | Queue an exact supported question; HTTP 202 with job metadata |
| GET | `/videos` | List persisted jobs, newest first |
| GET | `/videos/{job_id}` | Status, stage, safe error, and artifact URL if published |
| GET | `/videos/{job_id}/file` | Download the completed MP4 |

```powershell
$body = @{ question = 'How does the pH scale work?' } | ConvertTo-Json
$job = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/videos -ContentType 'application/json' -Body $body
$job
Invoke-RestMethod http://127.0.0.1:8000/videos
Invoke-RestMethod "http://127.0.0.1:8000/videos/$($job.job_id)"
# After status becomes completed:
Invoke-WebRequest "http://127.0.0.1:8000/videos/$($job.job_id)/file" -OutFile ph-scale.mp4
```

POST returns a snapshot with `status: "queued"`. Subsequent reads show `processing`,
then `completed` or `failed`; real publication uses `stage: "published"`. The renderer
can take minutes, especially on the first run. Repeating the same question creates a
different job and a fresh render, not a reused MP4.

Unsupported questions, invalid bodies and malformed UUIDs return 422. Unknown jobs and
missing completed artifacts return 404. File requests before publication return 409.
Question matching is exact and case sensitive. The API has no authentication or user
ownership model; use it as a local single-user prototype.

## Tests and complete demonstration

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache\test-run
```

The suite currently contains 32 cases. Tests use temporary SQLite databases and test
doubles for rendering. They cover API errors, FIFO execution, repeated requests, isolated
files, failure/timeout handling, restart recovery, validated storyboards, and construction
of every sentence-level animation. See [tests_covered](tests_covered) for the inventory.

With the server running, use a second PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m scripts.demo_api --base-url http://127.0.0.1:8000
```

This uses real HTTP, queues all three questions, lists and polls jobs, checks unavailable
file responses, downloads each fresh MP4, and saves numbered review copies plus
`artifacts/final-demo-report.json`. It can take several minutes. See
[DEMONSTRATION.md](DEMONSTRATION.md) for the recorded walkthrough.

Alternatively, stop the HTTP server before running the in-process render helper:

```powershell
.\.venv\Scripts\python.exe -m scripts.render_review
# Or one topic:
.\.venv\Scripts\python.exe -m scripts.render_review --concept covalent
```

Do not run these helpers alongside a server using the same database: they start another
application instance, and startup recovery assumes exclusive ownership of the database.

## Design and limits

Reviewed JSON storyboards hold narration and scene order. Explicit Python handlers draw
the science; adding arbitrary text does not create a new scientific animation. Each
sentence has a newly synthesized WAV, and its actual duration drives Voiceover timing.
The output configuration is 16:9, 1920 × 1080, 30 FPS. Read
[ARCHITECTURE.md](ARCHITECTURE.md) for the implementation boundaries and extension steps.

The worker has a 600-second render timeout and publishes only after a successful process
exit and a nonempty output. It does not retry deterministic failures. Queued jobs survive
restart; interrupted processing jobs become failed. On Windows, a child Kokoro process
may survive termination of the direct Manim process after a timeout. Graceful shutdown
waits for active execution. Multiple processes, resource quotas, distributed workers and
production monitoring are not implemented. More detail: [RELIABILITY.md](RELIABILITY.md).

Automated checks do not establish audiovisual quality, synchronization or scientific
clarity. The candidate personally reviews videos; the agent does not inspect frames,
listen to audio, probe media streams or run quality-scoring models.

## Sources, assets and provenance

The scientific narration is original, with reference to OpenStax *Chemistry 2e*:
[pH and pOH](https://openstax.org/books/chemistry-2e/pages/14-2-ph-and-poh),
[covalent bonding](https://openstax.org/books/chemistry-2e/pages/7-2-covalent-bonding), and
[ionic bonding](https://openstax.org/books/chemistry-2e/pages/7-1-ionic-bonding).
The activity-based pH definition follows [IUPAC Gold Book P04524](https://goldbook.iupac.org/terms/view/P04524).
The IUPAC page returned 403 during verification; its indexed definition was consulted.
See [knowledge/README.md](knowledge/README.md) for the teaching simplifications.

Lemon (`1F34B`), salt (`1F9C2`) and water drop (`1F4A7`) illustrations are by
[OpenMoji](https://openmoji.org/), licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Their provided filenames
are retained in `images_pour_videos/`. Figures depicting ions, atoms and bonds are drawn
with Manim. Credit appears in the rendered end card; preserve the applicable attribution
and share-alike terms when redistributing these assets or adaptations. Kokoro model
weights are not distributed here; consult its model card and license before redistribution.

The initial environment and implementation plan existed before application development.
The application, scenarios and integration were developed with Codex in this workspace.
SVG illustrations were supplied in the workspace and reused. Git history is preserved;
local environments, model weights, databases, intermediate renders and older review
videos are excluded. Only the three selected latest example MP4s are tracked.
