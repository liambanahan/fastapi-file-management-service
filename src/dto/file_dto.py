from pydantic import BaseModel
from typing import Any, Dict, Optional
from fastapi import UploadFile
from constants.file_extensions import FileExtension

class UploadChunkDTO(BaseModel):
    chunk_size: int
    file: UploadFile
    upload_id: str
    chunk_index: int

class UploadFileDTO(BaseModel):
    upload_id: str
    total_chunks: int
    total_size: int
    file_extension: FileExtension
    content_type: str
    size: int
    detail: Optional[Dict[str, Any]]
    credential: Optional[Dict[str, Any]]
    appointment: str

class FileBaseDTO(BaseModel):
    upload_id: str
    path: str
    credential: Optional[Dict[str, Any]]
    content_type: str
    size: int
    detail: Optional[Dict[str, Any]]
    celery_task_id: str
    appointment: str

class RetryUploadFileDTO(BaseModel):
    id: str
    credential: Optional[Dict[str, Any]]

