from typing import Optional

from pydantic import BaseModel, Field


class ConversationRelevancyVerdict(BaseModel):
    verdict: str
    reason: Optional[str] = Field(default=None)


class ConversationRelevancyScoreReason(BaseModel):
    reason: str
