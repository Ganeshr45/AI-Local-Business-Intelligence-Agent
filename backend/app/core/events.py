import threading

_lock = threading.Lock()
_events_by_run = {}
_done_runs = set()


def init_run(run_id: str):
    with _lock:
        _events_by_run[run_id] = []
        _done_runs.discard(run_id)


def push_event(run_id: str, event: dict):
    with _lock:
        _events_by_run.setdefault(run_id, []).append(event)


def mark_done(run_id: str):
    with _lock:
        _done_runs.add(run_id)


def is_done(run_id: str) -> bool:
    with _lock:
        return run_id in _done_runs


def get_events_since(run_id: str, offset: int):
    with _lock:
        events = _events_by_run.get(run_id, [])
        return events[offset:], len(events)
