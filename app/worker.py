import logging
from threading import Event, Thread

logger = logging.getLogger(__name__)


def simulated_executor(job: dict):
    """Lifecycle test double: completes without creating or claiming a video."""
    logger.info("Simulating generation for job %s; no video is produced", job["job_id"])


class Worker:
    def __init__(self, store, executor):
        self.store = store
        self.executor = executor
        self.stopping = Event()
        self.changed = Event()
        self.thread = None

    def start(self):
        self.stopping.clear()
        self.thread = Thread(target=self.run, name="video-worker", daemon=True)
        self.thread.start()

    def wake(self):
        self.changed.set()

    def stop(self):
        self.stopping.set()
        self.changed.set()
        if self.thread:
            self.thread.join()

    def run(self):
        while not self.stopping.is_set():
            self.changed.clear()
            job = self.store.claim_next()
            if job is None:
                self.changed.wait(timeout=1)
                continue
            try:
                artifact_available = self.executor(job)
            except Exception:
                logger.exception("Job %s failed", job["job_id"])
                self.store.finish(job["job_id"], "Job execution failed")
            else:
                url = f"/videos/{job['job_id']}/file" if artifact_available else None
                self.store.finish(job["job_id"], artifact_url=url)
