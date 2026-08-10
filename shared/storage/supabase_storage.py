import uuid
import requests
from core.config import settings

BUCKET = "profile-images"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB, matches bucket limit


class StorageUploadError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def upload_profile_image(
    file_bytes: bytes,
    content_type: str,
    auth_id: uuid.UUID,
) -> str:
    
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise StorageUploadError(
            f"Unsupported image type: {content_type}. "
            f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
            status_code=422,
        )

    if len(file_bytes) > MAX_SIZE_BYTES:
        raise StorageUploadError(
            "Image exceeds the 5 MB size limit.",
            status_code=422,
        )

    extension = content_type.split("/")[-1]
    object_path = f"{auth_id}.{extension}"

    upload_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/{BUCKET}/{object_path}"
    )

    response = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
        data=file_bytes,
        timeout=15,
    )

    if response.status_code not in (200, 201):
        raise StorageUploadError(
            f"Upload to storage failed: {response.text}",
            status_code=502,
        )

    public_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/public/"
        f"{BUCKET}/{object_path}"
    )

    return public_url