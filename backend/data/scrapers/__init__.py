"""Source-specific collectors that normalize raw inputs into `Signal` models."""

from .funding import get_funding_signals
from .jobs import get_job_signals
from .news import get_news_signals

__all__ = ["get_funding_signals", "get_job_signals", "get_news_signals"]
