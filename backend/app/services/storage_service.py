import os
import uuid
from typing import Optional, Tuple

from fastapi import UploadFile


class StorageService:
    """
    Simple local filesystem storage service.

    Provides a small API surface so we can swap the implementation later (e.g., to S3)
    without touching business logic.
    """

    def __init__(self, base_upload_dir: str = "uploads") -> None:
        self.base_upload_dir = base_upload_dir
        os.makedirs(self.base_upload_dir, exist_ok=True)

    def _ensure_dir(self, subdir: Optional[str] = None) -> str:
        target_dir = self.base_upload_dir
        if subdir:
            target_dir = os.path.join(self.base_upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def save_upload(self, file: UploadFile, subdir: Optional[str] = None) -> Tuple[str, int, Optional[str], str]:
        """
        Save an UploadFile to the local filesystem under base_upload_dir/subdir with a unique name.

        Returns (file_path, file_size, content_type, original_filename)
        """
        target_dir = self._ensure_dir(subdir)
        extension = os.path.splitext(file.filename or "")[1].lower()
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(target_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            # Using file.file which is a SpooledTemporaryFile
            buffer.write(file.file.read())

        file_size = os.path.getsize(file_path)
        content_type = file.content_type
        original_filename = file.filename or unique_filename
        return file_path, file_size, content_type, original_filename

    def delete_file(self, file_path: Optional[str]) -> bool:
        if not file_path:
            return False
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False


