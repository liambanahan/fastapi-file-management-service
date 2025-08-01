from pydantic import BaseModel
from typing import Optional, Dict, Any
from constants.upload_stauts import UploadStatus


class UploadInitResponse(BaseModel):
    chunk_size: int
    upload_id: str


class UploadChunkResponse(BaseModel):
    chunk_index: int
    upload_id: str


class FileResponse(BaseModel):
    id: str
    filename: str
    path: str
    content_type: str
    size: int
    detail:  Optional[Dict[str, Any]]
    credential:  Optional[Dict[str, Any]]
    download_url: str


class UploadStatusResponse(BaseModel):
    status: UploadStatus
