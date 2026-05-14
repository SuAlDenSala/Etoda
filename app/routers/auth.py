from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import Token
from app.models.domain import ExternalApp
from app.core.security import create_access_token, verify_password, get_api_key_hash, get_current_admin
from app.database.mongodb import db_client
import uuid
import secrets
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Unified Authentication & API Keys"])

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = db_client.db
    
    # 1. Check if LGU Admin
    admin_user = await db["admins"].find_one({"username": form_data.username})
    if admin_user and verify_password(form_data.password, admin_user["hashed_password"]):
        access_token = create_access_token(data={"sub": form_data.username, "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    # 2. Check if Commuter
    commuter_user = await db["commuters"].find_one({"email": form_data.username})
    if commuter_user and verify_password(form_data.password, commuter_user["hashed_password"]):
        access_token = create_access_token(data={"sub": form_data.username, "role": "commuter"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username/email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# CHANGED: Now a GET request that requires an active admin login session
@router.get("/generate-api-key", status_code=status.HTTP_200_OK)
async def generate_app_api_key(current_admin: dict = Depends(get_current_admin)):
    """Generates an API Key tied to the currently logged-in LGU Administrator."""
    db = db_client.db
    
    raw_api_key = secrets.token_urlsafe(32)
    key_hash = get_api_key_hash(raw_api_key)
    
    # Automatically name the app based on the logged-in admin's username
    admin_username = current_admin.get("username")
    app_name = f"{admin_username}'s Authorized External App"
    default_permissions = ["read_fares", "read_alerts"]
    
    new_app = ExternalApp(
        _id=str(uuid.uuid4()),
        app_name=app_name,
        api_key_hash=key_hash,
        permissions=default_permissions,
        created_at=datetime.utcnow()
    )
    
    await db["external_apps"].insert_one(new_app.model_dump(by_alias=True))
    
    return {
        "message": f"API Key successfully generated for {admin_username}. Please save it now.",
        "app_name": app_name,
        "api_key": raw_api_key,
        "permissions": default_permissions
    }