# TaloTrace — AI Chemistry Video Request Service
## IMPLEMENTATION_PLAN.md — v0.9 (clean-start, API-first, approval-gated)

**Date:** 2026-11-06  
**Status:** Pre-exam design and research only; **the application code must be implemented in the recorded session**.  
**Working language:** English for code, API, documentation, narration, and on-screen video text.

> **Critical reset from v0.6, extended in v0.9:** This version deliberately starts with a **clean application workspace**. The coding agent MUST NOT assume that existing Manim scene code, a Kokoro adapter, cached audio, existing MP4s, or a FastAPI implementation is present. Create the implementation live, with the mandatory agentic coding tool, while the screen and face are recorded. Previous experiments informed the decisions below; do not claim that they were developed during the recording. If any pre-existing code or assets are reused, disclose that fact openly.

## 1. Challenge objective and rules

Build a **backend-only FastAPI** prototype that accepts one of the exact three chemistry questions, starts an **asynchronous** video-generation job, exposes job status and a job list, and serves the resulting educational MP4 with visual content and narration.

Exact required learner questions:

1. `How does the pH scale work?`
2. `Why do atoms form covalent bonds?`
3. `What is the difference between ionic and covalent bonding?`

No frontend. Do not claim to support arbitrary chemistry/STEM questions. Design a clear extension point for new scene templates. Real generated video with visual + audio is the goal; partly simulated components are allowed by the challenge when identified transparently. **A prerecorded MP4 lookup is not a substitute for a generation job.**

**Mandatory process:** Work with Codex, Claude Code, Cursor Agent or another genuine *agentic coding harness*. Record your full screen **and face** throughout the session. Preserve the genuine coding, debugging, testing, and decisions on video. End the **same recording** with a walkthrough of the three concepts. Suggested session: **90–120 minutes**; completion is not the sole criterion.

## 2. Starting workspace — deliberately clean

At the beginning of the recorded implementation, keep the **clean application workspace**: `IMPLEMENTATION_PLAN.md` and, if prepared, `requirements.txt`, `.gitignore`, and the working `.venv/` / `.venv-tts/` environments. These are environment/configuration preparation, **not previously completed application code**. The application, API, scene implementations, and JSON scenarios are created during the recorded session. This is a deliberate personal choice, **not a formal TaloTrace prohibition on pre-existing code**.

- Do **not** copy in `ph_scale_v3_voiceover.py`, `covalent_bonds_v1_voiceover.py`, `ionic_vs_covalent_v1_voiceover.py`, the former TTS adapter, `audio/` outputs, or prerendered videos.
- Keep older prototypes in a **separate backup directory outside the exam workspace**. Do not delete them. They are prior experiments, not deliverables falsely portrayed as newly written code.
- Previously installed Python packages, Manim, FFmpeg, TTS model downloads, GPU drivers and a coding-agent extension are environment preparation, not newly written application source. Test they are usable; avoid spending the session reinstalling everything needlessly.
- If SVGs are not already in the clean workspace, the agent can obtain the three licensed OpenMoji files **during the recording**, document attribution, and store them in `images_pour_videos/`.
- Initialize or verify Git at the beginning of the recorded session. Make sensible incremental commits and preserve history. Never commit secrets, personal files, virtual environments, models, or temporary renders.

## 3. Fixed technical decisions

| Concern | Decision |
|---|---|
| Backend | FastAPI + Pydantic; no frontend |
| Metadata | SQLite, one small repository/helper module |
| Background work | A **single local FIFO worker**; run Manim via subprocess outside the request handler |
| Artifact storage | Job-specific directories on local disk |
| Scientific animation | **Manim Community Edition** |
| Narration | **Kokoro-82M** locally, voice **`af_heart`**, English |
| Sync | **Manim Voiceover**, scene-level timing driven by the actual narration |
| Images | OpenMoji SVGs stored in **`images_pour_videos/`** at the project root |
| Audio/video generation | Generate a **new actual Manim render for each job**; reusable audio cache is acceptable if transparent |
| LLM inside runtime | **None** for MVP; deterministic, pre-specified scenarios for three supported questions |
| Scenario source | **Three versioned JSON files** in `knowledge/`; narration and scene order belong in data, while drawing logic remains in Python |
| Scenario validation | One small Pydantic schema and a **simple explicit topic-to-scene mapping**; reject invalid or unknown scenario entries |
| Optional AI providers | Mistral, generative images, multi-agent pipeline: **skip** unless essentials are complete |
| Reliability | Tests, errors, bounded retries where justified, timeout, safe output publication, repeated-job verification |

