from __future__ import annotations
from typing import Any, Dict, List
import textract
from agno.document import Document

def files_to_documents(path_items: List[Dict[str, Any]], encoding: str = "utf-8") -> List[Document]:
    docs: List[Document] = []
    for it in path_items:
        path = it.get("path")
        meta = it.get("metadata") or {}
        if not path:
            continue
        try:
            raw = textract.process(path)              # kiest parser op basis van extensie
            text = raw.decode(encoding, errors="replace").strip() or "(empty document body)"
            docs.append(Document(content=text, name=str(path), meta_data=meta))
        except Exception:
            # hier kun je je eigen logging/telemetry gebruiken
            continue
    return docs