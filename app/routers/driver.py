from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from pydantic import BaseModel
import uuid

from app.database.mongodb import db_client
from app.models.domain import Driver
from app.models.schemas import Token
from app.services.qr_service import generate_driver_qr_hash
from app.core.security import create_access_token

router = APIRouter(prefix="/drivers", tags=["Driver Accounts & LGU Management"])

class DriverCreate(BaseModel):
    name: str
    franchise_number: str

class DriverLogin(BaseModel):
    qr_hash: str  # The driver's mobile app scans the official LGU QR code to log in

# ---------------------------------------------------------
# LGU ADMINISTRATOR ENDPOINTS (For managing drivers)
# ---------------------------------------------------------

@router.post("/register", response_model=Driver, status_code=status.HTTP_201_CREATED)
async def register_driver(driver_data: DriverCreate):
    """(Admin Only) Registers a new driver and generates their QR credential."""
    db = db_client.db
    
    existing = await db["drivers"].find_one({"franchise_number": driver_data.franchise_number})
    if existing:
        raise HTTPException(status_code=400, detail="Franchise number already registered")

    driver_id = str(uuid.uuid4())
    qr_hash = generate_driver_qr_hash(driver_data.franchise_number, driver_data.name)
    
    new_driver = Driver(
        _id=driver_id,
        name=driver_data.name,
        franchise_number=driver_data.franchise_number,
        qr_hash=qr_hash,
        is_active=True,
        updated_at=datetime.utcnow()
    )
    
    await db["drivers"].insert_one(new_driver.model_dump(by_alias=True))
    return new_driver

@router.get("/", response_model=list[Driver])
async def get_all_drivers():
    """(Admin Only) Fetches the registry of all drivers."""
    db = db_client.db
    cursor = db["drivers"].find({})
    return await cursor.to_list(length=1000)


# ---------------------------------------------------------
# DRIVER APP ENDPOINTS (For the Tricycle Driver's phone)
# ---------------------------------------------------------

@router.post("/login", response_model=Token)
async def login_driver(login_data: DriverLogin):
    """Authenticates a Driver using their LGU-issued QR Code."""
    db = db_client.db
    
    driver = await db["drivers"].find_one({"qr_hash": login_data.qr_hash})
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid driver QR code. Please contact the LGU."
        )
        
    if not driver.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This franchise is currently inactive or suspended."
        )
    
    # Issue a JWT specifically tagged with the "driver" role
    access_token = create_access_token(data={
        "sub": driver["franchise_number"], 
        "role": "driver"
    })
    
    return {"access_token": access_token, "token_type": "bearer"}