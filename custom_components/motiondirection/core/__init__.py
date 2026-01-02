"""Core detection and processing modules."""
from .event_collector import EventCollector
from .time_window_correlator import TimeWindowCorrelator
from .vector_calculator import VectorCalculator

__all__ = [
    "EventCollector",
    "TimeWindowCorrelator",
    "VectorCalculator",
]
