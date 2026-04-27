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


def get_trips(tag: str | None = None) -> list[dict]:
    """Return trips, optionally filtered by tag slug.

    This default implementation returns an empty list.  In production,
    replace it with real database queries.  Tests monkeypatch this
    function to avoid requiring a live database.
    """
    return []


@app.get("/api/trips")
def list_trips(tag: str | None = Query(None)) -> dict:
    trips = get_trips(tag=tag)
    return {"items": trips, "total": len(trips)}