**Simplicity is mandatory:** Write the **simplest human-readable, human-debuggable code that works**. Prefer short named functions, explicit branches, limited dependencies and small interfaces. Avoid elaborate design patterns, reflection-based registries, unnecessary async frameworks, and complexity that exists only to look impressive. A small explicit mapping for the three concepts is encouraged.

**Code must be written during the recording.** This plan fixes the *requirements and storyboards*, not finished implementation code. The coding agent chooses straightforward Manim instructions and FastAPI code, which the candidate inspects and corrects.

## 3A. Mandatory step-by-step development and approval gate

**HIGHEST-PRIORITY WORKFLOW RULE FOR THE CODING AGENT:** Work **one major phase at a time** according to **Section 9 (API-first execution order)**. Do not execute the entire plan in a single unattended run.

For **every phase**, the agent MUST:

1. Announce **which phase is starting**, its goal, and a concise list of intended code changes. Stay within that phase's scope.
2. Implement and run the **code, API, security, or process tests appropriate to that phase**, fixing ordinary errors within the same phase. Do not over-engineer or spend time on optional polish.
3. Report, briefly and concretely: **files created/changed**, **tests actually run and their results**, **what works**, **known limitations or blockers**, and **the next proposed phase**. Never claim tests or validation that were not performed.
4. **STOP AND WAIT FOR THE CANDIDATE'S EXPLICIT APPROVAL** (e.g. "Proceed to Phase 2") before starting the next phase. Silence, lack of objection, or a general initial approval to the plan does **not** authorize subsequent phases.
5. If a phase produces a video, provide its exact file path and technical process status, then **stop for the candidate's own visual and audio review**. Do not begin artistic changes or the next phase until authorized.

**Approval is required at every major phase boundary, not after every code line, file edit, or command.** If an implementation choice significantly changes architecture, dependencies, scope, or the scientifically approved scenario, explain it and request approval **before** making that change. Normal code-debugging fixes and software tests within the current approved phase do not need individual approval.

**The first implementation deliverable is the FastAPI API contract, not a standalone Manim animation.** A lightweight test double for generation is permitted *only to test the API and job lifecycle*, must be clearly labeled as a stub, must never be presented as a completed chemistry video, and must be replaced by genuine Manim/Kokoro generation in a later phase. The API should be designed so that this replacement is straightforward.

## 4. Division of validation responsibilities

### Agent MUST run automated software/security tests

- Python import/syntax sanity; meaningful tests for API contract and status transitions.
- Unsupported question, unknown job, incomplete job artifact requests, path traversal defenses, error handling, queue isolation, file output paths, subprocess failures and timeouts.
- Repeated requests for the same topic and multiple sequential queued jobs; verify that they produce separate artifacts.
- Basic render-process checks: successful process exit, output file exists and is non-empty.
- Explain failures and retry/recovery logic; do not claim success from a traceback or an empty file.

### Human exclusively reviews audiovisual quality

The agent **MUST NOT** inspect extracted video frames, screenshots, contact sheets, spectrograms, waveforms, transcriptions, media-stream/duration probes (`ffprobe`), or run models to score image/audio quality. Do not iterate on subjective graphics or voice without human feedback. After an output is generated, provide its path and code/process test results; **stop for the candidate to watch, listen, and request changes**. The candidate reviews scientific communication, visual quality, intelligibility, timing, and unwanted clipping.

**Known engineering trade-off:** This excludes some automated media-integrity checks. Be candid that process/file checks alone do **not** prove audio is audible, synchronized or scientifically clear. If the assessment reveals a need for stronger artifact quality gates, explicitly discuss the trade-off; do not falsely assert media validation was performed.

## 5. Four endpoint contracts

| Method | Route | Expected behavior |
|---|---|---|
| `POST` | `/videos` | Body `{"question":"..."}`; recognize one exact question; create a job; respond `202` with `job_id`, `status="queued"`, concept |
| `GET` | `/videos` | List all known jobs (newest first is fine) |
| `GET` | `/videos/{job_id}` | Job status, stage, optional safe error, artifact URL when complete |
| `GET` | `/videos/{job_id}/file` | `FileResponse` with MP4 only when completed; otherwise clear error |

