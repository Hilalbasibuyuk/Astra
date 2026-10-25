
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.postgres.connection import get_db
from services.events.models import Event
from services.events.schemas import EventResponse
from services.events.service import EventManagementService


router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)


@router.get("", response_model=list[EventResponse])
def list_events(
    status: Literal["open", "resolved"] | None = None,
    source_type: str | None = Query(default=None, min_length=1, max_length=50),
    source_id: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Event]:
    """List events with optional filters and pagination."""
    statement = select(Event)

    if status is not None:
        statement = statement.where(Event.status == status)

    if source_type is not None:
        statement = statement.where(Event.source_type == source_type)

    if source_id is not None:
        statement = statement.where(Event.source_id == source_id)

    statement = (
        statement
        .order_by(Event.last_seen.desc(), Event.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> Event:
    """Return the details of a single event."""
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} was not found.",
        )

    return event


@router.post("/{event_id}/resolve", response_model=EventResponse)
def resolve_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> Event:
    """Resolve an event and persist the change."""
    service = EventManagementService(db)

    try:
        event = service.resolve_event(event_id)
        db.commit()
        db.refresh(event)
        return event
    except LookupError as exc:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise
