from typing import Literal

from pydantic import BaseModel, Field


class Signal(BaseModel):
    source: str
    title: str
    body: str
    impact: Literal["high", "medium", "low"]
    date: str
    company: str = ""
    tags: list[str] = Field(default_factory=list)


class Action(BaseModel):
    text: str
    urgency: Literal["this-week", "this-month"]


class RankedAccount(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    reason: str
    signals: list[Signal]


class SetupRequest(BaseModel):
    company: str
    competitors: list[str]
    accounts: list[str]


class SetupResponse(BaseModel):
    session_id: str


class BriefRequest(BaseModel):
    session_id: str
    competitor: str


class BriefResponse(BaseModel):
    signals: list[Signal]
    summary: str
    actions: list[Action]


class PrioritizeRequest(BaseModel):
    session_id: str


class PrioritizeResponse(BaseModel):
    accounts: list[RankedAccount]


class BattlecardRequest(BaseModel):
    session_id: str
    competitor: str


class BattlecardResponse(BaseModel):
    markdown: str


class SignalsResponse(BaseModel):
    signals: list[Signal]
