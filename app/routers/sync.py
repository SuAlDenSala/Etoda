from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import SyncPushPayload, SyncPullResponse
from app.services.sync_service import process_sync_push, fetch_sync_pull_data

router = APIRouter(prefix="/sync", tags=["Offline-First Synchronization"])

@router.post("/push")
async def push_offline_data(payload: SyncPushPayload):
    synced_items = await process_sync_push(payload.queued_incidents)
    return {
        "status": "success", 
        "synced_items": synced_items,
        "message": "Offline data successfully written to central DB."
    }

@router.get("/pull", response_model=SyncPullResponse)
async def pull_server_updates(last_sync_time: str):
    # Unpack 3 variables to match the service
    drivers, fares, alerts = await fetch_sync_pull_data(last_sync_time)
    
    return SyncPullResponse(
        server_timestamp=datetime.utcnow().isoformat(),
        updated_drivers=drivers,
        updated_fares=fares,
        updated_alerts=alerts  # NEW: Added to satisfy the Pydantic schema
    )