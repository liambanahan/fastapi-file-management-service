from sqlalchemy.orm import Session
from .base_repository import BaseRepo
from entities.appointment import Appointment
from dto.appointment_dto import AppointmentCreate
from typing import List

class AppointmentRepo(BaseRepo[Appointment]):
    def __init__(self, db: Session):
        super().__init__(Appointment, db)

    def create_appointment(self, appointment: AppointmentCreate) -> Appointment:
        db_appointment = Appointment(name=appointment.name)
        return self.create(db_appointment)

    def get_appointment_by_name(self, name: str) -> Appointment:
        return self.db.query(self.model).filter(self.model.name == name).first()

    def list_appointments(self) -> List[Appointment]:
        return self.db.query(self.model).all() 