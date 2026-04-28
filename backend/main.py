import sqlite3
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vibe Trip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trips.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _serialize_trip(row: sqlite3.Row) -> dict:
    trip = dict(row)

    if isinstance(trip.get("tags"), str):
        try:
            trip["tags"] = json.loads(trip["tags"])
        except json.JSONDecodeError:
            trip["tags"] = []
    else:
        trip["tags"] = trip.get("tags") or []

    for key in ("latitude", "longitude"):
        if trip.get(key) is not None:
            trip[key] = float(trip[key])

    if trip.get("is_featured") is not None:
        trip["is_featured"] = bool(trip["is_featured"])

    return trip


def get_trips(tag: str | None = None) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if tag:
            query = "SELECT * FROM trips WHERE tags LIKE ?"
            cursor.execute(query, (f'%"{tag}"%',))
        else:
            query = "SELECT * FROM trips"
            cursor.execute(query)

        rows = cursor.fetchall()
        return [_serialize_trip(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/trips")
def list_trips(tag: str | None = Query(None)) -> dict:
    trips = get_trips(tag=tag)
    return {"items": trips, "total": len(trips)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
