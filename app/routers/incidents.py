from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["Incident Reports"])

@router.post("/")
async def report_incident():
    """Queue and record local transit incident reports."""
    return {"status": "received"}