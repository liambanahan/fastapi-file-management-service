from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infrastructure.db.mysql import mysql
from repositories.appointment_repository import AppointmentRepo
from services.appointment_service import AppointmentService
from dto.appointment_dto import Appointment, AppointmentCreate
from api.responses.response import SuccessResponse
from typing import List

router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["appointments"]
)

def get_appointment_service(db: Session = Depends(mysql.get_db)) -> AppointmentService:
    repo = AppointmentRepo(db=db)
    return AppointmentService(repo=repo)

@router.post("/", response_model=SuccessResponse[Appointment])
def create_appointment(appointment: AppointmentCreate, service: AppointmentService = Depends(get_appointment_service)):
    new_appointment = service.create_appointment(appointment)
    return SuccessResponse(data=new_appointment)

@router.get("/", response_model=SuccessResponse[List[Appointment]])
def list_appointments(service: AppointmentService = Depends(get_appointment_service)):
    appointments = service.list_appointments()
    return SuccessResponse(data=appointments) 