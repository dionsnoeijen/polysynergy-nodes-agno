import os
import base64
import hashlib
import boto3
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


def download_images_as_base64(file_paths: List[str]) -> List[Dict[str, str]]:
    """
    Download files from S3 and convert to base64 data URLs.
    This is needed because some AI models (OpenAI, Anthropic) cannot access presigned S3 URLs directly.

    Args:
        file_paths: List of relative S3 file paths (e.g., 'chat/session-123/image.png', 'chat/session-123/document.pdf')

    Returns:
        List of dicts with 'path', 'base64', and 'mime_type' for each file
    """
    if not file_paths:
        return []

    # Get required environment variables
    project_id = os.getenv('PROJECT_ID')
    tenant_id = os.getenv('TENANT_ID')
    aws_region = os.getenv('AWS_REGION', 'eu-central-1')

    if not project_id or not tenant_id:
        logger.warning("Missing PROJECT_ID or TENANT_ID environment variables")
        return []

    # Calculate bucket name
    bucket_name = _get_unified_bucket_name(tenant_id, project_id)

    try:
        # Create S3 client
        is_lambda = os.getenv("AWS_EXECUTION_ENV") is not None

        if is_lambda:
            s3_client = boto3.client('s3', region_name=aws_region)
        else:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=aws_region
            )

        results = []

        for file_path in file_paths:
            try:
                # Download file from S3
                response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
                file_content = response['Body'].read()

                # Determine MIME type from file extension
                mime_type = _get_mime_type(file_path)

                # Convert to base64
                base64_data = base64.b64encode(file_content).decode('utf-8')

                # Create data URL
                data_url = f"data:{mime_type};base64,{base64_data}"

                results.append({
                    'path': file_path,
                    'base64': data_url,
                    'mime_type': mime_type
                })

                logger.info(f"Downloaded and encoded {file_path} as base64 ({len(file_content)} bytes)")

            except Exception as e:
                logger.error(f"Failed to download {file_path}: {e}")
                continue

        return results

    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return []


def _get_mime_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(file_path).suffix.lower()

    mime_types = {
        # Images
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        # Documents
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'text/xml',
        '.html': 'text/html',
        '.md': 'text/markdown',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    return mime_types.get(ext, 'application/octet-stream')  # Default to binary


def _get_unified_bucket_name(tenant_id: str, project_id: str) -> str:
    """
    Get unified bucket name using same strategy as FileManagerService.

    Bucket naming pattern: polysynergy-{tenant_hash}-{project_hash}-media
    Uses MD5 hashes to keep names under 63 characters.
    """
    tenant_id = str(tenant_id) if tenant_id else 'default'
    project_id = str(project_id) if project_id else 'default'

    # For long tenant/project IDs (UUIDs), create shortened versions using hash
    if len(tenant_id) > 8:
        tenant_short = hashlib.md5(tenant_id.encode()).hexdigest()[:8]
    else:
        tenant_short = tenant_id

    if len(project_id) > 8:
        project_short = hashlib.md5(project_id.encode()).hexdigest()[:8]
    else:
        project_short = project_id

    # Bucket naming pattern
    bucket_name = f"polysynergy-{tenant_short}-{project_short}-media".lower()

    # Ensure bucket name is valid (lowercase, no underscores)
    bucket_name = bucket_name.replace('_', '-')

    # Final safety check
    if len(bucket_name) > 63:
        tenant_short = hashlib.md5(tenant_id.encode()).hexdigest()[:6]
        project_short = hashlib.md5(project_id.encode()).hexdigest()[:6]
        bucket_name = f"poly-{tenant_short}-{project_short}-media".lower()

    return bucket_name
