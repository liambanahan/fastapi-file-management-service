from services.file_service import FileService
from fastapi import UploadFile, status
from constants.messages import Message
from dto.file_dto import UploadFileDTO, UploadChunkDTO, RetryUploadFileDTO
from api.responses.file_response import FileResponse, UploadInitResponse, UploadChunkResponse, UploadStatusResponse
from handlers.base_handler import BaseHandler
from api.responses.response import SuccessResponse, ErrorResponse
from fastapi.responses import JSONResponse
from exceptions.http_exception import BaseException
from constants.file_extensions import FileExtension
from constants.errors import Errors
from typing import Dict, Any
from core.config import config
from utils import parse_json_to_dict
import logging
import traceback
from dto.file_dto import FileResponseDTO

# Configure logging
logger = logging.getLogger(__name__)

class FileHandler(BaseHandler[FileService]):
    def __init__(self, service: FileService) -> None:
        super().__init__(service=service)

    async def upload_initialize(self):
        upload_id = await self.service.upload_initialize()
        return self.response.success(content=SuccessResponse[UploadInitResponse](data=UploadInitResponse(
            chunk_size=config.APP_MAX_CHUNK_SIZE,
            upload_id=upload_id
        )))

    async def upload_chunk(self, chunk_size: int, upload_id: str, chunk_index: int, file: UploadFile):
        payload = UploadChunkDTO(
            chunk_size=chunk_size, file=file, upload_id=upload_id, chunk_index=chunk_index)
        try:
            await self.service.upload_chunk(payload)
            return self.response.success(content=SuccessResponse[UploadChunkResponse](
                data=UploadChunkResponse(chunk_index=chunk_index, upload_id=upload_id), message=Message.UPLOADED_CHUNK
            ))
        except FileNotFoundError as exc:
            logger.error(f"File not found error in upload_chunk: {str(exc)}")
            return self.response.error(ErrorResponse(message=Errors.FILE_NOT_FOUND), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            logger.error(f"Unexpected error in upload_chunk: {str(exc)}\n{traceback.format_exc()}")
            return self.response.error(ErrorResponse(message="An error occurred during chunk upload"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def upload_complete(self, upload_id: str, total_chunks: int, total_size: int, file_extension: FileExtension,
                              content_type: str, credential: str, detail: str, appointment_id: str, user_id: str, filename: str, size: int = 0) -> JSONResponse:
        logger.info("=== UPLOAD_COMPLETE HANDLER CALLED ===")
        try:
            logger.info(f"Starting upload_complete for upload_id: {upload_id}")
            
            if credential:
                credential_dict = parse_json_to_dict(credential, 'credential')
            else:
                credential_dict = None

            if detail:
                detail_dict = parse_json_to_dict(detail, 'detail')
            else:
                detail_dict = None
                
            payload = UploadFileDTO(upload_id=upload_id, total_chunks=total_chunks, total_size=total_size, file_extension=file_extension,
                                    content_type=content_type, detail=detail_dict, credential=credential_dict, size=size,
                                    appointment_id=appointment_id, user_id=user_id, filename=filename)
            
            logger.info(f"Calling service.upload_complete with payload: {payload}")
            file = await self.service.upload_complete(payload=payload)
            logger.info(f"File created successfully: {file.id}")
            
            download_url = await self.service.get_download_link(file)
            data = FileResponse(id=file.id, path=file.path, credential=file.credential,
                                content_type=file.content_type, detail=file.detail, download_url=download_url,
                                filename=file.filename, size=file.size)
            return self.response.success(content=SuccessResponse[FileResponse](data=data))
            
        except FileNotFoundError as exc:
            logger.error(f"File not found error in upload_complete: {str(exc)}")
            return self.response.error(ErrorResponse(message=Errors.FILE_NOT_FOUND), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            logger.error(f"Unexpected error in upload_complete: {str(exc)}\n{traceback.format_exc()}")
            # Return a generic error message but log the specific error
            return self.response.error(ErrorResponse(message="An error occurred during upload completion"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_file(self, file_id: str, credential=Dict[str, Any]) -> JSONResponse:
        try:
            file = await self.service.get_file(id=file_id, credential=credential)
            download_url = await self.service.get_download_link(file)
            data = FileResponse(id=file.id, path=file.path, credential=file.credential,
                                content_type=file.content_type, detail=file.detail, download_url=download_url,
                                filename=file.filename, size=file.size)
            return self.response.success(SuccessResponse[FileResponse](data=data))
        except BaseException as exception:
            return self.response.error(ErrorResponse(message=exception.message), status=exception.status)

    async def get_upload_status(self, file_id: str, credential=Dict[str, Any]) -> JSONResponse:
        try:
            result = await self.service.get_upload_status(file_id=file_id, credential=credential)
            return self.response.success(SuccessResponse[UploadStatusResponse](data=UploadStatusResponse(status=result)))
        except BaseException as exception:
            return self.response.error(ErrorResponse(message=exception.message), status=exception.status)

    async def retry_upload(self, file_id: str, credential: str):
        if credential:
            credential_dict = parse_json_to_dict(credential, 'credential')
        else:
            credential_dict = None
        payload = RetryUploadFileDTO(id=file_id, credential=credential_dict)
        try:
            file = await self.service.retry_upload(payload=payload)
            download_url = await self.service.get_download_link(file)
            data = FileResponse(id=file.id, path=file.path, credential=file.credential,
                                content_type=file.content_type, detail=file.detail, download_url=download_url,
                                filename=file.filename, size=file.size)
            return self.response.success(content=SuccessResponse[FileResponse](data=data))
        except BaseException as exception:
            return self.response.error(ErrorResponse(message=exception.message), status=exception.status)

    async def get_files_by_appointment(self, appointment_id: str) -> JSONResponse:
        files = await self.service.get_files_by_appointment(appointment_id)
        files_response = []
        for file in files:
            download_url = await self.service.get_download_link(file)
            file_resp = FileResponseDTO.from_orm(file)
            file_resp.download_url = download_url
            files_response.append(file_resp)
        return self.response.success(content=SuccessResponse[list[FileResponseDTO]](data=files_response))

    async def list_all_files(self, user_id: str) -> JSONResponse:
        file_tuples = await self.service.list_all_files(user_id)
        files_response = []
        for file, appointment_name in file_tuples:
            download_url = await self.service.get_download_link(file)
            file_resp = FileResponseDTO.from_orm(file)
            file_resp.download_url = download_url
            file_resp.appointment_name = appointment_name
            files_response.append(file_resp)
        return self.response.success(content=SuccessResponse[list[FileResponseDTO]](data=files_response))

    async def delete_file(self, file_id: str) -> JSONResponse:
        deleted_file = await self.service.delete_file(file_id)
        if not deleted_file:
            return self.response.error(ErrorResponse(message="File not found"), status=status.HTTP_404_NOT_FOUND)
        return self.response.success(content=SuccessResponse(message="File deleted successfully."))
