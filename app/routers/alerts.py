from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database.mongodb import db_client
from app.models.domain import CommunityAlert
from app.core.security import get_current_admin

router = APIRouter(prefix="/alerts", tags=["Community Alerts"])

class AlertCreate(BaseModel):
    title: str
    message: str
    is_critical: bool = False

@router.post("/", response_model=CommunityAlert, status_code=status.HTTP_201_CREATED)
async def create_alert(alert_data: AlertCreate, current_admin: dict = Depends(get_current_admin)):
    """(Admin Only) Create a new community or traffic alert."""
    db = db_client.db
    alert_id = str(uuid.uuid4())
    
    new_alert = CommunityAlert(
        _id=alert_id,
        title=alert_data.title,
        message=alert_data.message,
        is_critical=alert_data.is_critical,
        updated_at=datetime.utcnow()
    )
    
    await db["alerts"].insert_one(new_alert.model_dump(by_alias=True))
    return new_alert

@router.get("/", response_model=list[CommunityAlert])
async def get_alerts():
    """Fetch active traffic and road closure alerts for Bongao."""
    db = db_client.db
    cursor = db["alerts"].find({}).sort("updated_at", -1) # Fetch newest first
    return await cursor.to_list(length=100)

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, current_admin: dict = Depends(get_current_admin)):
    """(Admin Only) Remove an old or expired alert."""
    db = db_client.db
    result = await db["alerts"].delete_one({"_id": alert_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    return {"message": "Alert deleted successfully"}