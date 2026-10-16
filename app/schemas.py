from pydantic import BaseModel, Field
from typing import Optional

class TimelineRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=30000)
    reference_date: Optional[str] = Field(default=None, description="YYYY-MM-DD; defaults to today")

class TimelineEvent(BaseModel):
    event: str
    date: Optional[str] = None
    evidence: str
    confidence: str = "medium"
    notes: Optional[str] = None

class TimelineResponse(BaseModel):
    reference_date: str
    summary: str
    events: list[TimelineEvent]
    warnings: list[str] = []