Job states: `queued -> processing -> completed` or `queued/processing -> failed`. Optional stages: `preparing`, `audio`, `rendering`, `publishing`.

Error conventions: unsupported question `422`; unknown job `404`; output requested before completion `409` (or clearly documented equivalent). Pydantic input schema, UUID job IDs, no arbitrary filesystem paths accepted from clients.

API must return immediately after queuing; **do not execute blocking Manim within an HTTP request handler**. For the recorded prototype, run exactly one worker; a thread supervising subprocess calls is sufficient if lifecycle is simple. Local single-process design and recovery limitations must be documented honestly.

## 6. Genuine per-job generation flow

1. API accepts exactly one supported question and stores a `queued` job in SQLite.
2. A single worker takes the next pending job, sets `processing`, and maps the question to one validated JSON scenario and its corresponding Manim scene/template.
3. Worker invokes Manim through a subprocess, targeting a unique per-job render directory. Scenes use Manim Voiceover and Kokoro `af_heart` (or an explicitly explained compatible cached speech result).
4. Handle subprocess exit status, timeout, logs, and presence/nonzero size of output.
5. Publish the MP4 to a stable per-job artifact path **only after successful process checks**, using a temporary path then rename where practical. Set `completed`; on failure, store a safe, understandable `failed` error.
6. Job status and artifact remain queryable from the API.

**Retries:** Only retry bounded transient errors that plausibly recover. Never recursively retry a deterministic broken scene. Worker crashes or restarts must not leave jobs indefinitely in `processing`: implement the simplest explicit startup recovery policy, or document and test a small limitation if time constrained.

A cached narration file may save time, but **do not return previously exported MP4s** in place of a real render. No runtime LLM re-authoring of scientific scripts: the versioned JSON scenarios, derived from the scientifically reviewed outlines below, are authoritative for narration and scene order. Python only implements how those scenes are drawn.

## 7. Frozen educational scenarios — data and code to be written live

**Chosen architecture: separate educational content from rendering code.** During the recorded session, author the three small JSON storyboards in `knowledge/` using the fixed, scientifically reviewed requirements below. The JSON files are the **single source of truth** for each topic's exact question, ordered segments and narration. Manim Python code handles visual behavior; it must not independently duplicate or reinvent narration text.

Example *illustrative schema* (not a prebuilt exam artifact):

```json
{
  "schema_version": 1,
  "concept_id": "covalent",
  "question": "Why do atoms form covalent bonds?",
  "scene_type": "covalent",
  "segments": [
    {
      "id": "intro",
      "visual": "two_hydrogen_atoms",
      "narration": "Two hydrogen atoms can form a covalent bond."
    },
    {
      "id": "energy",
      "visual": "bond_energy_curve",
      "narration": "At the right distance, the bonded state can have lower energy."
    }
  ]
}
```

This is only a **format example**: write the complete, verified content during the challenge, consistent with the five-step outlines below. Keep fields minimal (`schema_version`, `concept_id`, `question`, `scene_type`, ordered `segments` with `id`, `visual`, `narration`); add optional asset/parameter fields only if the real implementation needs them. Do not store executable Python, arbitrary class paths or unrestricted expressions in JSON.

**Minimal implementation contract:**

1. `knowledge/ph_scale.json`, `knowledge/covalent.json`, and `knowledge/ionic_vs_covalent.json` contain the approved narration and ordered visual segments.
2. A small Pydantic model validates nonempty text, supported identifiers, required scene sequence and usable asset paths before a job renders; fail clearly on invalid configurations.
3. A simple explicit dictionary maps the three exact user questions to `{scenario_file, scene_class}`; no dynamic imports or general-purpose workflow engine.
4. The Manim scene reads the validated scenario; its named animation functions draw the `visual` types and use each segment's `narration` with Kokoro `af_heart` and Manim Voiceover. Unsupported visual types fail explicitly rather than rendering unrelated content.
5. Re-running the same scenario should produce consistent educational content; media timing and bytes need not be bit-for-bit identical. Record the scenario version with the job when practical.
6. Adding a future STEM topic involves creating a **reviewed JSON file** and registering the question. Reuse existing drawing components where possible; introduce a new Manim component or scene class when the new science requires it. **JSON makes content extensible, not visual generation universally automatic.**
7. Tests verify that all three JSON files load, validate, select the right question/scene, and reject invalid or unknown `visual` identifiers. These are source/code tests, **not audiovisual inspections**.

