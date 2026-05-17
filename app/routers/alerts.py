from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["Community Alerts"])

@router.get("/")
async def get_alerts():
    """Fetch active traffic and road closure alerts for Bongao."""
    return {"alerts": []}