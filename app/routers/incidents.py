from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database.mongodb import db_client
from app.models.domain import IncidentReport
from app.core.security import get_current_admin

router = APIRouter(prefix="/incidents", tags=["Incident Reports"])

class IncidentCreate(BaseModel):
    driver_qr_hash: str
    issue_description: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def report_incident(incident_data: IncidentCreate):
    """Queue and record local transit incident reports from Commuters."""
    db = db_client.db
    report_id = str(uuid.uuid4())
    
    new_incident = IncidentReport(
        report_id=report_id,
        driver_qr_hash=incident_data.driver_qr_hash,
        issue_description=incident_data.issue_description,
        timestamp=datetime.utcnow()
    )
    
    await db["incident_reports"].insert_one(new_incident.model_dump())
    
    return {
        "status": "received", 
        "message": "Incident reported successfully. The LGU will review this.",
        "report_id": report_id
    }

@router.get("/", response_model=list[IncidentReport])
async def get_incidents(current_admin: dict = Depends(get_current_admin)):
    """(Admin Only) Fetch all reported incidents for LGU review."""
    db = db_client.db
    cursor = db["incident_reports"].find({}).sort("timestamp", -1)
    return await cursor.to_list(length=500)