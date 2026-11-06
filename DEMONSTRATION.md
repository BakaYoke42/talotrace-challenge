# Final demonstration and explanation

This guide walks a reviewer through the complete backend workflow. Use the same
full-screen and face recording required by the challenge, and finish it with the three
concepts. The agent can execute process checks; only the candidate watches and listens
to the videos and records the audiovisual assessment.

## Run the demonstration

1. Follow `README.md`, including caching Kokoro assets, and run the server with one worker.
2. Open `/docs` and show the four routes. Explain that question matching is exact.
3. In a second terminal, run:

   ```powershell
   .\.venv\Scripts\python.exe -m scripts.demo_api --base-url http://127.0.0.1:8000
   ```

4. Show the three HTTP 202 responses, the list endpoint and the live job states. One job
   processes while later jobs wait. A request for an unpublished file returns 409.
5. When each job completes, show its artifact URL and HTTP 200 download. The script saves
   numbered review copies and `artifacts/final-demo-report.json`. These are fresh renders;
   the tracked example videos are not consulted by the worker.
6. Personally open each MP4. Explain hydronium/activity and the logarithmic pH scale;
   electron sharing and the lower-energy H2 state; and ionic attraction in a NaCl crystal
   compared with polar covalent O–H bonds. The lemon symbols are only a visual metaphor.
7. Show `knowledge/`, `ARCHITECTURE.md`, `tests_covered` and the passing test command. State
   the single-process, timeout-cleanup and audiovisual-review limitations accurately.

The committed `examples/demo-report.json` contains the actual final HTTP run results.
The subsequent single-question walkthrough is recorded in
`examples/ph-walkthrough-report.json`; its pH v06 is now the selected pH example.
The test inventory distinguishes simulated failure cases from real media generation.

## What is included

- `README.md`: setup, server, API examples, tests, sources and limits.
- `ARCHITECTURE.md`: explanation of the request, state, worker, rendering and storage boundaries.
- `RELIABILITY.md` and `tests_covered`: known limits and the specific checks performed.
- `examples/`: the latest three numbered MP4s, questions, job IDs, hashes and final run report.
- `IMPLEMENTATION_PLAN_v0.9.md` and `rules/`: the original plan and challenge requirements.

Virtual environments, model weights, SQLite files, logs, intermediate media and older
video iterations remain local and ignored. The history is retained on GitHub; the final
branch must be merged into the repository's default branch when the candidate is ready.

## Submission remains the candidate's action

Reply to the invitation email with exactly the two required links: the private GitHub
repository and the single Google Drive recording. The challenge asks for repository
access for `praveen.k@growtrics.ai` and `wayne.le@growtrics.ai`, and Viewer access to the
recording for `hr-submissions@talotrace.ai`. Verify those shares before sending.
Publishing a branch does not grant those people access, create the recording, validate
the videos, or send the submission email; no such actions are claimed by this repository.
