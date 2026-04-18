from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Signal(BaseModel):
    source: str  # "job_postings" | "news" | "funding" | "reviews"
    title: str
    body: str
    impact: Literal["high", "medium", "low"]
    date: str
    company: str
    tags: list[str] = Field(default_factory=list)


class Company(BaseModel):
    name: str
    competitors: list[str]
    accounts: list[str]
