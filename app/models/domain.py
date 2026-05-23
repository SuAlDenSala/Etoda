from pydantic import BaseModel, Field
from datetime import datetime

class Driver(BaseModel):
    id: str = Field(alias="_id")
    name: str
    franchise_number: str
    qr_hash: str
    is_active: bool
    updated_at: datetime

class FareMatrix(BaseModel):
    id: str = Field(alias="_id")
    origin: str
    destination: str
    regular_fare: float
    student_pwd_fare: float
    updated_at: datetime

class IncidentReport(BaseModel):
    report_id: str
    driver_qr_hash: str
    issue_description: str
    timestamp: datetime

class CommunityAlert(BaseModel):
    id: str = Field(alias="_id")
    title: str
    message: str
    is_critical: bool
    updated_at: datetime

# --- NEW MODELS BELOW ---

class Commuter(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    hashed_password: str
    discount_status: str  # e.g., "Regular", "Student", "PWD", "Senior"
    is_verified: bool
    created_at: datetime

class ExternalApp(BaseModel):
    id: str = Field(alias="_id")
    app_name: str         # e.g., "MSU-TCTO Campus Portal"
    api_key_hash: str     # Hashed for security, just like passwords
    permissions: list     # e.g., ["read_fares", "read_alerts"]
    created_at: datetime