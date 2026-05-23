from datetime import datetime
from app.database.mongodb import db_client

async def process_sync_push(queued_incidents: list):
    db = db_client.db
    if queued_incidents:
        reports_data = [report.model_dump() for report in queued_incidents]
        await db["incident_reports"].insert_many(reports_data)
    return len(queued_incidents)

async def fetch_sync_pull_data(last_sync_time: str):
    db = db_client.db
    last_sync_dt = datetime.fromisoformat(last_sync_time)
    
    drivers_cursor = db["drivers"].find({"updated_at": {"$gt": last_sync_dt}})
    drivers = await drivers_cursor.to_list(length=100)
    
    fares_cursor = db["fares"].find({"updated_at": {"$gt": last_sync_dt}})
    fares = await fares_cursor.to_list(length=100)
    
    # NEW: Fetch the community alerts
    alerts_cursor = db["alerts"].find({"updated_at": {"$gt": last_sync_dt}})
    alerts = await alerts_cursor.to_list(length=50)
    
    # Return 3 items instead of 2
    return drivers, fares, alerts