from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, model_validator


class AnalyticsFilterParams(BaseModel):
    agent_id: UUID | None = None
    tick_from: int | None = None
    tick_to: int | None = None
    zone_id: UUID | None = None
    event_type: str | None = None

    @model_validator(mode="after")
    def validate_tick_range(self) -> "AnalyticsFilterParams":
        if self.tick_from is not None and self.tick_from < 0:
            raise ValueError("tick_from must be non-negative")
        if self.tick_to is not None and self.tick_to < 0:
            raise ValueError("tick_to must be non-negative")
        if self.tick_from is not None and self.tick_to is not None and self.tick_from > self.tick_to:
            raise ValueError("tick_from must be less than or equal to tick_to")
        return self

    def as_query_params(self) -> dict[str, str | int]:
        params: dict[str, str | int] = {}
        if self.agent_id is not None:
            params["agent_id"] = str(self.agent_id)
        if self.tick_from is not None:
            params["tick_from"] = self.tick_from
        if self.tick_to is not None:
            params["tick_to"] = self.tick_to
        if self.zone_id is not None:
            params["zone_id"] = str(self.zone_id)
        if self.event_type:
            params["event_type"] = self.event_type
        return params