**Timebox fallback:** If the above separation becomes a blocker to delivering a real working vertical slice, prioritize working generation but document any inline hardcoded content as a temporary compromise and avoid falsely claiming JSON-driven generation. Do not build a generic JSON-to-animation interpreter.


These are requirements for newly authored Manim scenes, **not existing scene implementations**. The agent writes new Python code during the recording. Prioritize a compact, readable video over cinematic complexity; aim for approximately **20–40 seconds per topic** if necessary to stay within the exercise time. Use 16:9, 30 FPS, a consistent dark theme, readable labels and transitions.

### A. `How does the pH scale work?`

1. Introduce pH and an aqueous solution containing hydronium ions.
2. Show the familiar pH scale, with acidic / approximately neutral / basic regions and a few examples.
3. Explain that pH is logarithmic: a difference of one pH unit corresponds to **10×** hydrogen ion activity.
4. Use a visually clear 1-vs-10 comparison. If lemon icons are used, explicitly label them a **metaphor**; ten lemons do *not* guarantee a one-unit pH change. Link the factor-ten claim to ion activity, not number of lemons.
5. Concise recap.

Asset: **`images_pour_videos/lemon.svg`** (OpenMoji `1F34B.svg`).

Scientific caveats: pH strictly relates to hydrogen ion *activity*, approximately hydronium concentration in dilute solutions; neutral water is approximately pH 7 **at 25°C**; 0–14 is a common classroom range, not universal.

### B. `Why do atoms form covalent bonds?`

1. Introduce two separate hydrogen atoms.
2. Show overlap/shared electron density in a simplified pedagogical model.
3. Explain that attraction and repulsion can yield a **lower-energy bonded state** at an equilibrium separation; show a qualitative potential-energy minimum if feasible.
4. Show H₂ with a shared electron pair.
5. Recap: shared electron density and energetically favorable bonding.

No external SVGs for atoms: create nuclei, electron-density illustration and bonds with Manim. Do not imply that electrons orbit like little planets or that atoms consciously “want” octets.

### C. `What is the difference between ionic and covalent bonding?`

1. Introduce sodium chloride (NaCl) vs water (H₂O), using salt and water images as familiar examples.
2. Ionic model: simplified transfer of an electron from sodium to chlorine, creation of Na⁺ and Cl⁻, electrostatic attraction and a small lattice depiction (solid NaCl is not discrete NaCl molecules).
3. Covalent model: shared electrons in the O–H bonds of H₂O; note that the sharing is unequal and the bonds are polar covalent.
4. Quick side-by-side comparison of oppositely charged ions vs shared electrons.
5. Concise takeaway.

Assets: **`images_pour_videos/salt.svg`** (OpenMoji `1F9C2.svg`), **`images_pour_videos/water.svg`** (OpenMoji `1F4A7.svg`). Scientific diagrams are generated with Manim, not the emojis.

### Asset policy

Use project-root-relative `pathlib` paths, do not silently rename `images_pour_videos/`. If SVGs are not present, download and save them under the names above, or make an explicit, documented fallback graphic in Manim rather than crashing unexpectedly. OpenMoji license: **CC BY-SA 4.0**; include attribution and links in the README, and respect distribution requirements.

## 8. Scientific references (consult and cite in README)

**Primary textbook:** OpenStax, *Chemistry 2e* (Rice University / OpenStax), using relevant sections:

- pH / pOH: https://openstax.org/books/chemistry-2e/pages/14-2-ph-and-poh
- Covalent bonding: https://openstax.org/books/chemistry-2e/pages/7-2-covalent-bonding
- Ionic bonding: https://openstax.org/books/chemistry-2e/pages/7-1-ionic-bonding

**Technical definition of pH:** IUPAC Gold Book: https://goldbook.iupac.org/terms/view/P04524

These are scientific background references, not permission to copy textbook figures or copyrighted text. Research and check the written narration and scientific depiction at the code/script level. **Do not inspect the generated audiovisual artifact; leave that to the human.** If a reference cannot be accessed, say so instead of claiming it was checked.

## 9. API-first, step-by-step execution plan (approval required after **every** phase)

