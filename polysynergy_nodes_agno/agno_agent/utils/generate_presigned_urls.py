import os
import hashlib
import boto3
import logging
from typing import List

logger = logging.getLogger(__name__)


def generate_presigned_urls_for_files(file_paths: List[str]) -> List[str]:
    """
    Convert relative S3 file paths to presigned URLs.
    Uses the same bucket naming strategy as FileManagerService.

    Args:
        file_paths: List of relative file paths (e.g., 'chat/session-123/image.png')

    Returns:
        List of presigned URLs (or original paths if generation fails)
    """
    if not file_paths:
        return []

    # Get required environment variables
    project_id = os.getenv('PROJECT_ID')
    tenant_id = os.getenv('TENANT_ID')
    aws_region = os.getenv('AWS_REGION', 'eu-central-1')

    if not project_id or not tenant_id:
        logger.warning("Missing PROJECT_ID or TENANT_ID environment variables, cannot generate presigned URLs")
        return file_paths  # Return original paths as fallback

    # Calculate bucket name using same logic as FileManagerService
    bucket_name = _get_unified_bucket_name(tenant_id, project_id)

    try:
        # Create S3 client
        is_lambda = os.getenv("AWS_EXECUTION_ENV") is not None

        if is_lambda:
            # In Lambda, use IAM role
            s3_client = boto3.client('s3', region_name=aws_region)
        else:
            # Local development with explicit credentials
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=aws_region
            )

        presigned_urls = []

        for file_path in file_paths:
            # S3 key is just the file path directly
            s3_key = file_path

            try:
                # Generate presigned URL (7 days expiry for conversation history)
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_key},
                    ExpiresIn=604800  # 7 days (for chat history to work with images)
                )
                presigned_urls.append(url)
                logger.info(f"Generated presigned URL for {file_path}")
            except Exception as e:
                logger.error(f"Failed to generate presigned URL for {file_path}: {e}")
                # Fallback to original path
                presigned_urls.append(file_path)

        return presigned_urls

    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return file_paths  # Return original paths as fallback


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

    # Final safety check - should never exceed 63 chars with our hash approach
    if len(bucket_name) > 63:
        # Emergency fallback: use shorter hashes
        tenant_short = hashlib.md5(tenant_id.encode()).hexdigest()[:6]
        project_short = hashlib.md5(project_id.encode()).hexdigest()[:6]
        bucket_name = f"poly-{tenant_short}-{project_short}-media".lower()

    return bucket_name