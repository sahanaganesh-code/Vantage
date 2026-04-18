"""Data layer: normalized competitive signals from multiple sources."""

from .models import Company, Signal
from .processors.signal_processor import (
    get_signals_for_company,
    get_signals_for_competitor,
)

__all__ = [
    "Company",
    "Signal",
    "get_signals_for_company",
    "get_signals_for_competitor",
]
