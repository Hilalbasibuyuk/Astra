
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


EventStatus = Literal["open", "resolved"]
EventSeverity = Literal["low", "medium", "high", "critical"]


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: str
    source_id: str
    event_type: str
    severity: EventSeverity
    status: EventStatus
    summary: str
    details: dict[str, Any]
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    resolved_at: datetime | None
    created_at: datetime
