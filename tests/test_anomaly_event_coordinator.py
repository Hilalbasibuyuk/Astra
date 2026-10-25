
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.postgres.connection import Base
from services.anomaly_detection.event_coordinator import (
    AnomalyEventCoordinator,
)
from services.events.models import Event


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_anomalous_sample_creates_an_event(db_session):
    coordinator = AnomalyEventCoordinator(db_session)

    event = coordinator.evaluate_sample(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        metric_name="motor_temperature",
        historical_values=[
            10.0,
            10.1,
            9.9,
            10.2,
            10.0,
        ],
        current_value=30.0,
        severity="high",
        summary="Telescope motor temperature is abnormal.",
        occurred_at=datetime.now(timezone.utc),
    )
    db_session.commit()

    assert event is not None
    assert event.id is not None
    assert event.source_id == "TCS-01"
    assert event.event_type == "motor_overheating"
    assert event.status == "open"
    assert event.occurrence_count == 1
    assert event.details["metric_name"] == "motor_temperature"
    assert event.details["current_value"] == 30.0


def test_normal_sample_does_not_create_an_event(db_session):
    coordinator = AnomalyEventCoordinator(db_session)

    event = coordinator.evaluate_sample(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        metric_name="motor_temperature",
        historical_values=[
            10.0,
            10.1,
            9.9,
            10.2,
            10.0,
        ],
        current_value=10.1,
        severity="high",
        summary="Telescope motor temperature is abnormal.",
    )
    db_session.commit()

    assert event is None
    assert db_session.query(Event).count() == 0


def test_anomaly_detection_uses_only_the_latest_prediction(
    db_session,
):
    coordinator = AnomalyEventCoordinator(db_session)

    # The last value is normal, even though history contains a spike.
    event = coordinator.evaluate_sample(
        source_type="telescope",
        source_id="TCS-01",
        event_type="motor_overheating",
        metric_name="motor_temperature",
        historical_values=[
            10.0,
            10.1,
            9.9,
            10.2,
            10.0,
            30.0,
        ],
        current_value=10.1,
        severity="high",
        summary="Telescope motor temperature is abnormal.",
    )

    db_session.commit()

    assert event is None
    assert db_session.query(Event).count() == 0
