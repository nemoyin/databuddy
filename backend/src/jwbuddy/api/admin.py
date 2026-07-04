from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header

from jwbuddy.data.connection import db_manager
from jwbuddy.security.audit import audit_logger

router = APIRouter(prefix="/admin", tags=["admin"])


async def verify_admin_key(x_admin_key: str = Header("")):
    from jwbuddy.config import settings
    if settings.admin_api_key and x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")


class DataSourceCreate(BaseModel):
    name: str
    url: str


@router.post("/datasources", dependencies=[Depends(verify_admin_key)])
async def add_datasource(data: DataSourceCreate):
    try:
        await db_manager.connect(data.name, data.url)
        audit_logger.log(action="datasource_add", detail=data.name)
        return {"status": "ok", "name": data.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/datasources", dependencies=[Depends(verify_admin_key)])
async def list_datasources():
    return {"datasources": db_manager.list_connections()}


@router.get("/audit", dependencies=[Depends(verify_admin_key)])
async def get_audit_log(limit: int = 100, user: str | None = None, action: str | None = None):
    return {
        "logs": audit_logger.query(limit=limit, user=user, action=action)
    }
