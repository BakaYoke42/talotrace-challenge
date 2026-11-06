# Reliability and security notes

- Run one API process and one worker. Multiple server processes or application instances
  sharing the same database are not supported; startup recovery would mark another
  process's active jobs as failed.
- SQLite holds queued jobs and statuses. On restart, queued jobs are resumed in FIFO
  order and interrupted processing jobs become failed; they are not silently retried.
- Jobs use UUIDs, distinct directories, and a fresh directory must be created for each
  render. A nonempty output is published only after Manim exits successfully. The file
  endpoint never accepts client-supplied paths and rejects resolved paths outside the
  expected artifact location. Missing artifacts return 404.
- Render failures and timeouts are recorded with safe messages. Detailed logs are local
  to each job. No automatic retry is attempted for deterministic scene failures.
- The subprocess timeout terminates the direct Manim process. On Windows, a child such
  as the separate Kokoro process may outlive it; cleanup of the entire process tree is
  not yet guaranteed. A stalled executor can also delay a graceful server shutdown.
- Process exit and nonempty-file checks do not establish whether audio is audible,
  synchronized, or educationally clear. The human reviews audiovisual results.
- There is no authentication, user isolation, rate limiting or multi-host deployment
  support. This is a local single-user prototype, not an internet-facing service.
