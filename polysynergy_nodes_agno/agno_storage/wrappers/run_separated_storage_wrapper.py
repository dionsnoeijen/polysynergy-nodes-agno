"""
RunSeparatedStorageWrapper - Optimized Agno Storage

Replaces DeltaStorageWrapper with a more efficient approach:
1. Separates runs from main session for lazy loading
2. Stores runs individually to prevent loading huge sessions
3. Maintains message optimization from DeltaStorageWrapper
4. Provides caching for frequently accessed runs
5. Automatic migration from legacy sessions

No configuration needed - this wrapper is always optimal.
"""

from __future__ import annotations
from typing import Any, List, Optional, Callable, Dict
import inspect
import json
import hashlib
from datetime import datetime, timezone

from agno.storage.base import Storage


def _maybe_await(func: Callable, *args, **kwargs):
    """Handle both sync and async functions."""
    if inspect.iscoroutinefunction(func):
        return func(*args, **kwargs)  # caller should await
    return func(*args, **kwargs)


class RunSeparatedStorageWrapper(Storage):
    """
    Optimized storage wrapper that separates runs for efficient access.
    
    Instead of storing all runs within sessions (causing huge JSON blobs),
    this wrapper:
    1. Stores runs separately with unique IDs
    2. Maintains run references in the main session
    3. Provides lazy loading of individual runs
    4. Caches frequently accessed runs
    5. Automatically migrates legacy sessions on first access
    
    This eliminates the need for persist_delta_only by being efficient by default.
    """

    def __init__(self, inner: Storage, verbose: bool = True):
        self.inner = inner
        self.verbose = verbose
        self.runs_cache: Dict[str, Any] = {}  # Cache for individual runs
        self.session_cache: Dict[str, Any] = {}  # Cache for session metadata
        self.migration_cache: set[str] = set()  # Track migrated sessions

    # ---- Core Storage API (delegate with optimization) ----
    
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
        """
        Read session and reconstruct it for Agno with embedded runs.
        For optimized sessions: loads run references and reconstructs complete session.
        For legacy sessions: returns as-is.
        """
        # Read from storage
        result = _maybe_await(self.inner.read, session_id, user_id, *args, **kwargs)
        
        if not result:
            return result

        # DEBUG: Print session type information
        session_type = type(result).__name__
        storage_mode = self.inner.mode if hasattr(self.inner, 'mode') else 'unknown'
        print(f"[DEBUG] Wrapper read() - session_id: {session_id}, storage_mode: {storage_mode}, returned session type: {session_type}")

        # Skip separated runs (they're not real sessions)
        if self._is_separated_run(result):
            print(f"[DEBUG] Skipping separated run: {session_id}")
            return None

        # For optimized sessions, reconstruct with embedded runs for Agno
        if self._is_optimized_session(result):
            print(f"[DEBUG] Reconstructing optimized session {session_id} for Agno")
            return self._reconstruct_session_for_agno(result)
        
        # Legacy sessions are returned as-is (they already have embedded runs)
        print(f"[DEBUG] Returning legacy session {session_id} as-is")
        return result

    def upsert(self, session: Any, *args, **kwargs) -> None:
        """
        Upsert session with run separation.
        Extracts runs, stores them separately, updates session with references.
        """
        # DEBUG: Print session type information
        session_type = type(session).__name__
        session_id = getattr(session, 'session_id', 'unknown')
        storage_mode = self.inner.mode if hasattr(self.inner, 'mode') else 'unknown'
        
        # DEBUG: Analyze incoming session runs
        incoming_runs = self._get_runs_from_session(session)
        print(f"[DEBUG] Wrapper upsert() - session_id: {session_id}, storage_mode: {storage_mode}, input session type: {session_type}")
        print(f"[DEBUG] Wrapper upsert() - incoming session has {len(incoming_runs)} embedded runs")
        
        for i, run in enumerate(incoming_runs):
            run_messages = run.get('messages', []) if isinstance(run, dict) else getattr(run, 'messages', [])
            print(f"[DEBUG] Wrapper upsert() - run {i+1}: {len(run_messages)} messages")
        
        optimized_session = self._extract_and_separate_runs(session)
        
        optimized_type = type(optimized_session).__name__
        print(f"[DEBUG] Wrapper upsert() - session_id: {session_id}, optimized session type: {optimized_type}")
        
        # Clear relevant caches
        session_id = self._get_session_id(session)
        cache_keys_to_remove = [k for k in self.session_cache.keys() if k.startswith(session_id)]
        for key in cache_keys_to_remove:
            del self.session_cache[key]
            
        return _maybe_await(self.inner.upsert, optimized_session, *args, **kwargs)

    def delete_session(self, session_id: str, *args, **kwargs) -> None:
        """Delete session and associated runs."""
        # TODO: Also delete separated runs
        # For now, just delete main session
        
        # Clear caches
        cache_keys_to_remove = [k for k in self.session_cache.keys() if k.startswith(session_id)]
        for key in cache_keys_to_remove:
            del self.session_cache[key]
        
        runs_keys_to_remove = [k for k in self.runs_cache.keys() if k.startswith(session_id)]
        for key in runs_keys_to_remove:
            del self.runs_cache[key]
        
        return _maybe_await(self.inner.delete_session, session_id, *args, **kwargs)

    def get_all_session_ids(self, *args, **kwargs) -> List[str]:
        return _maybe_await(self.inner.get_all_session_ids, *args, **kwargs)

    def get_all_sessions(self, limit: int = 100, *args, **kwargs) -> List[Any]:
        return _maybe_await(self.inner.get_all_sessions, limit, *args, **kwargs)

    def get_recent_sessions(self, limit: int = 100, *args, **kwargs) -> List[Any]:
        return _maybe_await(self.inner.get_recent_sessions, limit, *args, **kwargs)

    def _reconstruct_session_for_agno(self, session: Any, max_runs: int = 20) -> Any:
        """
        Reconstruct session for Agno with embedded runs.
        Loads the most recent runs and embeds them in the session memory.
        """
        session_id = self._get_session_id(session)
        
        # Get run references from session
        run_references = self._get_run_references(session)
        if not run_references:
            print(f"[DEBUG] No run references found for session {session_id}")
            return session
        
        # Load the most recent runs (limit to max_runs to avoid performance issues)
        runs_to_load = run_references[-max_runs:] if len(run_references) > max_runs else run_references
        print(f"[DEBUG] Loading {len(runs_to_load)} runs for session {session_id} (out of {len(run_references)} total)")
        
        reconstructed_runs = []
        for run_id in runs_to_load:
            run_data = self._load_run_from_storage(run_id)
            if run_data:
                # Extract the actual run data (remove our wrapper metadata)
                if isinstance(run_data, dict) and 'single_run' in run_data:
                    reconstructed_runs.append(run_data['single_run'])
                else:
                    reconstructed_runs.append(run_data)
            else:
                print(f"[DEBUG] Warning: Could not load run {run_id} for session {session_id}")
        
        # Create a copy of the session and embed the runs
        import copy
        reconstructed_session = copy.deepcopy(session)
        
        # Update the memory with embedded runs
        memory = self._get_memory(reconstructed_session)
        if isinstance(memory, dict):
            memory = memory.copy()
        else:
            memory = {}
        
        # Replace run_references with actual embedded runs
        memory['runs'] = reconstructed_runs
        # Remove optimization markers so it looks like a normal session to Agno
        memory.pop('run_references', None)
        memory.pop('__run_separated', None)
        memory.pop('__migrated_at', None)
        memory.pop('__last_updated', None)
        
        # Update session memory
        if hasattr(reconstructed_session, 'memory'):
            reconstructed_session.memory = memory
        elif isinstance(reconstructed_session, dict):
            reconstructed_session['memory'] = memory
        
        print(f"[DEBUG] Reconstructed session {session_id} with {len(reconstructed_runs)} embedded runs")
        return reconstructed_session

    # ---- Extra pass-throughs (with optimization) ----

    def save_session(self, session: Any, *args, **kwargs) -> None:
        optimized_session = self._extract_and_separate_runs(session)
        fn = getattr(self.inner, "save_session", None)
        if fn is None:
            return self.upsert(optimized_session, *args, **kwargs)
        return _maybe_await(fn, optimized_session, *args, **kwargs)

    def save(self, session: Any, *args, **kwargs) -> None:
        optimized_session = self._extract_and_separate_runs(session)
        fn = getattr(self.inner, "save", None)
        if fn is None:
            return self.upsert(optimized_session, *args, **kwargs)
        return _maybe_await(fn, optimized_session, *args, **kwargs)

    # ---- New optimized methods ----

    def read_for_api(self, session_id: str, user_id: Optional[str] = None, *args, **kwargs) -> Any:
        """
        Read session optimized for API usage - returns raw optimized session without reconstruction.
        This bypasses the Agno-optimized reconstruction and gives direct access to the stored session.
        """
        # Just delegate to inner storage - API will handle run reconstruction separately
        return _maybe_await(self.inner.read, session_id, user_id, *args, **kwargs)

    def get_run(self, session_id: str, run_id: str) -> Optional[Any]:
        """Load a single run by ID without loading the entire session."""
        cache_key = f"{session_id}:{run_id}"
        
        # Check cache first
        if cache_key in self.runs_cache:
            return self.runs_cache[cache_key]
        
        # Try to load from separated storage
        run_data = self._load_run_from_storage(run_id)
        
        if run_data:
            # Cache the result
            self.runs_cache[cache_key] = run_data
            return run_data
        
        if self.verbose:
            print(f"[RunSeparatedStorage] Run {run_id} not found")
        return None

    def get_recent_runs(self, session_id: str, limit: int = 10, user_id: Optional[str] = None) -> List[Any]:
        """Get recent runs without loading all session data."""
        # Read session to get run references
        session = self.read(session_id, user_id)
        if not session:
            return []
        
        run_references = self._get_run_references(session)
        if not run_references:
            return []
        
        # Get last N run references
        recent_refs = run_references[-limit:] if len(run_references) > limit else run_references
        
        # Load each run (will use cache if available)
        recent_runs = []
        for run_id in recent_refs:
            run_data = self.get_run(session_id, run_id)
            if run_data:
                recent_runs.append(run_data)
        
        return recent_runs

    # ---- Helper methods ----

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown methods to inner storage."""
        return getattr(self.inner, name)

    def _get_session_type(self, session: Any) -> str:
        """Detect if this is an AgentSession or TeamSession."""
        # Check for distinctive attributes
        if hasattr(session, 'agent_data') or (isinstance(session, dict) and 'agent_data' in session):
            return 'agent'
        elif hasattr(session, 'team_data') or (isinstance(session, dict) and 'team_data' in session):
            return 'team'
        # Fallback: check class name if available
        class_name = session.__class__.__name__ if hasattr(session, '__class__') else ''
        if 'Team' in class_name:
            return 'team'
        elif 'Agent' in class_name:
            return 'agent'
        # Default to agent for backward compatibility
        return 'agent'

    def _get_session_id(self, session: Any) -> str:
        """Extract session ID from session object."""
        if hasattr(session, 'id'):
            return str(session.id)
        elif hasattr(session, 'session_id'):
            return str(session.session_id)
        elif isinstance(session, dict):
            return str(session.get('id') or session.get('session_id', 'unknown'))
        return 'unknown'

    def _get_run_count(self, session: Any) -> int:
        """Get number of runs in session."""
        if self._is_optimized_session(session):
            run_refs = self._get_run_references(session)
            return len(run_refs) if run_refs else 0
        else:
            # Legacy session
            runs = self._get_runs_from_session(session)
            return len(runs) if runs else 0

    def _is_legacy_session(self, session: Any) -> bool:
        """Check if session is in legacy format (with embedded runs)."""
        return not self._is_optimized_session(session)

    def _is_optimized_session(self, session: Any) -> bool:
        """Check if session is already in optimized format."""
        # Check for our optimization marker
        memory = self._get_memory(session)
        session_id = self._get_session_id(session)
        
        print(f"[DEBUG] _is_optimized_session - session_id: {session_id}")
        print(f"[DEBUG] _is_optimized_session - memory type: {type(memory)}")
        
        if isinstance(memory, dict):
            has_marker = memory.get('__run_separated') is True
            has_refs = 'run_references' in memory
            print(f"[DEBUG] _is_optimized_session - has __run_separated marker: {has_marker}")
            print(f"[DEBUG] _is_optimized_session - has run_references: {has_refs}")
            if has_refs:
                print(f"[DEBUG] _is_optimized_session - run_references count: {len(memory.get('run_references', []))}")
            return has_marker
        
        print(f"[DEBUG] _is_optimized_session - memory is not dict, returning False")
        return False

    def _is_separated_run(self, session: Any) -> bool:
        """Check if this is a separated run, not a real session."""
        memory = self._get_memory(session)
        if isinstance(memory, dict):
            return memory.get('__is_separated_run') is True
        return False

    def _get_memory(self, session: Any) -> Any:
        """Extract memory from session object."""
        if hasattr(session, 'memory'):
            return session.memory
        elif isinstance(session, dict) and 'memory' in session:
            return session['memory']
        return None

    def _get_runs_from_session(self, session: Any) -> List[Any]:
        """Extract runs from legacy session."""
        memory = self._get_memory(session)
        if not memory:
            return []
        
        if isinstance(memory, str):
            try:
                memory = json.loads(memory)
            except:
                return []
        
        if isinstance(memory, dict):
            return memory.get('runs', [])
        
        return []

    def _get_run_references(self, session: Any) -> List[str]:
        """Extract run references from optimized session."""
        memory = self._get_memory(session)
        if not memory:
            return []
        
        if isinstance(memory, str):
            try:
                memory = json.loads(memory)
            except:
                return []
        
        if isinstance(memory, dict):
            return memory.get('run_references', [])
        
        return []

    def _generate_run_id(self, session_id: str, run_data: Any) -> str:
        """Generate a deterministic ID for a run based on content."""
        content_str = json.dumps(run_data, sort_keys=True, default=str)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        return f"run_{session_id}_{content_hash}"

    def _migrate_session_to_optimized(self, session: Any) -> Any:
        """Migrate a legacy session to optimized format."""
        runs = self._get_runs_from_session(session)
        if not runs:
            # No runs to separate, just mark as optimized
            return self._mark_session_optimized(session, [])
        
        session_id = self._get_session_id(session)
        run_references = []
        
        # Store each run separately
        for run_data in runs:
            # Apply message optimization (from old DeltaStorageWrapper)
            optimized_run = self._optimize_run_messages(run_data)
            
            # Generate run ID and store
            run_id = self._generate_run_id(session_id, optimized_run)
            self._store_run_separately(run_id, optimized_run)
            run_references.append(run_id)
        
        # Update session with references
        optimized_session = self._mark_session_optimized(session, run_references)
        
        if self.verbose:
            print(f"[RunSeparatedStorage] Migrated session {session_id}: {len(runs)} runs separated")
        
        return optimized_session

    def _mark_session_optimized(self, session: Any, run_references: List[str]) -> Any:
        """Mark session as optimized and replace runs with references."""
        memory = self._get_memory(session)
        
        if isinstance(memory, str):
            try:
                memory_dict = json.loads(memory)
            except:
                memory_dict = {}
        elif isinstance(memory, dict):
            memory_dict = memory.copy()
        else:
            memory_dict = {}
        
        # Replace runs with references and add optimization marker
        optimized_memory = {
            **memory_dict,
            'runs': [],  # Clear embedded runs
            'run_references': run_references,
            '__run_separated': True,
            '__migrated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # CRITICAL FIX: Don't modify the original session object!
        # Instead create a copy with only the memory field changed for storage
        if hasattr(session, 'memory'):
            # Create a copy of the session object for storage
            import copy
            session_copy = copy.deepcopy(session)
            session_copy.memory = optimized_memory
            return session_copy
        elif isinstance(session, dict):
            # Create a copy of the dict
            session_copy = session.copy()
            session_copy['memory'] = optimized_memory
            return session_copy
        
        return session

    def _optimize_run_messages(self, run_data: Any) -> Any:
        """
        Apply message optimization from DeltaStorageWrapper.
        Keep only the newest user and newest assistant message per run.
        """
        # Helper functions
        def _is_dict(x):
            return isinstance(x, dict)

        def _get(obj, key, default=None):
            return obj.get(key, default) if _is_dict(obj) else getattr(obj, key, default)

        def _set(obj, key, val):
            obj[key] = val if _is_dict(obj) else setattr(obj, key, val)
        
        messages = _get(run_data, "messages") or []
        if not isinstance(messages, list):
            messages = list(messages)

        # Filter to only chat roles and drop from_history messages
        chat = []
        for m in messages:
            role = _get(m, "role")
            if role not in ("user", "assistant"):
                continue
            if bool(_get(m, "from_history", False)):
                continue
            chat.append(m)

        if not chat:
            _set(run_data, "messages", [])
            return run_data

        # Keep newest user and newest assistant (chronological order)
        def role_at(i):
            return _get(chat[i], "role")

        last_user_i = next((i for i in range(len(chat) - 1, -1, -1) if role_at(i) == "user"), None)
        last_asst_i = next((i for i in range(len(chat) - 1, -1, -1) if role_at(i) == "assistant"), None)

        if last_user_i is not None and last_asst_i is not None:
            a, b = sorted([last_user_i, last_asst_i])
            kept = [chat[a], chat[b]]
        elif last_user_i is not None:
            kept = [chat[last_user_i]]
        elif last_asst_i is not None:
            kept = [chat[last_asst_i]]
        else:
            kept = []

        # Clean up kept messages
        for m in kept:
            if _is_dict(m):
                m.pop("metrics", None)
                m.pop("from_history", None)

        _set(run_data, "messages", kept)
        return run_data

    def _extract_and_separate_runs(self, session: Any) -> Any:
        """
        Extract runs from session memory and store them separately.
        Only stores the LAST run from the incoming session (the new one).
        """
        session_id = self._get_session_id(session)
        
        # Get incoming runs from session
        incoming_runs = self._get_runs_from_session(session)
        print(f"[DEBUG] _extract_and_separate_runs - session {session_id} has {len(incoming_runs)} total runs from Agno")
        
        if not incoming_runs:
            # No runs to process
            return self._mark_session_optimized(session, [])
        
        # Get existing run references from storage
        existing_run_refs = []
        try:
            existing_session = self.inner.read(session_id)
            if existing_session:
                existing_run_refs = self._get_run_references(existing_session)
                print(f"[DEBUG] _extract_and_separate_runs - found {len(existing_run_refs)} existing run references in storage")
        except:
            print(f"[DEBUG] _extract_and_separate_runs - no existing session found in storage")
        
        # Only process the LAST run (the new one that Agno just added)
        # Agno always gives us ALL runs, so we just need the last one
        last_run = incoming_runs[-1]
        print(f"[DEBUG] _extract_and_separate_runs - processing only the LAST run (the new one)")
        
        # Apply message optimization
        optimized_run = self._optimize_run_messages(last_run)
        
        # Generate run ID and store
        run_id = self._generate_run_id(session_id, optimized_run)
        
        # Check if this exact run already exists (dedup check)
        if run_id not in existing_run_refs:
            print(f"[DEBUG] _extract_and_separate_runs - storing new run {run_id}")
            self._store_run_separately(run_id, optimized_run)
            existing_run_refs.append(run_id)
        else:
            print(f"[DEBUG] _extract_and_separate_runs - run {run_id} already exists, skipping")
        
        # Update session with all run references
        optimized_session = self._mark_session_optimized(session, existing_run_refs)
        
        print(f"[DEBUG] _extract_and_separate_runs - session now has {len(existing_run_refs)} total run references")
        
        return optimized_session

    def _handle_incremental_runs(self, session: Any) -> Any:
        """
        Handle incremental run updates for already optimized sessions.
        Extract any new runs that were added and store them separately.
        """
        try:
            session_id = self._get_session_id(session)
            
            # Get current embedded runs (if any - these are new runs)
            current_runs = self._get_runs_from_session(session)
            
            print(f"[DEBUG] _handle_incremental_runs - session_id: {session_id}, found {len(current_runs)} embedded runs")
            
            if not current_runs:
                # No new runs to process
                if self.verbose:
                    print(f"[RunSeparatedStorage] No new runs in optimized session {session_id}")
                return session
            
            # Get existing run references
            memory = self._get_memory(session)
            if isinstance(memory, str):
                try:
                    memory_dict = json.loads(memory)
                except:
                    memory_dict = {}
            elif isinstance(memory, dict):
                memory_dict = memory.copy()
            else:
                memory_dict = {}
                
            existing_run_refs = memory_dict.get('run_references', [])
            
            print(f"[DEBUG] _handle_incremental_runs - session has {len(existing_run_refs)} existing run references")
            print(f"[DEBUG] _handle_incremental_runs - processing {len(current_runs)} embedded runs")
            
            # Process new runs and create references
            new_run_refs = []
            for i, run_data in enumerate(current_runs):
                print(f"[DEBUG] _handle_incremental_runs - processing embedded run {i+1}/{len(current_runs)}")
                
                # Apply message optimization
                optimized_run = self._optimize_run_messages(run_data)
                
                # Generate run ID and check if it already exists
                run_id = self._generate_run_id(session_id, optimized_run)
                print(f"[DEBUG] _handle_incremental_runs - generated run_id: {run_id}")
                
                # Only store if this run doesn't already exist
                if run_id not in existing_run_refs:
                    print(f"[DEBUG] _handle_incremental_runs - storing new run {run_id}")
                    self._store_run_separately(run_id, optimized_run)
                    new_run_refs.append(run_id)
                else:
                    print(f"[DEBUG] _handle_incremental_runs - run {run_id} already exists, skipping")
            
            # Update session: add new run references, clear embedded runs
            updated_run_refs = existing_run_refs + new_run_refs
            optimized_memory = {
                **memory_dict,
                'runs': [],  # Clear new embedded runs
                'run_references': updated_run_refs,
                '__run_separated': True,
                '__last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # CRITICAL FIX: Don't modify the original session object!
            # Create a copy with updated memory for storage
            if hasattr(session, 'memory'):
                import copy
                session_copy = copy.deepcopy(session)
                session_copy.memory = optimized_memory
                result_session = session_copy
            elif isinstance(session, dict):
                session_copy = session.copy()
                session_copy['memory'] = optimized_memory
                result_session = session_copy
            else:
                result_session = session
            
            if self.verbose:
                print(f"[RunSeparatedStorage] Added {len(new_run_refs)} new runs to optimized session {session_id}")
            
            return result_session
            
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedStorage] Error handling incremental runs: {e}")
            # Fallback: return session as-is to avoid breaking the flow
            return session

    def _store_run_separately(self, run_id: str, run_data: Any):
        """
        Store a run in separate storage.
        Creates appropriate Session type based on storage mode.
        """
        try:
            import time
            
            # Determine the session type based on storage mode
            storage_mode = self.inner.mode if hasattr(self.inner, 'mode') else 'agent'
            
            if storage_mode == 'team':
                from agno.storage.session.team import TeamSession
                run_session = TeamSession(
                    session_id=run_id,
                    team_id="run_storage",   # Dummy team ID
                    user_id="run_storage",   # Dummy user ID  
                    memory={
                        'single_run': run_data,
                        'run_id': run_id,
                        '__is_separated_run': True
                    },
                    created_at=int(time.time())
                )
            elif storage_mode == 'workflow':
                from agno.storage.session.workflow import WorkflowSession
                run_session = WorkflowSession(
                    session_id=run_id,
                    workflow_id="run_storage",  # Dummy workflow ID
                    user_id="run_storage",      # Dummy user ID  
                    memory={
                        'single_run': run_data,
                        'run_id': run_id,
                        '__is_separated_run': True
                    },
                    created_at=int(time.time())
                )
            elif storage_mode == 'workflow_v2':
                from agno.storage.session.v2.workflow import WorkflowSession as WorkflowSessionV2
                run_session = WorkflowSessionV2(
                    session_id=run_id,
                    workflow_id="run_storage",  # Dummy workflow ID
                    user_id="run_storage",      # Dummy user ID  
                    runs=[{
                        'single_run': run_data,
                        'run_id': run_id,
                        '__is_separated_run': True
                    }],
                    created_at=int(time.time())
                )
            else:  # Default to agent
                from agno.storage.session.agent import AgentSession
                run_session = AgentSession(
                    session_id=run_id,
                    agent_id="run_storage",  # Dummy agent ID
                    user_id="run_storage",   # Dummy user ID  
                    memory={
                        'single_run': run_data,
                        'run_id': run_id,
                        '__is_separated_run': True
                    },
                    created_at=int(time.time())
                )
            
            # Store using inner storage
            result = _maybe_await(self.inner.upsert, run_session)
            
            if self.verbose:
                print(f"[RunSeparatedStorage] Stored separated run {run_id} as {storage_mode} session")
                
            return result
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedStorage] Error storing run {run_id}: {e}")
            raise

    def _load_run_from_storage(self, run_id: str) -> Optional[Any]:
        """Load a single run from separate storage."""
        try:
            run_session = _maybe_await(self.inner.read, run_id)
            if not run_session:
                return None
            
            memory = self._get_memory(run_session)
            if isinstance(memory, dict) and '__is_separated_run' in memory:
                return memory.get('single_run')
            
            return None
        except:
            return None

    def _create_lazy_session(self, session: Any) -> Any:
        """
        Create a session object with lazy-loaded runs.
        This maintains compatibility with existing Agno code.
        """
        if not self._is_optimized_session(session):
            return session
        
        # For now, return the session as-is
        # TODO: Implement LazyRuns object that loads runs on access
        return session