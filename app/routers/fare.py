from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel
import uuid

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