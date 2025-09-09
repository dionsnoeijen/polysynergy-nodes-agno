import json
import os
from typing import Any, Dict, Iterable, List, Union, Sequence
from urllib.parse import urlparse, unquote

UrlItem = Union[str, Dict[str, Any]]

def enrich_metadata(
    urls: Iterable[UrlItem],
    extensions: Sequence[str] = ("pdf",),   # meerdere toegestaan: ("pdf","docx","doc","csv")
) -> List[Dict[str, Any]]:
    """
    Converteer mixed input naar uniform formaat:
      {"url": str, "metadata": dict}

    Ondersteunt:
      - "https://.../file.ext?sig=..."
      - {"url": "...", "metadata": {...}}
      - {"key": "...", "value": "{...json...}"}  (dock_dict)

    Gedrag:
      - Als filename GEEN extensie heeft, voeg de eerste uit `extensions` toe.
      - Als filename al een extensie heeft, laat die staan (ook als die niet in `extensions` zit).
      - Metadata 'document_name' en 'source_url' worden alleen gezet als ze nog ontbreken.
    """
    formatted: List[Dict[str, Any]] = []

    # normaliseer extensies (zonder punt, lower)
    exts = [e.lower().lstrip(".") for e in (extensions or ("pdf",))]
    default_ext = exts[0]  # wordt gebruikt als er nog geen extensie is

    for item in urls or []:
        url: str = ""
        metadata: Dict[str, Any] = {}

        if isinstance(item, str):
            url = item.strip()

        elif isinstance(item, dict):
            if "url" in item:  # standaard formaat
                url = str(item.get("url", "")).strip()
                md = item.get("metadata", {})
                if isinstance(md, str):
                    try:
                        metadata = json.loads(md) if md.strip() else {}
                    except Exception:
                        metadata = {}
                elif isinstance(md, dict):
                    metadata = md or {}
            elif "key" in item:  # dock-dict formaat
                url = str(item.get("key", "")).strip()
                val = item.get("value", "{}")
                if isinstance(val, str):
                    try:
                        metadata = json.loads(val) if val.strip() else {}
                    except Exception:
                        metadata = {}
                elif isinstance(val, dict):
                    metadata = val or {}
            else:
                continue
        else:
            continue

        if not url:
            continue

        # Auto metadata aanvullen (alleen als ontbreekt)
        if "document_name" not in metadata or "source_url" not in metadata:
            parsed = urlparse(url)
            fname = os.path.basename(unquote(parsed.path))  # alleen path, query negeren
            # als leeg (bv. eindigt op '/'), geef fallback
            if not fname:
                fname = f"document.{default_ext}"
            # heeft filename al een extensie?
            base, dot, ext = fname.rpartition(".")
            if dot == "":  # geen extensie
                fname = f"{fname}.{default_ext}"
            # zet defaults als ze ontbreken
            metadata.setdefault("document_name", fname)
            metadata.setdefault("source_url", url)

        formatted.append({"url": url, "metadata": metadata})

    return formatted