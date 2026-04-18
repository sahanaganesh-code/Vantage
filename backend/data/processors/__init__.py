"""Aggregation and ranking of competitive signals."""

from .signal_processor import (
    get_signals_for_company,
    get_signals_for_competitor,
)

__all__ = ["get_signals_for_company", "get_signals_for_competitor"]
