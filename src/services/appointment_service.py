from repositories.appointment_repository import AppointmentRepo
from services.base_service import BaseService
from dto.appointment_dto import AppointmentCreate, Appointment
from typing import List

class AppointmentService(BaseService[AppointmentRepo]):
    def __init__(self, repo: AppointmentRepo):
        super().__init__(repo)

    def seed_appointments(self):
        hardcoded_appointments = ["subash", "appointment2", "appointment3"]
        for name in hardcoded_appointments:
            existing = self.repo.get_appointment_by_name(name)
            if not existing:
                self.repo.create_appointment(AppointmentCreate(name=name))

    def create_appointment(self, appointment: AppointmentCreate) -> Appointment:
        # In a real app, you'd add more validation here
        return self.repo.create_appointment(appointment)

    def list_appointments(self) -> List[Appointment]:
        return self.repo.list_appointments() 