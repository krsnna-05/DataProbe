from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db.connection import get_connection
from app.schema.introspector import get_schema
from app.schema.models import DatabaseSchema
from app.schema.tool import get_table_schema, list_tables

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
async def root():
    return {"message": "DataProbe Server Running"}


@app.get("/health")
async def health():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded",
                "service": "dataprobe-server",
                "database": {"status": "unavailable"},
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ) from error

    return {
        "status": "ok",
        "service": "dataprobe-server",
        "database": {"status": "ok"},
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/schema", response_model=DatabaseSchema)
def schemas():
    return get_schema()


@app.get("/schema/tables")
def tables():
    return {"tables": list_tables()}


@app.get("/schema/tables/{table_name}")
def table_schema(table_name: str):
    try:
        return get_table_schema(table_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
