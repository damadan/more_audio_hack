from typing import List, Literal, Optional
from pydantic import BaseModel, Field

EventType = Literal["partial", "final", "segment_final", "info", "error"]


class Word(BaseModel):
    w: str
    start: float
    end: float
    conf: float


class TranscriptEvent(BaseModel):
    type: EventType
    session_id: str
    ts_start: float
    ts_end: float
    text: str
    words: List[Word] = Field(default_factory=list)
    stability: Optional[float] = None
    revised_text: Optional[str] = None
    diff_from_online: Optional[str] = None


class StartMessage(BaseModel):
    type: Literal["start"]
    lang: Literal["ru", "en"] = "ru"
    profile: Literal["online", "hybrid"] = "hybrid"
    sample_rate: int = 16000
    hotwords: List[str] = Field(default_factory=list)


class StopMessage(BaseModel):
    type: Literal["stop"]


class CreateSessionRequest(BaseModel):
    lang: Literal["ru", "en"] = "ru"
    profile: Literal["online", "hybrid"] = "hybrid"
    hotwords: List[str] = Field(default_factory=list)


class CreateSessionResponse(BaseModel):
    session_id: str


class TranscriptResponse(BaseModel):
    session_id: str
    text: str
    segments: List[TranscriptEvent]
