import os
import json
import threading
import logging
import time
from dataclasses import asdict

import redis


class AgnoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Agno objects that handles complex types."""
    
    def default(self, obj):
        # Handle MessageReferences and similar Agno objects
        if hasattr(obj, '__dict__'):
            # Convert object to dict, handling nested objects
            return self._serialize_object(obj.__dict__)
        elif hasattr(obj, '_asdict'):  # Handle named tuples
            return obj._asdict()
        elif isinstance(obj, (list, tuple)):
            return [self.default(item) if not self._is_json_serializable(item) else item for item in obj]
        elif isinstance(obj, dict):
            return {k: (self.default(v) if not self._is_json_serializable(v) else v) for k, v in obj.items()}
        else:
            # For any other non-serializable object, convert to string representation
            return str(obj)
    
    def _serialize_object(self, obj_dict):
        """Recursively serialize an object's dictionary."""
        result = {}
        for key, value in obj_dict.items():
            if self._is_json_serializable(value):
                result[key] = value
            else:
                result[key] = self.default(value)
        return result
    
    def _is_json_serializable(self, obj):
        """Check if an object is directly JSON serializable."""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False

logger = logging.getLogger(__name__)

_redis = None

# Global sequence counters per run_id to ensure ordering
_sequence_counters = {}
_sequence_lock = threading.Lock()

def get_redis():
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
    if not redis_url:
        raise ValueError("REDIS_URL environment variable is not set")
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            redis_url,
            decode_responses=True,
            db=0
        )
    return _redis

def send_chat_stream_event(flow_id: str, run_id: str, node_id: str, event):
    channel = f"chat_stream:{flow_id}"
    
    # Get next sequence number for this run (thread-safe)
    with _sequence_lock:
        if run_id not in _sequence_counters:
            _sequence_counters[run_id] = 0
        _sequence_counters[run_id] += 1
        sequence_id = _sequence_counters[run_id]

    def fire():
        try:
            redis_conn = get_redis()
            if isinstance(event, dict):
                payload = event
            elif hasattr(event, "__dataclass_fields__"):
                payload = asdict(event)
            else:
                raise TypeError(f"Cannot serialize event: {type(event)}")

            # Add ordering metadata
            payload['run_id'] = run_id
            payload['node_id'] = node_id
            payload['sequence_id'] = sequence_id
            payload['microtime'] = time.time()  # Precise timestamp
            payload['message_id'] = f"msg_{run_id}_{sequence_id}"
            
            logger.debug(f"Sending chat stream event {sequence_id} for run {run_id}")

            redis_conn.publish(channel, json.dumps(payload, cls=AgnoJSONEncoder))
        except Exception as e:
            logger.warning(f"[Redis] chat stream publish failed (ignored): {e}")

    threading.Thread(target=fire).start()

def cleanup_sequence_counter(run_id: str):
    """Clean up sequence counter for completed run to prevent memory leaks."""
    with _sequence_lock:
        if run_id in _sequence_counters:
            del _sequence_counters[run_id]
            logger.debug(f"Cleaned up sequence counter for run {run_id}")