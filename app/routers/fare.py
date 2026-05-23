from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
import uuid
from app.core.security import get_current_admin
from fastapi import Depends

from app.database.mongodb import db_client
from app.models.domain import FareMatrix

router = APIRouter(prefix="/fares", tags=["LGU Fare Matrix"])

class FareCreate(BaseModel):
    origin: str
    destination: str
    regular_fare: float
    student_pwd_fare: float

@router.post("/", response_model=FareMatrix)
async def create_or_update_fare(fare_data: FareCreate):
    db = db_client.db
    
    fare_id = str(uuid.uuid4())
    new_fare = FareMatrix(
        _id=fare_id,
        origin=fare_data.origin,
        destination=fare_data.destination,
        regular_fare=fare_data.regular_fare,
        student_pwd_fare=fare_data.student_pwd_fare,
        updated_at=datetime.utcnow()
    )
    
    await db["fares"].update_one(
        {"origin": fare_data.origin, "destination": fare_data.destination},
        {"$set": new_fare.model_dump(by_alias=True)},
        upsert=True
    )
    return new_fare

@router.get("/", response_model=list[FareMatrix])
async def get_fare_matrix():
    db = db_client.db
    cursor = db["fares"].find({})
    return await cursor.to_list(length=500)

@router.delete("/{fare_id}", response_model=dict)
async def delete_fare(fare_id: str, current_admin: dict = Depends(get_current_admin)):
    """(Admin Only) Remove a route from the fare matrix."""
    db = db_client.db
    result = await db["fares"].delete_one({"_id": fare_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fare route not found")
        
    return {"message": "Fare route deleted successfully"}