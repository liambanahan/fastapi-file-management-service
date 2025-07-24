from infrastructure.db.mysql import MySQLDB
from .base_repository import BaseRepo
from entities.file import File
from dto.file_dto import FileBaseDTO
from sqlalchemy.orm import Session


class FileRepo(BaseRepo[File]):
    def __init__(self, db: Session) -> None:
        super().__init__(File, db)

    def get_file(self, id: str) -> File:
        return self.get(id=id)

    def create_file(self, file: FileBaseDTO) -> File:
        db_file = File(
            path=file.path, credential=file.credential, content_type=file.content_type,
            size=file.size, detail=file.detail, celery_task_id=file.celery_task_id,
            appointment=file.appointment
        )
        return self.create(db_file)

    def get_files_by_appointment(self, appointment: str) -> list[File]:
        return self.db.query(self.model).filter(self.model.appointment == appointment).all()

    def delete_file(self, file_id: str):
        file_to_delete = self.get(id=file_id)
        if file_to_delete:
            self.db.delete(file_to_delete)
            self.db.commit()
        return file_to_delete
