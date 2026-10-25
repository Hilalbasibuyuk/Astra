
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.events.models import Event, utc_now


def _as_utc(value: datetime) -> datetime:
    """Normalize a datetime to timezone-aware UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


class EventManagementService:
    """Manage the lifecycle of persistent observatory events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def record_occurrence(
        self,
        *,
        source_type: str,
        source_id: str,
        event_type: str,
        severity: str,
        summary: str,
        details: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> Event:
        """Create an event or update an existing open event."""
        timestamp = _as_utc(occurred_at or utc_now())

        statement = (
            select(Event)
            .where(
                Event.source_type == source_type,
                Event.source_id == source_id,
                Event.event_type == event_type,
                Event.status == "open",
            )
            .order_by(Event.last_seen.desc(), Event.id.desc())
            .limit(1)
        )

        event = self.db.scalar(statement)

        if event is None:
            event = Event(
                source_type=source_type,
                source_id=source_id,
                event_type=event_type,
                severity=severity,
                status="open",
                summary=summary,
                details=details or {},
                first_seen=timestamp,
                last_seen=timestamp,
                occurrence_count=1,
            )
            self.db.add(event)
        else:
            previous_last_seen = _as_utc(event.last_seen)

            event.severity = severity
            event.summary = summary
            event.last_seen = max(previous_last_seen, timestamp)
            event.occurrence_count += 1
            event.details = details or {}

        # Assign generated database values without committing.
        self.db.flush()
        return event

    def resolve_event(
        self,
        event_id: int,
        *,
        resolved_at: datetime | None = None,
    ) -> Event:
        """Resolve an event while preserving its history."""
        event = self.db.get(Event, event_id)

        if event is None:
            raise LookupError(f"Event {event_id} was not found.")

        if event.status == "resolved":
            return event

        event.status = "resolved"
        event.resolved_at = _as_utc(resolved_at or utc_now())

        self.db.flush()
        return event
