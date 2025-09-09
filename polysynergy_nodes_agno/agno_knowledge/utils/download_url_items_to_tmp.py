from __future__ import annotations
import os, hashlib, tempfile
from typing import Dict, List, Iterable, Any, Sequence
from urllib.parse import urlparse
import requests

def download_url_items_to_tmp(
    items: List[Dict[str, Any]],
    *,
    extensions: Sequence[str] = (".docx", ".doc"),
    tmp_dir: str | None = None,
    timeout: int = 25,
    max_bytes: int = 50_000_000,
) -> List[Dict[str, Any]]:
    """
    Verwacht items zoals [{'url': 'https://.../x.docx', 'metadata': {...}}, ...]
    Download naar /tmp en geeft [{'path': '/tmp/xxx.docx', 'metadata': {...}}, ...] terug.
    """
    exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in (extensions or (".docx",))}
    out: List[Dict[str, Any]] = []
    base_tmp = tmp_dir or tempfile.gettempdir()

    for it in items:
        url = it.get("url")
        md  = it.get("metadata") or {}
        if not isinstance(url, str) or not url:
            continue

        path = urlparse(url).path.lower()
        if not any(ext in path for ext in exts):
            continue

        # stabiele bestandsnaam
        h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        # gebruik extensie uit URL-path indien aanwezig, anders eerste uit lijst
        ext = os.path.splitext(path)[1] or next(iter(exts))
        local = os.path.join(base_tmp, f"{h}{ext}")

        if not (os.path.exists(local) and os.path.getsize(local) > 0):
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                size = 0
                with open(local, "wb") as f:
                    for chunk in r.iter_content(256 * 1024):
                        if not chunk:
                            continue
                        size += len(chunk)
                        if size > max_bytes:
                            raise ValueError(f"File too large (> {max_bytes} bytes): {url}")
                        f.write(chunk)

        out.append({"path": local, "metadata": md})
    return out