# delta_storage_wrapper.py
from __future__ import annotations
from typing import Any, List, Optional, Callable
import inspect
from agno.storage.base import Storage

def _maybe_await(func: Callable, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        return func(*args, **kwargs)  # caller moet awaiten
    return func(*args, **kwargs)

class DeltaStorageWrapper(Storage):
    """
    Persist only the DELTA per run across the entire memory:
    for every run, keep only the newest user + newest assistant message.
    This prevents expanded-history duplication inside each run.
    """

    def __init__(self, inner: Storage, verbose: bool = True):
        self.inner = inner
        self.verbose = verbose

    # ---- abstract API (delegate) ----
    def create(self, *args, **kwargs) -> None:
        return _maybe_await(self.inner.create, *args, **kwargs)

    def upgrade_schema(self, *args, **kwargs) -> None:
        fn = getattr(self.inner, "upgrade_schema", None)
        if fn is None:
            return None
        return _maybe_await(fn, *args, **kwargs)

    def drop(self, *args, **kwargs) -> None:
        return _maybe_await(self.inner.drop, *args, **kwargs)

    def read(self, session_id: str, user_id: Optional[str] = None, *args, **kwargs) -> Any:
        return _maybe_await(self.inner.read, session_id, user_id, *args, **kwargs)

    def upsert(self, session: Any, *args, **kwargs) -> None:
        self._prune_all_runs(session)
        return _maybe_await(self.inner.upsert, session, *args, **kwargs)

    def delete_session(self, session_id: str, *args, **kwargs) -> None:
        return _maybe_await(self.inner.delete_session, session_id, *args, **kwargs)

    def get_all_session_ids(self, *args, **kwargs) -> List[str]:
        return _maybe_await(self.inner.get_all_session_ids, *args, **kwargs)

    def get_all_sessions(self, limit: int = 100, *args, **kwargs) -> List[Any]:
        return _maybe_await(self.inner.get_all_sessions, limit, *args, **kwargs)

    def get_recent_sessions(self, limit: int = 100, *args, **kwargs) -> List[Any]:
        return _maybe_await(self.inner.get_recent_sessions, limit, *args, **kwargs)

    # ---- extra pass-throughs some storages use ----
    def save_session(self, session: Any, *args, **kwargs) -> None:
        self._prune_all_runs(session)
        fn = getattr(self.inner, "save_session", None)
        if fn is None:
            return self.upsert(session, *args, **kwargs)
        return _maybe_await(fn, session, *args, **kwargs)

    def save(self, session: Any, *args, **kwargs) -> None:
        self._prune_all_runs(session)
        fn = getattr(self.inner, "save", None)
        if fn is None:
            return self.upsert(session, *args, **kwargs)
        return _maybe_await(fn, session, *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)

    def _prune_all_runs(self, session: Any) -> None:
        # helpers
        def _is_dict(x):
            return isinstance(x, dict)

        def _get(obj, key, default=None):
            return obj.get(key, default) if _is_dict(obj) else getattr(obj, key, default)

        def _set(obj, key, val):
            obj[key] = val if _is_dict(obj) else setattr(obj, key, val)

        mem = _get(session, "memory")
        if mem is None:
            if self.verbose: print("[DeltaStorageWrapper] no memory on session")
            return

        runs = _get(mem, "runs") or []
        if not isinstance(runs, list):
            runs = list(runs)
            _set(mem, "runs", runs)

        total_before = sum(len(_get(r, "messages") or []) for r in runs)

        for run in runs:
            msgs = _get(run, "messages") or []
            if not isinstance(msgs, list):
                msgs = list(msgs)

            # 1) alleen chatrollen + drop from_history==True
            chat = []
            for m in msgs:
                role = _get(m, "role")
                if role not in ("user", "assistant"):
                    continue
                if bool(_get(m, "from_history", False)):
                    continue
                chat.append(m)

            if not chat:
                _set(run, "messages", [])
                continue

            # 2) nieuwste user en nieuwste assistant (chronologische volgorde)
            def role_at(i):
                return _get(chat[i], "role")

            last_user_i = next((i for i in range(len(chat) - 1, -1, -1) if role_at(i) == "user"), None)
            last_asst_i = next((i for i in range(len(chat) - 1, -1, -1) if role_at(i) == "assistant"), None)

            if last_user_i is not None and last_asst_i is not None:
                a, b = sorted([last_user_i, last_asst_i])
                kept = [chat[a], chat[b]]
            elif last_user_i is not None:
                kept = [chat[last_user_i]]
            else:
                kept = [chat[last_asst_i]]

            # optioneel: klein beetje schoonmaken
            for m in kept:
                if _is_dict(m):
                    m.pop("metrics", None)
                    m.pop("from_history", None)

            _set(run, "messages", kept)

        if self.verbose:
            total_after = sum(len(_get(r, "messages") or []) for r in runs)
            sid = _get(session, "id") or _get(session, "session_id")
            print(f"[DeltaStorageWrapper] pruned session {sid}: messages {total_before} → {total_after}")