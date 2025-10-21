from __future__ import annotations
import os, hashlib, tempfile, boto3
from typing import Dict, List, Iterable, Any, Sequence
from urllib.parse import urlparse
import requests
from botocore.exceptions import ClientError
from polysynergy_node_runner.utils.tenant_project_naming import get_prefixed_name

def download_mixed_items_to_tmp(
    items: List[Dict[str, Any]],
    *,
    extensions: Sequence[str] = (".docx", ".doc"),
    tmp_dir: str | None = None,
    timeout: int = 25,
    max_bytes: int = 50_000_000,
    s3_bucket: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Verwacht items zoals [{'url': 'https://.../x.docx', 'metadata': {...}}, ...]
    OF [{'url': 'folder/file.docx', 'metadata': {...}}, ...] (S3 keys)
    
    Download URLs via HTTP en S3 keys via boto3 naar /tmp 
    Geeft [{'path': '/tmp/xxx.docx', 'metadata': {...}}, ...] terug.
    """
    exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in (extensions or (".docx",))}
    out: List[Dict[str, Any]] = []
    base_tmp = tmp_dir or tempfile.gettempdir()
    
    # Initialize S3 client if needed
    s3_client = None

    for it in items:
        url_or_key = it.get("url")
        md = it.get("metadata") or {}
        if not isinstance(url_or_key, str) or not url_or_key:
            continue

        # Check if it's a URL or S3 key
        is_url = url_or_key.startswith(('http://', 'https://'))
        
        if is_url:
            # Handle as URL
            path = urlparse(url_or_key).path.lower()

            # Check if valid extension exists in URL path OR in metadata filename
            has_valid_ext = any(ext in path for ext in exts)
            if not has_valid_ext and "filename" in md:
                # Check if metadata filename has valid extension
                filename_lower = md["filename"].lower()
                has_valid_ext = any(filename_lower.endswith(ext) for ext in exts)

            if not has_valid_ext:
                continue
                
            try:
                resp = requests.get(url_or_key, timeout=timeout, stream=True)
                resp.raise_for_status()
                
                # Check content length
                content_length = resp.headers.get('content-length')
                if content_length and int(content_length) > max_bytes:
                    print(f"Skipping {url_or_key}: too large ({content_length} bytes)")
                    continue
                
                # Generate filename - prefer metadata filename if available
                if "filename" in md and md["filename"]:
                    filename = md["filename"]
                else:
                    parsed = urlparse(url_or_key)
                    filename = os.path.basename(parsed.path)
                    if not filename or "." not in filename:
                        # Generate filename from URL hash
                        url_hash = hashlib.md5(url_or_key.encode()).hexdigest()[:8]
                        ext = next((ext for ext in exts if ext in path), ".tmp")
                        filename = f"download_{url_hash}{ext}"
                
                tmp_path = os.path.join(base_tmp, filename)
                
                # Download file
                total_size = 0
                with open(tmp_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            total_size += len(chunk)
                            if total_size > max_bytes:
                                f.close()
                                os.unlink(tmp_path)
                                print(f"Skipping {url_or_key}: exceeded size limit during download")
                                break
                            f.write(chunk)
                    else:
                        # Completed successfully
                        out.append({"path": tmp_path, "metadata": md})
                        
            except Exception as e:
                print(f"Failed to download {url_or_key}: {e}")
                continue
                
        else:
            # Handle as S3 key
            s3_key = url_or_key
            
            # Check extension
            if not any(s3_key.lower().endswith(ext) for ext in exts):
                continue
                
            try:
                # Initialize S3 client on first use
                if s3_client is None:
                    s3_client = boto3.client('s3')
                
                # Get bucket from parameter, env var, or auto-detect from project
                bucket = s3_bucket or os.environ.get('S3_BUCKET') or get_prefixed_name(prefix="polysynergy", suffix="media", max_length=63)
                if not bucket:
                    print(f"No S3 bucket specified for key: {s3_key}")
                    continue
                
                # Check if object exists and get size
                try:
                    response = s3_client.head_object(Bucket=bucket, Key=s3_key)
                    file_size = response['ContentLength']
                    if file_size > max_bytes:
                        print(f"Skipping {s3_key}: too large ({file_size} bytes)")
                        continue
                except ClientError as e:
                    print(f"S3 object not found: {s3_key} - {e}")
                    continue
                
                # Generate local filename
                filename = os.path.basename(s3_key)
                if not filename or "." not in filename:
                    # Generate filename from key hash
                    key_hash = hashlib.md5(s3_key.encode()).hexdigest()[:8]
                    ext = next((ext for ext in exts if s3_key.lower().endswith(ext)), ".tmp")
                    filename = f"s3_{key_hash}{ext}"
                
                tmp_path = os.path.join(base_tmp, filename)
                
                # Download from S3
                s3_client.download_file(bucket, s3_key, tmp_path)
                out.append({"path": tmp_path, "metadata": md})
                
            except Exception as e:
                print(f"Failed to download S3 object {s3_key}: {e}")
                continue

    return out