**BEFORE PHASE 1:** Start recording the full screen and face. Open this plan in the agentic IDE. The candidate authorizes **Phase 1 only** with the opening prompt. All later phases require separate explicit approval.

### Phase 1 — Inventory and minimal FastAPI API contract (first real coding task)

- Confirm working Python environment, FastAPI/Pydantic availability and version, and the basic Manim/FFmpeg/TTS installation state; do not reinstall working dependencies needlessly.
- Initialize/verify Git and the clean project structure. Do not copy prior application source into this workspace.
- Implement the four endpoint **routes**, Pydantic models and clear HTTP error handling: `POST /videos` (`202`), `GET /videos`, `GET /videos/{job_id}`, `GET /videos/{job_id}/file` (not-ready response).
- Use the **three exact allowed questions** in a simple explicit mapping. Use an in-memory job store **temporarily**, if needed, to verify the HTTP interface before persistence. `POST` can initially create a `queued` job; **do not claim a renderer is running yet**.
- Write and run small API tests: accepted/unsupported questions, list/detail, invalid IDs, and not-ready file route. Confirm `/docs` loads if feasible.
- **Checkpoint:** Summarize endpoints, changed files, tests and remaining gaps. **STOP. Await explicit authorization for Phase 2.**

### Phase 2 — SQLite job state and one asynchronous worker (still no real media required)

- Replace temporary state with straightforward **SQLite** persistence. Implement the documented `queued -> processing -> completed/failed` states.
- Add a **single** FIFO worker that runs outside the request handler. Use a **clearly marked small test-double job executor** only to verify queuing, concurrency, lifecycle, failure states and immediate HTTP `202`. A mock may complete a job without an MP4 but **must not publish a fake video or claim media generation succeeded**; protect the file route accordingly.
- Test API responsiveness while a slow test job runs, sequential execution of two jobs, bad input, injected failure, and recovery policy (or document a narrow restart limitation).
- Prefer few modules and explicit functions. Do not introduce Celery, Redis or multiple worker processes.
- **Checkpoint:** Report actual lifecycle tests, what remains mocked and architecture choices. **STOP. Await explicit authorization for Phase 3.**

### Phase 3 — Real minimal audiovisual rendering through the API

- Verify Manim Community Edition, Kokoro-82M voice `af_heart`, Manim Voiceover and FFmpeg can work together using the installed environments.
- Build the **smallest real scene** with a short English narration, launch it from the **existing worker** using a subprocess, and store its MP4 in a job-specific directory. **Do not bypass the API with a separate standalone demo as the main deliverable.**
- Remove the test executor from the normal generation path; keep injected test doubles in tests only.
- Check subprocess exit code, timeout, missing/empty files and safe publication. Never return a cached prerecorded MP4 as a newly rendered job.
- No agent inspection of video frames, audio, duration probes, spectrograms or waveforms. The candidate personally watches and listens to the MP4.
- **Checkpoint:** Provide exact MP4 path, actual API/job behavior, and code/process tests. **STOP for human audiovisual approval and authorization for Phase 4.**

### Phase 4 — First complete science topic: pH and its validated JSON scenario

- Author `knowledge/ph_scale.json` from the **frozen pH outline** in Section 7 and the scientific references in Section 8, including original English narration and permitted visual IDs.
- Implement the minimal **Pydantic scenario validation** and connect validated JSON segments to the Manim renderer. Reuse the already working API/worker/audio path rather than rewriting it.
- Build the real pH explanation with Manim and `images_pour_videos/lemon.svg` if available. Obtain and attribute OpenMoji assets when needed; use the documented fallback if downloading blocks progress.
- Test scenario loading, wrong visual IDs, topic selection, API job creation and process success. Candidate reviews audiovisual output.
- **Checkpoint:** Report tests, code and rendered file. **STOP for human audiovisual approval and authorization for Phase 5.**

### Phase 5 — Remaining two JSON scenarios and videos

- Create `knowledge/covalent.json` and `knowledge/ionic_vs_covalent.json`, using the frozen five-step outlines, source references and original English narration.
- Add their Manim renderers, using existing simple components where genuinely useful. The covalent video draws atomic/molecular visuals in Manim; the ionic comparison uses `images_pour_videos/salt.svg` and `images_pour_videos/water.svg` as illustrative accents.
- Route the **same four endpoints and same worker** to all three concepts; ensure concept-specific output paths and no accidental cross-topic substitutions.
- Run software/process tests and produce both MP4s. Human reviews the audiovisual outputs.
- **Checkpoint:** Report the three supported query mappings, tests and paths to the two new MP4s. **STOP for human audiovisual approval and authorization for Phase 6.**

