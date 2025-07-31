from repositories.file_repository import FileRepo
from dto.file_dto import UploadFileDTO, UploadChunkDTO, RetryUploadFileDTO
from typing import Dict, Any, Optional
from entities.file import File
import os
import aiofiles
from fastapi.exceptions import RequestValidationError
from constants.errors import ValidatonErrors
from infrastructure.minio import minioStorage
from dto.file_dto import FileBaseDTO
from services.base_service import BaseService
from exceptions.http_exception import PermissionException, FileNotFoundException, FileUploadedException, FilePendingUploadException
from tasks.file_upload_task import upload_file_task
import uuid
from core.config import config
from celery.result import AsyncResult
from tasks import celery
from constants.upload_stauts import UploadStatus
import logging
import traceback

logger = logging.getLogger(__name__)

class FileService(BaseService[FileRepo]):
    def __init__(self, repo: FileRepo) -> None:
        super().__init__(repo=repo)

    async def upload_initialize(self) -> str:
        upload_id = str(uuid.uuid4())
        os.makedirs(os.path.join(
            config.APP_UPLOAD_DIR, upload_id), exist_ok=True)
        return upload_id

    async def upload_chunk(self, payload: UploadChunkDTO) -> None:
        upload_dir = os.path.join(config.APP_UPLOAD_DIR, payload.upload_id)
        chunk_path = os.path.join(upload_dir, f"{payload.chunk_index}.part")
        async with aiofiles.open(chunk_path, "wb") as chunk_file:
            content = await payload.file.read()
            if len(content) > config.APP_MAX_CHUNK_SIZE:
                raise RequestValidationError(errors=[{
                    'loc': ('body', 'file'),
                    'msg': ValidatonErrors.LE_CHUNCK_SIZE,
                    'type': 'value_error'
                }],
                    body={"file": "invalid_size"})
            await chunk_file.write(content)

    async def upload_complete(self, payload: UploadFileDTO) -> File:
        try:
            logger.info(f"Starting upload_complete for upload_id: {payload.upload_id}")

            # First, check if a file record with this upload_id already exists
            existing_file = self.repo.db.query(File).filter(File.upload_id == payload.upload_id).first()
            if existing_file:
                logger.warning(f"File with upload_id {payload.upload_id} already exists. Returning existing file record.")
                return existing_file

            # Check if upload directory exists
            upload_path = os.path.join(config.APP_UPLOAD_DIR, payload.upload_id)
            if not os.path.exists(upload_path):
                logger.error(f"Upload directory not found: {upload_path}")
                raise FileNotFoundError(f"Upload directory not found for upload_id: {payload.upload_id}")

            # Determine bucket
            if not payload.credential:
                bucket = minioStorage.public_bucket
            else:
                bucket = minioStorage.private_bucket

            filename = f"{payload.upload_id}.{payload.file_extension.value}"
            logger.info(f"Creating Celery task for bucket: {bucket}, filename: {filename}")

            # Create Celery task
            celery_task = upload_file_task.delay(bucket=bucket, upload_id=payload.upload_id,
                                                 total_chunks=payload.total_chunks, filename=filename)
            logger.info(f"Celery task created with ID: {celery_task.id}")

            # Create file record in database
            file_dto = FileBaseDTO(
                upload_id=payload.upload_id,
                path=bucket + "/" + filename,
                content_type=payload.content_type,
                detail=payload.detail,
                size=payload.total_size,
                credential=payload.credential,
                celery_task_id=celery_task.id,
                appointment_id=payload.appointment_id,
                filename=payload.filename
            )
            logger.info(f"Creating file record with DTO: {file_dto}")

            file = self.repo.create_file(file_dto)
            logger.info(f"File record created successfully with ID: {file.id}")
            return file

        except FileNotFoundError:
            # Re-raise FileNotFoundError as is
            raise
        except Exception as e:
            logger.error(f"Error in upload_complete: {str(e)}\n{traceback.format_exc()}")
            # Re-raise the original exception so it can be handled by the handler
            raise

    async def get_download_link(self, file: File) -> str:
        bucket_name = file.path.split("/")[0]
        filename = "/".join(file.path.split("/")[1:])
        if not file.credential:
            return minioStorage.get_url(bucket_name=bucket_name, object_name=filename)
        else:
            for key, value in file.credential.items():
                if not isinstance(value, str):
                    file.credential[key] = str(value)
            return minioStorage.get_presigned_url("GET", bucket_name=bucket_name, object_name=filename, extra_query_params=file.credential)


    async def get_files_by_appointment(self, appointment_id: str) -> list[File]:
        # In a real app, you'd validate the appointment name here
        return self.repo.get_files_by_appointment(appointment_id)

    async def list_all_files(self) -> list[tuple]:
        return self.repo.list_all_files()

    async def delete_file(self, file_id: str):
        # First get the file record to extract MinIO path info
        file = self.repo.get_file(file_id)
        if file:
            # Delete from MinIO
            try:
                bucket_name = file.path.split("/")[0]
                object_name = "/".join(file.path.split("/")[1:])
                minioStorage.remove_object(bucket_name, object_name)
                logger.info(f"Deleted file from MinIO: {bucket_name}/{object_name}")
            except Exception as e:
                logger.error(f"Failed to delete file from MinIO: {str(e)}")
                # Continue with DB deletion even if MinIO deletion fails
            
            # Delete from database
            return self.repo.delete_file(file_id)
        return None
    async def get_file(self, id: id, credential=Dict[str, Any]) -> File:
        file = self.repo.get_file(id=id)
        if file == None:
            raise FileNotFoundException
        if file.credential and credential != file.credential:
            raise PermissionException()
        return file

    async def get_upload_status(self, file_id: str, credential=Dict[str, Any]) -> str:
        file = await self.get_file(id=file_id, credential=credential)
        result = AsyncResult(file.celery_task_id)
        return result.state

    async def retry_upload(self, payload: RetryUploadFileDTO):
        file = await self.get_file(id=payload.id, credential=payload.credential)
        result = AsyncResult(file.celery_task_id)
        if result.status == UploadStatus.SUCCESS.value:
            raise FileUploadedException()
        if result.status == UploadStatus.PENDING.value or result.status == UploadStatus.STARTED.value:
            raise FilePendingUploadException()
        meta = celery.backend.get_task_meta(file.celery_task_id)
        upload_file_task.apply_async(
            args=meta['args'], kwargs=meta['kwargs'], task_id=file.celery_task_id)
        return file
