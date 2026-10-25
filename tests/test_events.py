
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.postgres.connection import Base
from services.events.models import Event
from services.events.service import EventManagementService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_event_is_created_with_default_values(
    db_session: Session,
):
    event = Event(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        summary="Telescope motor temperature is abnormal.",
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.id is not None
    assert event.severity == "medium"
    assert event.status == "open"
    assert event.occurrence_count == 1
    assert event.resolved_at is None
    # SQLite does not preserve timezone information when reading
    # DateTime(timezone=True) values back from the database.
    # Normalize SQLite's naive datetimes to UTC for this test.
    assert event.first_seen.replace(
        tzinfo=timezone.utc
    ).utcoffset() == timezone.utc.utcoffset(event.first_seen)

    assert event.last_seen.replace(
        tzinfo=timezone.utc
    ).utcoffset() == timezone.utc.utcoffset(event.last_seen)

    assert event.created_at.replace(
        tzinfo=timezone.utc
    ).utcoffset() == timezone.utc.utcoffset(event.created_at)
    assert event.details == {}


def test_event_stores_source_and_diagnostic_details(
    db_session: Session,
):
    event = Event(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        severity="high",
        summary="Motor temperature exceeded its configured limit.",
        details={
            "motor_temperature": 82.5,
            "threshold": 80.0,
        },
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.source_type == "telescope"
    assert event.source_id == "TCS-01"
    assert event.severity == "high"
    assert event.details["motor_temperature"] == 82.5


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("severity", "urgent"),
        ("status", "pending"),
        ("occurrence_count", 0),
    ],
)
def test_event_rejects_invalid_values(
    db_session: Session,
    field: str,
    value: object,
):
    event_data = {
        "source_type": "telescope",
        "source_id": "TCS-01",
        "event_type": "motor_overheating",
        "summary": "Test event.",
    }
    event_data[field] = value

    event = Event(**event_data)

    db_session.add(event)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_event_can_be_marked_as_resolved(
    db_session: Session,
):
    resolved_at = datetime.now(timezone.utc)

    event = Event(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        summary="Motor temperature returned to normal.",
        status="resolved",
        resolved_at=resolved_at,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.status == "resolved"
    assert event.resolved_at is not None



def test_repeated_occurrences_update_the_same_open_event(db_session):
    service = EventManagementService(db_session)

    first = service.record_occurrence(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        severity="high",
        summary="Telescope motor temperature is abnormal.",
        details={"motor_temperature": 82.5},
    )
    db_session.commit()

    second = service.record_occurrence(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        severity="critical",
        summary="Telescope motor temperature remains abnormal.",
        details={"motor_temperature": 91.2},
    )
    db_session.commit()

    events = db_session.query(Event).all()

    assert len(events) == 1
    assert first.id == second.id
    assert second.occurrence_count == 2
    assert second.severity == "critical"
    assert second.details == {"motor_temperature": 91.2}
    assert second.status == "open"


def test_resolved_event_is_not_reused(db_session):
    service = EventManagementService(db_session)

    first = service.record_occurrence(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        severity="high",
        summary="Motor temperature is abnormal.",
    )
    db_session.commit()

    resolved = service.resolve_event(first.id)
    db_session.commit()

    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None

    second = service.record_occurrence(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        severity="high",
        summary="Motor temperature is abnormal again.",
    )
    db_session.commit()

    events = (
        db_session.query(Event)
        .order_by(Event.id)
        .all()
    )

    assert len(events) == 2
    assert second.id != first.id
    assert events[0].status == "resolved"
    assert events[1].status == "open"
    assert events[1].occurrence_count == 1


def test_resolving_an_event_is_idempotent(db_session):
    service = EventManagementService(db_session)

    event = service.record_occurrence(
        source_type="telescope",
        source_id="TCS-01",
        event_type="tracking_error",
        severity="medium",
        summary="Telescope tracking error detected.",
    )
    db_session.commit()

    first_resolution = service.resolve_event(event.id)
    original_resolved_at = first_resolution.resolved_at
    db_session.commit()

    second_resolution = service.resolve_event(event.id)

    assert second_resolution.status == "resolved"
    assert normalize_utc(second_resolution.resolved_at) == normalize_utc(
    original_resolved_at
)


def test_resolving_a_missing_event_raises_lookup_error(db_session):
    service = EventManagementService(db_session)

    with pytest.raises(LookupError, match="was not found"):
        service.resolve_event(999999)

def normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)