### Phase 6 — Reliability, security and repeated-run testing

- Agent tests multiple separate jobs for the same question, several queued questions, error states, subprocess timeout/failure, unsupported questions, unknown IDs, path safety and job-file isolation.
- Keep **automated checks focused on code, API and process/file existence**, respecting Section 4's exclusion of audiovisual analysis by the agent.
- Fix meaningful defects without unnecessary refactoring or optional features. Record known limitations accurately; do not falsely report full media validation.
- **Checkpoint:** State tests actually run, their outcomes, relevant fixes, remaining risks and limitations. **STOP. Await explicit authorization for Phase 7.**

### Phase 7 — Documentation, example artifacts and final walkthrough

- Write `README.md`: setup/run commands, endpoints, tests, voice/assets, scientific references, known limitations. Add `ARCHITECTURE.md` covering job lifecycle, SQLite, subprocess worker, JSON/storyboard boundary and artifact storage.
- Make sensible Git commits with real history; ensure the three best MP4 examples and their questions are included in the private repository. Keep virtual environments, model weights, intermediate renders and secrets untracked.
- Explain how to share the private repository and recording under the exact challenge submission requirements in Section 11.
- **Finish the same recording** with a walkthrough of all **three** concepts and show API usage; do not claim missing stages were completed.
- **Checkpoint:** Summarize submission readiness. **STOP and let the candidate review before submitting.**

**Timebox rule:** The suggested duration is approximately 90–120 minutes. Prefer a working, honest vertical slice to unsupported claims of completeness. If time is running short, the agent should tell the candidate which phase is complete and recommend a narrower path; it must **still request approval** before changing the plan or skipping a phase. Prior experiments and this plan may inform the build, but must never be portrayed as newly developed code.

## 10. Initial project shape (created live, not supplied in advance)

```text
TaloTrace_Recrutment/
├── IMPLEMENTATION_PLAN.md      # Main plan; optional preexisting requirements/.gitignore/.venvs
├── README.md                   # Created during recording
├── ARCHITECTURE.md             # Created during recording
├── .gitignore                  # Created during recording
├── requirements.txt            # Created during recording
├── app/
│   ├── main.py                 # FastAPI endpoints
│   ├── jobs.py                 # SQLite state
│   ├── worker.py               # Sequential subprocess runner
│   └── generator.py            # Manim invocation and explicit topic mapping
├── knowledge/                  # Validated, versioned educational content
│   ├── ph_scale.json
│   ├── covalent.json
│   └── ionic_vs_covalent.json
├── scenes/
│   ├── ph_scale.py
│   ├── covalent.py
│   └── ionic_vs_covalent.py
├── images_pour_videos/
│   ├── lemon.svg
│   ├── salt.svg
│   └── water.svg
├── artifacts/                  # Per-job generated media; not all intermediates in Git
└── tests/
```

This is a **suggested** layout, not an instruction to create unnecessary abstractions. Collapse modules when clearer; name files according to actual code. Keep secrets in environment variables and `.env` files excluded from Git.

## 11. Submission checklist

Send **exactly two links** in reply to the invitation email:

1. **Private GitHub repository**, preserving the real commit history; share with `praveen.k@growtrics.ai` and `wayne.le@growtrics.ai`. Include FastAPI code, README setup/run/API/tests instructions, short architecture note, and the **three best generated videos with the originating learner question**. Exclude dependencies, generated cache/build output and secrets.
2. **Google Drive full-screen + face recording**, shared with `hr-submissions@talotrace.ai` as **Viewer**; final walkthrough of all three chemistry concepts must be in this same recording.

**Core framing for the reviewer:** JSON storyboards hold reviewed, stable science and narration; Python Manim functions supply the actual visuals. This provides a clear extension point without pretending to handle arbitrary topics automatically. Existing research and prior small prototypes led to the decisions and this written plan. **The submitted application, scene code and agent-supervised integration are developed live in the recorded session** if the clean-start strategy is followed. Be truthful about any exceptions.
