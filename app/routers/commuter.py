from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid

from app.database.mongodb import db_client
from app.models.domain import Commuter
from app.models.schemas import CommuterCreate
from app.core.security import get_password_hash

router = APIRouter(prefix="/commuters", tags=["Commuter Public Endpoints"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_commuter(commuter_data: CommuterCreate):
    db = db_client.db
    
    existing_user = await db["commuters"].find_one({"email": commuter_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    is_verified = True if commuter_data.discount_status == "Regular" else False

    commuter_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(commuter_data.password)
    
    new_commuter = Commuter(
        _id=commuter_id,
        name=commuter_data.name,
        email=commuter_data.email,
        hashed_password=hashed_pwd,
        discount_status=commuter_data.discount_status,
        is_verified=is_verified,
        created_at=datetime.utcnow()
    )
    
    await db["commuters"].insert_one(new_commuter.model_dump(by_alias=True))
    
    return {
        "status": "success",
        "message": f"Account created for {commuter_data.name}.",
        "commuter_id": commuter_id,
        "discount_status": commuter_data.discount_status,
        "is_verified": is_verified
    }