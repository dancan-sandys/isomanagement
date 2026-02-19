import os
import uuid
import hashlib
import mimetypes
import re
from typing import Optional, Tuple, List
from pathlib import Path

from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse


class StorageService:
    """
    Enhanced local filesystem storage service with security features.

    Provides a secure API surface with filename sanitization, content-type validation,
    file size limits, and checksum calculation.
    """

    def __init__(self, base_upload_dir: str = "uploads") -> None:
        self.base_upload_dir = base_upload_dir
        os.makedirs(self.base_upload_dir, exist_ok=True)
        
        # Security configuration
        self.max_file_size = 50 * 1024 * 1024  # 50MB default
        self.allowed_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.txt', '.csv', '.zip', '.rar'
        }
        self.allowed_mime_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
            'text/plain',
            'text/csv',
            'application/zip',
            'application/x-rar-compressed'
        }

    def _ensure_dir(self, subdir: Optional[str] = None) -> str:
        target_dir = self.base_upload_dir
        if subdir:
            target_dir = os.path.join(self.base_upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other security issues.
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename or "unnamed_file"

    def _validate_file_type(self, filename: str, content_type: Optional[str]) -> bool:
        """
        Validate file type based on extension and content-type.
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False
        
        # Check content-type if provided
        if content_type:
            # Handle cases where content-type might be more specific
            base_content_type = content_type.split(';')[0].strip()
            if base_content_type not in self.allowed_mime_types:
                # Try to get content-type from extension
                guessed_type, _ = mimetypes.guess_type(filename)
                if not guessed_type or guessed_type not in self.allowed_mime_types:
                    return False
        
        return True

    def _calculate_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum of file.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def save_upload(self, file: UploadFile, subdir: Optional[str] = None, 
                   max_size: Optional[int] = None) -> Tuple[str, int, Optional[str], str, str]:
        """
        Save an UploadFile to the local filesystem with security validations.

        Args:
            file: UploadFile to save
            subdir: Subdirectory under base_upload_dir
            max_size: Maximum file size in bytes (overrides default)

        Returns:
            Tuple of (file_path, file_size, content_type, original_filename, checksum)

        Raises:
            HTTPException: If file validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate file size
        file_size_limit = max_size or self.max_file_size
        if file.size and file.size > file_size_limit:
            logger.warning(f"File upload rejected: {file.filename} ({file.size} bytes) exceeds limit ({file_size_limit} bytes)")
            raise HTTPException(
                status_code=413, 
                detail={
                    "error": "File too large",
                    "filename": file.filename,
                    "file_size": file.size,
                    "max_size": file_size_limit,
                    "max_size_mb": file_size_limit // (1024*1024),
                    "allowed_extensions": list(self.allowed_extensions),
                    "allowed_mime_types": list(self.allowed_mime_types)
                }
            )

        # Validate file type
        if not self._validate_file_type(file.filename or "", file.content_type):
            logger.warning(f"File upload rejected: {file.filename} (type: {file.content_type}) - invalid file type")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File type not allowed",
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "allowed_extensions": list(self.allowed_extensions),
                    "allowed_mime_types": list(self.allowed_mime_types),
                    "message": "Please check the allowed file types and ensure your file matches the requirements."
                }
            )

        # Sanitize filename
        original_filename = self._sanitize_filename(file.filename or "")
        
        target_dir = self._ensure_dir(subdir)
        extension = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(target_dir, unique_filename)

        try:
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            # Calculate actual file size and checksum
            file_size = os.path.getsize(file_path)
            checksum = self._calculate_checksum(file_path)
            
            logger.info(f"File uploaded successfully: {original_filename} -> {file_path} ({file_size} bytes)")
            
            return file_path, file_size, file.content_type, original_filename, checksum
            
        except Exception as e:
            logger.error(f"File upload failed: {original_filename} - {str(e)}")
            # Clean up partial file if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "File upload failed",
                    "filename": original_filename,
                    "message": "An error occurred while saving the file. Please try again."
                }
            )

    def delete_file(self, file_path: Optional[str]) -> bool:
        """
        Delete a file from storage.
        """
        if not file_path:
            return False
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file information including size, checksum, and metadata.
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            stat = os.stat(file_path)
            checksum = self._calculate_checksum(file_path)
            
            return {
                "file_path": file_path,
                "file_size": stat.st_size,
                "checksum": checksum,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime
            }
        except Exception:
            return None

    def create_file_response(self, file_path: str, filename: str, 
                           content_type: Optional[str] = None) -> FileResponse:
        """
        Create a secure FileResponse for file downloads.
        """
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content-type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or 'application/octet-stream'
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "X-Content-Type-Options": "nosniff"
            }
        )

    def list_files(self, subdir: Optional[str] = None) -> List[dict]:
        """
        List files in a subdirectory with their metadata.
        """
        target_dir = self._ensure_dir(subdir)
        files = []
        
        try:
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                if os.path.isfile(file_path):
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        files.append(file_info)
        except Exception:
            pass
        
        return files


