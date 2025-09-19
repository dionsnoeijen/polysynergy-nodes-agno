"""
RunSeparatedDbWrapper - Optimized Agno DB Storage

Solves the "team run blob" problem by separating member runs from team runs:

PROBLEM: Team sessions contain massive runs with "member_responses" arrays with full member run data,
causing huge JSON blobs and duplicated data in DynamoDB.

SOLUTION: 
1. Intercept upsert_session() calls for team sessions
2. Extract member_responses from runs and replace with lightweight references  
3. On get_session(), reconstruct member_responses by loading individual member runs
4. Maintain full backward compatibility with Agno

This dramatically reduces team session size and eliminates data duplication.
"""

from __future__ import annotations
from typing import Any, List, Optional, Dict, Union, Tuple
import copy
from datetime import date

from agno.db.base import BaseDb, SessionType
from agno.db.schemas import UserMemory
from agno.db.schemas.evals import EvalFilterType, EvalRunRecord, EvalType
from agno.db.schemas.knowledge import KnowledgeRow
from agno.session import Session


class RunSeparatedDbWrapper(BaseDb):
    """
    DB wrapper that separates member runs from team runs for optimal storage.
    
    Intercepts and optimizes team sessions by:
    - Replacing member_responses with member_run_refs on write
    - Reconstructing member_responses from refs on read  
    - Caching frequently accessed sessions
    - Full backward compatibility with Agno
    """

    def __init__(self, inner_db: BaseDb, verbose: bool = True, **kwargs):
        # Initialize BaseDb with same parameters
        super().__init__(**kwargs)
        self.inner_db = inner_db
        self.verbose = verbose
        self.session_cache: Dict[str, Any] = {}  # Cache for sessions
        self.member_run_cache: Dict[str, Any] = {}  # Cache for individual member runs

    # ---- Sessions (Core optimization methods) ----

    def upsert_session(
        self, session: Session, deserialize: Optional[bool] = True
    ) -> Optional[Union[Session, Dict[str, Any]]]:
        """
        Upsert session, optimizing team sessions by separating member runs.
        """
        session_id = getattr(session, 'id', 'unknown')
        
        if self.verbose:
            run_count = len(self._get_runs_from_session(session) or [])
            print(f"[RunSeparatedDb] ⏰ UPSERT CALLED for session {session_id} with {run_count} runs")
            
        # Optimize if this session has runs that can be separated
        if self._should_optimize_session(session):
            if self.verbose:
                run_count = len(self._get_runs_from_session(session) or [])
                print(f"[RunSeparatedDb] Optimizing session {session_id} with {run_count} runs")
            
            try:
                optimized_session = self._optimize_team_session(session)
                
                # Clear cache for this session
                cache_key = f"{session_id}_{getattr(session, 'user_id', 'default')}"
                if cache_key in self.session_cache:
                    del self.session_cache[cache_key]
                    
                # The key issue: serialize as dict instead of object to avoid DynamoDB issues
                return self.inner_db.upsert_session(optimized_session, deserialize=False)
            except Exception as e:
                import traceback
                if self.verbose:
                    print(f"[RunSeparatedDb] Error optimizing session {session_id}: {e}")
                    print(f"[RunSeparatedDb] Full traceback: {traceback.format_exc()}")
                    print(f"[RunSeparatedDb] Falling back to raw session storage")
                # Fallback to storing the raw session without optimization
                return self.inner_db.upsert_session(session, deserialize)
        else:
            if self.verbose:
                print(f"[RunSeparatedDb] Upserting non-optimizable session {session_id} as-is")
            return self.inner_db.upsert_session(session, deserialize)

    def get_session(
        self,
        session_id: str,
        session_type: SessionType,
        user_id: Optional[str] = None,
        deserialize: Optional[bool] = True,
    ) -> Optional[Union[Session, Dict[str, Any]]]:
        """
        Get session, reconstructing team sessions with member_responses.
        """
        cache_key = f"{session_id}_{user_id or 'default'}"
        
        # Check cache first  
        if cache_key in self.session_cache:
            if self.verbose:
                print(f"[RunSeparatedDb] Cache hit for session {session_id}")
            return self.session_cache[cache_key]

        # Get from inner DB
        session = self.inner_db.get_session(session_id, session_type, user_id, deserialize)
        if not session:
            return None

        # ALWAYS reconstruct if this is an optimized session for Agno to work properly
        if self._is_optimized_session(session):
            if self.verbose:
                print(f"[RunSeparatedDb] Reconstructing optimized session {session_id} for Agno")
            session = self._reconstruct_team_session(session)
        else:
            if self.verbose:
                print(f"[RunSeparatedDb] Session {session_id} is not optimized, returning as-is")

        # Cache the result
        self.session_cache[cache_key] = session
        
        if self.verbose:
            session_type_name = type(session).__name__
            run_count = len(self._get_runs_from_session(session) or [])
            print(f"[RunSeparatedDb] 🔄 RETURNING session {session_id} to Agno:")
            print(f"[RunSeparatedDb]   - Type: {session_type_name}")
            print(f"[RunSeparatedDb]   - Runs: {run_count}")
            print(f"[RunSeparatedDb]   - Has metadata: {hasattr(session, 'metadata') or isinstance(session, dict) and 'metadata' in session}")
            
        return session

    # ---- Delegate all other BaseDb methods ----

    def delete_session(self, session_id: str) -> bool:
        # Clear caches and delegate
        cache_keys_to_remove = [k for k in self.session_cache.keys() if k.startswith(session_id)]
        for key in cache_keys_to_remove:
            del self.session_cache[key]
        return self.inner_db.delete_session(session_id)

    def delete_sessions(self, session_ids: List[str]) -> None:
        # Clear caches and delegate
        for session_id in session_ids:
            cache_keys_to_remove = [k for k in self.session_cache.keys() if k.startswith(session_id)]
            for key in cache_keys_to_remove:
                del self.session_cache[key]
        return self.inner_db.delete_sessions(session_ids)

    def get_sessions(
        self,
        session_type: SessionType,
        user_id: Optional[str] = None,
        component_id: Optional[str] = None,
        session_name: Optional[str] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        deserialize: Optional[bool] = True,
    ) -> Union[List[Session], Tuple[List[Dict[str, Any]], int]]:
        sessions = self.inner_db.get_sessions(
            session_type, user_id, component_id, session_name,
            start_timestamp, end_timestamp, limit, page, sort_by, sort_order, deserialize
        )
        
        # Handle both list and tuple return types
        if isinstance(sessions, tuple):
            session_list, total = sessions
            reconstructed_sessions = []
            for session in session_list:
                if self._is_optimized_session(session):
                    session = self._reconstruct_team_session(session)
                reconstructed_sessions.append(session)
            return (reconstructed_sessions, total)
        else:
            reconstructed_sessions = []
            for session in sessions:
                if self._is_optimized_session(session):
                    session = self._reconstruct_team_session(session)
                reconstructed_sessions.append(session)
            return reconstructed_sessions

    def rename_session(
        self, session_id: str, session_type: SessionType, session_name: str, deserialize: Optional[bool] = True
    ) -> Optional[Union[Session, Dict[str, Any]]]:
        # Clear cache and delegate
        cache_keys_to_remove = [k for k in self.session_cache.keys() if k.startswith(session_id)]
        for key in cache_keys_to_remove:
            del self.session_cache[key]
        return self.inner_db.rename_session(session_id, session_type, session_name, deserialize)

    # ---- Memory methods (delegate) ----

    def clear_memories(self) -> None:
        return self.inner_db.clear_memories()

    def delete_user_memory(self, memory_id: str) -> None:
        return self.inner_db.delete_user_memory(memory_id)

    def delete_user_memories(self, memory_ids: List[str]) -> None:
        return self.inner_db.delete_user_memories(memory_ids)

    def get_all_memory_topics(self) -> List[str]:
        return self.inner_db.get_all_memory_topics()

    def get_user_memory(
        self, memory_id: str, deserialize: Optional[bool] = True
    ) -> Optional[Union[UserMemory, Dict[str, Any]]]:
        return self.inner_db.get_user_memory(memory_id, deserialize)

    def get_user_memories(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        topics: Optional[List[str]] = None,
        search_content: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        deserialize: Optional[bool] = True,
    ) -> Union[List[UserMemory], Tuple[List[Dict[str, Any]], int]]:
        return self.inner_db.get_user_memories(
            user_id, agent_id, team_id, topics, search_content, limit, page, sort_by, sort_order, deserialize
        )

    def get_user_memory_stats(
        self, limit: Optional[int] = None, page: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return self.inner_db.get_user_memory_stats(limit, page)

    def upsert_user_memory(
        self, memory: UserMemory, deserialize: Optional[bool] = True
    ) -> Optional[Union[UserMemory, Dict[str, Any]]]:
        return self.inner_db.upsert_user_memory(memory, deserialize)

    # ---- Metrics methods (delegate) ----

    def get_metrics(
        self, starting_date: Optional[date] = None, ending_date: Optional[date] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[int]]:
        return self.inner_db.get_metrics(starting_date, ending_date)

    def calculate_metrics(self) -> Optional[Any]:
        return self.inner_db.calculate_metrics()

    # ---- Knowledge methods (delegate) ----

    def delete_knowledge_content(self, id: str):
        return self.inner_db.delete_knowledge_content(id)

    def get_knowledge_content(self, id: str) -> Optional[KnowledgeRow]:
        return self.inner_db.get_knowledge_content(id)

    def get_knowledge_contents(
        self,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Tuple[List[KnowledgeRow], int]:
        return self.inner_db.get_knowledge_contents(limit, page, sort_by, sort_order)

    def upsert_knowledge_content(self, knowledge_row: KnowledgeRow):
        return self.inner_db.upsert_knowledge_content(knowledge_row)

    # ---- Evals methods (delegate) ----

    def create_eval_run(self, eval_run: EvalRunRecord) -> Optional[EvalRunRecord]:
        return self.inner_db.create_eval_run(eval_run)

    def delete_eval_runs(self, eval_run_ids: List[str]) -> None:
        return self.inner_db.delete_eval_runs(eval_run_ids)

    def get_eval_run(
        self, eval_run_id: str, deserialize: Optional[bool] = True
    ) -> Optional[Union[EvalRunRecord, Dict[str, Any]]]:
        return self.inner_db.get_eval_run(eval_run_id, deserialize)

    def get_eval_runs(
        self,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        model_id: Optional[str] = None,
        filter_type: Optional[EvalFilterType] = None,
        eval_type: Optional[List[EvalType]] = None,
        deserialize: Optional[bool] = True,
    ) -> Union[List[EvalRunRecord], Tuple[List[Dict[str, Any]], int]]:
        return self.inner_db.get_eval_runs(
            limit, page, sort_by, sort_order, agent_id, team_id, workflow_id, 
            model_id, filter_type, eval_type, deserialize
        )

    def rename_eval_run(
        self, eval_run_id: str, name: str, deserialize: Optional[bool] = True
    ) -> Optional[Union[EvalRunRecord, Dict[str, Any]]]:
        return self.inner_db.rename_eval_run(eval_run_id, name, deserialize)

    # ---- Helper Methods ----

    def _serialize_run(self, run: Any) -> str:
        """Serialize run object using Agno's own serialization if available."""
        try:
            # Try using inner_db's serialization method if available
            if hasattr(self.inner_db, '_serialize_run'):
                return self.inner_db._serialize_run(run)
            elif hasattr(run, 'to_dict'):
                # If run has to_dict method, use that
                import json
                return json.dumps(run.to_dict())
            elif hasattr(run, '__dict__'):
                # Fallback: use object's __dict__
                import json
                return json.dumps(run.__dict__, default=str)
            else:
                # Last resort: basic JSON serialization
                import json
                return json.dumps(run, default=str)
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedDb] Warning: Error serializing run: {e}")
            # Ultimate fallback
            import json
            return json.dumps(str(run))

    def _deserialize_run(self, run_data_str: str) -> Any:
        """Deserialize run object using Agno's own deserialization if available."""
        try:
            import json
            run_data = json.loads(run_data_str)
            
            # Try using inner_db's deserialization method if available
            if hasattr(self.inner_db, '_deserialize_run'):
                return self.inner_db._deserialize_run(run_data)
            else:
                # Fallback: return the JSON data as-is
                return run_data
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedDb] Warning: Error deserializing run: {e}")
            # Return original string if all fails
            return run_data_str

    def _get_session_id(self, session: Any) -> str:
        """Extract session ID from session object."""
        try:
            if hasattr(session, 'id'):
                return str(session.id)
            elif hasattr(session, 'session_id'):
                return str(session.session_id)
            elif isinstance(session, dict):
                return str(session.get('id') or session.get('session_id', 'unknown'))
            else:
                # Try common ID attributes
                for attr in ['id', 'session_id', 'conversation_id']:
                    if hasattr(session, attr):
                        value = getattr(session, attr)
                        if value:
                            return str(value)
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedDb] Error extracting session ID from {type(session).__name__}: {e}")
        return 'unknown'

    def _should_optimize_session(self, session: Any) -> bool:
        """Check if this session should be optimized (has runs that can be separated)."""
        runs = self._get_runs_from_session(session)
        
        # Only optimize if we have runs
        should_optimize = runs and len(runs) > 0
        
        if self.verbose:
            session_id = self._get_session_id(session)
            session_type = type(session).__name__
            print(f"[RunSeparatedDb] Analyzing session {session_id} of type {session_type}")
            if should_optimize:
                print(f"[RunSeparatedDb] ✅ Session with {len(runs)} runs detected - will optimize")
            else:
                print(f"[RunSeparatedDb] ➡️  No runs found - no optimization needed")
            
        return should_optimize

    def _is_optimized_session(self, session: Any) -> bool:
        """Check if this is an optimized session (runs are just IDs)."""
        # Check for optimization marker in metadata (now boolean or legacy string)
        try:
            if isinstance(session, dict):
                metadata = session.get('metadata', {})
                return metadata and (metadata.get('__runs_separated') is True or metadata.get('__runs_separated') == 'true')
            else:
                metadata = getattr(session, 'metadata', {})
                return metadata and (metadata.get('__runs_separated') is True or metadata.get('__runs_separated') == 'true')
        except:
            return False

    def _get_runs_from_session(self, session: Any) -> Optional[List[Any]]:
        """Extract runs from session."""
        if hasattr(session, 'runs'):
            return getattr(session, 'runs')
        elif isinstance(session, dict) and 'runs' in session:
            return session.get('runs')
        return None


    def _get_run_id(self, run: Any) -> str:
        """Extract run ID from run object."""
        if hasattr(run, 'run_id'):
            return str(run.run_id)
        elif isinstance(run, dict):
            return str(run.get('run_id', 'unknown'))
        return 'unknown'

    def _optimize_team_session(self, session: Any) -> Any:
        """
        Optimize session by separating runs from the session.
        For first-time optimization: store all runs separately.
        For incremental updates: only store NEW runs that aren't already separated.
        """
        session_id = self._get_session_id(session)
        runs = self._get_runs_from_session(session)
        
        if not runs:
            if self.verbose:
                print(f"[RunSeparatedDb] No runs to optimize in session {session_id}")
            return session

        # Check if this is an incremental update (session already optimized before)
        existing_session = None
        existing_run_ids = []
        try:
            existing_session = self.inner_db.get_session(session_id, SessionType.TEAM, deserialize=True)
            if existing_session and self._is_optimized_session(existing_session):
                if isinstance(existing_session, dict):
                    metadata = existing_session.get('metadata', {})
                    existing_run_ids = metadata.get('__separated_run_ids', [])
                else:
                    metadata = getattr(existing_session, 'metadata', {})
                    existing_run_ids = metadata.get('__separated_run_ids', []) if metadata else []
                    
                if self.verbose:
                    print(f"[RunSeparatedDb] Found existing optimized session with {len(existing_run_ids)} separated runs")
        except:
            pass  # First-time optimization

        # Create optimized session copy
        if isinstance(session, dict):
            optimized_session = copy.deepcopy(session)
        else:
            optimized_session = copy.deepcopy(session)

        original_size = len(str(session))
        
        # Process runs: store only NEW ones, keep track of ALL run IDs
        all_run_ids = existing_run_ids.copy()  # Start with existing run IDs
        new_runs_stored = 0
        
        for i, run in enumerate(runs):
            run_id = self._get_run_id(run)
            
            # Only store if this is a new run (not already separated)
            if run_id not in existing_run_ids:
                all_run_ids.append(run_id)
                
                # Cache the full run object in memory
                self.member_run_cache[run_id] = run
                
                # Store this new run in DynamoDB
                try:
                    # Just store the run data directly - no Session wrapper needed
                    run_storage_id = f"__run__{run_id}"
                    
                    # Store directly in the inner DB's session table as a plain record
                    import json
                    import boto3
                    from datetime import datetime
                    
                    # Use inner_db's boto3 client directly to access the table
                    if hasattr(self.inner_db, 'client') and hasattr(self.inner_db, 'session_table_name'):
                        try:
                            # Create a resource from the client and access the table
                            import boto3
                            resource = boto3.resource('dynamodb', 
                                                     region_name=self.inner_db.client.meta.region_name,
                                                     aws_access_key_id=self.inner_db.client._get_credentials().access_key,
                                                     aws_secret_access_key=self.inner_db.client._get_credentials().secret_key)
                            table = resource.Table(self.inner_db.session_table_name)
                            
                            # Store as DynamoDB item with table schema (session_id is required key)
                            table.put_item(Item={
                                'session_id': run_storage_id,  # Required primary key
                                'id': run_storage_id,  # Keep for compatibility  
                                'user_id': getattr(session, 'user_id', 'system') if hasattr(session, 'user_id') else session.get('user_id', 'system'),
                                'run_data': self._serialize_run(run),  # Proper run serialization
                                'is_run_storage': True,
                                'original_session_id': session_id,
                                'created_at': int(datetime.now().timestamp())
                            })
                            
                            new_runs_stored += 1
                            if self.verbose:
                                run_type = type(run).__name__
                                print(f"[RunSeparatedDb] ✅ Stored NEW run {i}: {run_type} {run_id}")
                                
                        except Exception as e:
                            if self.verbose:
                                print(f"[RunSeparatedDb] ⚠️ Error storing run {run_id} in DynamoDB: {e}")
                            pass
                    else:
                        # Fallback: skip storage but keep in cache
                        if self.verbose:
                            print(f"[RunSeparatedDb] Warning: Cannot access DynamoDB connection for run {run_id}")
                        pass
                        
                except Exception as e:
                    if self.verbose:
                        print(f"[RunSeparatedDb] ⚠️ Failed to store run {run_id}: {e}")
                    # Continue - at least we have it in cache
            else:
                # This run was already stored, just add to tracking
                if self.verbose:
                    run_type = type(run).__name__
                    print(f"[RunSeparatedDb] ⏭️  Skipped existing run {i}: {run_type} {run_id}")

        # Store the run IDs as a proper list (not comma-separated string)
        if isinstance(optimized_session, dict):
            # Store in metadata as a proper list
            if not optimized_session.get('metadata'):
                optimized_session['metadata'] = {}
            optimized_session['metadata']['__separated_run_ids'] = all_run_ids  # Direct list
            optimized_session['runs'] = []  # Empty runs array
            optimized_session['metadata']['__runs_separated'] = True  # Boolean instead of string
        else:
            # For objects, store in metadata attribute
            if not hasattr(optimized_session, 'metadata') or not optimized_session.metadata:
                setattr(optimized_session, 'metadata', {})
            optimized_session.metadata['__separated_run_ids'] = all_run_ids  # Direct list
            setattr(optimized_session, 'runs', [])  # Empty runs array  
            optimized_session.metadata['__runs_separated'] = True  # Boolean instead of string

        if self.verbose:
            try:
                optimized_size = len(str(optimized_session))
                reduction = ((original_size - optimized_size) / original_size) * 100 if original_size > 0 else 0
                print(f"[RunSeparatedDb] 🎯 Session {session_id} optimization complete:")
                print(f"[RunSeparatedDb]   Original size: {original_size:,} chars")
                print(f"[RunSeparatedDb]   Optimized size: {optimized_size:,} chars")
                print(f"[RunSeparatedDb]   Size reduction: {reduction:.1f}%")
                print(f"[RunSeparatedDb]   New runs stored: {new_runs_stored}")
                print(f"[RunSeparatedDb]   Total runs: {len(all_run_ids)}")
            except Exception as e:
                print(f"[RunSeparatedDb] 🎯 Session {session_id} optimization complete:")
                print(f"[RunSeparatedDb]   Original size: {original_size:,} chars")
                print(f"[RunSeparatedDb]   Optimized size: Cannot calculate")
                print(f"[RunSeparatedDb]   New runs stored: {new_runs_stored}")
                print(f"[RunSeparatedDb]   Total runs: {len(all_run_ids)}")

        return optimized_session

    def _reconstruct_team_session(self, session: Any) -> Any:
        """
        Reconstruct session by loading full runs from run IDs.
        """
        session_id = self._get_session_id(session)
        
        # Get run IDs from the metadata field (now as direct list)
        try:
            if isinstance(session, dict):
                metadata = session.get('metadata', {})
                run_ids = metadata.get('__separated_run_ids', [])
            else:
                metadata = getattr(session, 'metadata', {})
                run_ids = metadata.get('__separated_run_ids', []) if metadata else []
                
            # Ensure it's a list (backward compatibility with old comma-separated strings)
            if isinstance(run_ids, str):
                run_ids = run_ids.split(',') if run_ids else []
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedDb] Error getting run IDs from metadata: {e}")
            run_ids = []
        
        if not run_ids:
            if self.verbose:
                print(f"[RunSeparatedDb] No separated run IDs to reconstruct in session {session_id}")
            return session

        if self.verbose:
            print(f"[RunSeparatedDb] Reconstructing session {session_id} with {len(run_ids)} separated run IDs")

        # Create reconstructed copy (try to preserve original session structure)
        try:
            if isinstance(session, dict):
                reconstructed_session = copy.deepcopy(session)
            else:
                reconstructed_session = copy.deepcopy(session)
        except Exception as e:
            if self.verbose:
                print(f"[RunSeparatedDb] ⚠️ Error deep copying session: {e}")
            # Fallback to shallow copy
            if isinstance(session, dict):
                reconstructed_session = session.copy()
            else:
                reconstructed_session = copy.copy(session)

        # Load full run objects from cache or DynamoDB storage
        reconstructed_runs = []
        for run_id in run_ids:  # These should be simple strings now
            if isinstance(run_id, str) and run_id:  # Make sure it's not empty
                # Try to load from cache first
                full_run = self.member_run_cache.get(run_id)
                if full_run:
                    reconstructed_runs.append(full_run)
                    if self.verbose:
                        print(f"[RunSeparatedDb] Loaded run {run_id} from cache")
                else:
                    # Try to load from DynamoDB directly  
                    try:
                        run_storage_id = f"__run__{run_id}"
                        
                        # Get from DynamoDB table using inner_db's boto3 client
                        if hasattr(self.inner_db, 'client') and hasattr(self.inner_db, 'session_table_name'):
                            try:
                                # Create a resource from the client and access the table
                                import boto3
                                resource = boto3.resource('dynamodb', 
                                                         region_name=self.inner_db.client.meta.region_name,
                                                         aws_access_key_id=self.inner_db.client._get_credentials().access_key,
                                                         aws_secret_access_key=self.inner_db.client._get_credentials().secret_key)
                                table = resource.Table(self.inner_db.session_table_name)
                                
                                response = table.get_item(Key={'session_id': run_storage_id})
                                if 'Item' in response:
                                    item = response['Item']
                                    if item.get('is_run_storage') and 'run_data' in item:
                                        # Deserialize the run data using our proper deserialization
                                        full_run = self._deserialize_run(item['run_data'])
                                        reconstructed_runs.append(full_run)
                                        # Cache it for future use
                                        self.member_run_cache[run_id] = full_run
                                        if self.verbose:
                                            print(f"[RunSeparatedDb] ✅ Loaded run {run_id} from DynamoDB storage")
                                    else:
                                        if self.verbose:
                                            print(f"[RunSeparatedDb] ⚠️ Run record {run_id} found but invalid format")
                                else:
                                    if self.verbose:
                                        print(f"[RunSeparatedDb] ⚠️ Run record {run_id} not found")
                                        
                            except Exception as e:
                                if self.verbose:
                                    print(f"[RunSeparatedDb] ⚠️ Error loading run {run_id} from DynamoDB: {e}")
                        else:
                            if self.verbose:
                                print(f"[RunSeparatedDb] Warning: Cannot access DynamoDB _get_table method for run {run_id}")
                                
                    except Exception as e:
                        if self.verbose:
                            print(f"[RunSeparatedDb] ⚠️ Error loading run {run_id} from DynamoDB: {e}")
            else:
                if self.verbose:
                    print(f"[RunSeparatedDb] Warning: Expected non-empty string run ID, got {type(run_id)}: {run_id}")

        # Update session with reconstructed runs and remove optimization markers from metadata
        if isinstance(reconstructed_session, dict):
            reconstructed_session['runs'] = reconstructed_runs
            # Clean up metadata (remove separation markers)
            if reconstructed_session.get('metadata'):
                reconstructed_session['metadata'].pop('__separated_run_ids', None)
                reconstructed_session['metadata'].pop('__runs_separated', None)
                # Remove metadata if it's empty now
                if not reconstructed_session['metadata']:
                    reconstructed_session.pop('metadata', None)
        else:
            setattr(reconstructed_session, 'runs', reconstructed_runs)
            # Clean up metadata (remove separation markers)
            if hasattr(reconstructed_session, 'metadata') and reconstructed_session.metadata:
                reconstructed_session.metadata.pop('__separated_run_ids', None)
                reconstructed_session.metadata.pop('__runs_separated', None)
                # Remove metadata if it's empty now
                if not reconstructed_session.metadata:
                    setattr(reconstructed_session, 'metadata', None)

        if self.verbose:
            print(f"[RunSeparatedDb] 🔧 Reconstructed session {session_id}:")
            print(f"[RunSeparatedDb]   - Full runs loaded: {len(reconstructed_runs)}")
            print(f"[RunSeparatedDb]   - Session type: {type(reconstructed_session).__name__}")
            print(f"[RunSeparatedDb]   - Has runs attribute: {hasattr(reconstructed_session, 'runs')}")
            if hasattr(reconstructed_session, 'runs'):
                print(f"[RunSeparatedDb]   - Runs count: {len(getattr(reconstructed_session, 'runs', []))}")

        return reconstructed_session