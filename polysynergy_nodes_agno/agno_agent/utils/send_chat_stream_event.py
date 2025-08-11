import os
import json
import threading
import logging
from dataclasses import asdict

import redis

logger = logging.getLogger(__name__)

_redis = None

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

    def fire():
        try:
            redis_conn = get_redis()
            if isinstance(event, dict):
                payload = event
            elif hasattr(event, "__dataclass_fields__"):
                payload = asdict(event)
            else:
                raise TypeError(f"Cannot serialize event: {type(event)}")

            payload['run_id'] = run_id
            payload['node_id'] = node_id

            redis_conn.publish(channel, json.dumps(payload))
        except Exception as e:
            logger.warning(f"[Redis] chat stream publish failed (ignored): {e}")

    threading.Thread(target=fire).start()