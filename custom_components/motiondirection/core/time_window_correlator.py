"""Time window correlation for motion events."""
import logging
from datetime import datetime
from typing import List

from ..models import MotionEvent, MotionSequence

_LOGGER = logging.getLogger(__name__)


class TimeWindowCorrelator:
    """Correlates motion events within configurable time windows.
    
    Uses a sliding window approach to group temporally related motion events
    into sequences. Events within the time window are considered part of the
    same motion sequence.
    
    Algorithm (see Appendix A.2):
    1. Sort events by timestamp
    2. Start new sequence with first event
    3. For each subsequent event:
       - If within window of last event: add to sequence
       - Else: start new sequence
    4. Filter sequences with < 2 events
    
    Attributes:
        default_window_size: Default time window in milliseconds
        min_window_size: Minimum allowed window size
        max_window_size: Maximum allowed window size
    """
    
    DEFAULT_WINDOW_SIZE = 5000  # milliseconds
    MIN_WINDOW_SIZE = 500
    MAX_WINDOW_SIZE = 30000
    
    def __init__(self, default_window_size: int = DEFAULT_WINDOW_SIZE) -> None:
        """Initialize correlator.
        
        Args:
            default_window_size: Default time window in milliseconds
        
        Raises:
            ValueError: If window size is outside valid range
        """
        if not self.MIN_WINDOW_SIZE <= default_window_size <= self.MAX_WINDOW_SIZE:
            raise ValueError(
                f"Window size must be between {self.MIN_WINDOW_SIZE} "
                f"and {self.MAX_WINDOW_SIZE}ms"
            )
        
        self.default_window_size = default_window_size
        
        _LOGGER.info(
            "TimeWindowCorrelator initialized with window_size=%dms",
            default_window_size,
        )
    
    def correlate_events(
        self,
        events: List[MotionEvent],
        window_size: int | None = None,
    ) -> List[MotionSequence]:
        """Groups related motion events based on temporal proximity.
        
        Args:
            events: List of motion events to correlate
            window_size: Time window in milliseconds (None uses default)
        
        Returns:
            List of motion sequences where events are temporally related
        
        Raises:
            ValueError: If window_size is outside valid range
        """
        if window_size is None:
            window_size = self.default_window_size
        
        if not self.MIN_WINDOW_SIZE <= window_size <= self.MAX_WINDOW_SIZE:
            raise ValueError(
                f"Window size must be between {self.MIN_WINDOW_SIZE} "
                f"and {self.MAX_WINDOW_SIZE}ms"
            )
        
        if not events:
            _LOGGER.debug("No events to correlate")
            return []
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        sequences: List[List[MotionEvent]] = []
        current_sequence: List[MotionEvent] = []
        
        for event in sorted_events:
            if not current_sequence:
                # Start new sequence
                current_sequence.append(event)
            else:
                # Check if within window
                time_diff_ms = self._calculate_time_diff_ms(
                    current_sequence[-1].timestamp,
                    event.timestamp,
                )
                
                if time_diff_ms <= window_size:
                    # Add to current sequence
                    current_sequence.append(event)
                else:
                    # Save current sequence and start new one
                    if len(current_sequence) >= 2:
                        sequences.append(current_sequence)
                    current_sequence = [event]
        
        # Add final sequence if it has at least 2 events
        if len(current_sequence) >= 2:
            sequences.append(current_sequence)
        
        # Create MotionSequence objects
        motion_sequences = [
            MotionSequence(events=seq)
            for seq in sequences
        ]
        
        _LOGGER.debug(
            "Correlated %d events into %d sequences (window=%dms)",
            len(events),
            len(motion_sequences),
            window_size,
        )
        
        return motion_sequences
    
    @staticmethod
    def _calculate_time_diff_ms(
        timestamp1: datetime,
        timestamp2: datetime,
    ) -> float:
        """Calculate time difference in milliseconds.
        
        Args:
            timestamp1: Earlier timestamp
            timestamp2: Later timestamp
        
        Returns:
            Time difference in milliseconds
        """
        time_diff = (timestamp2 - timestamp1).total_seconds() * 1000
        return abs(time_diff)
    
    def set_default_window_size(self, window_size: int) -> None:
        """Update default window size.
        
        Args:
            window_size: New default window size in milliseconds
        
        Raises:
            ValueError: If window size is outside valid range
        """
        if not self.MIN_WINDOW_SIZE <= window_size <= self.MAX_WINDOW_SIZE:
            raise ValueError(
                f"Window size must be between {self.MIN_WINDOW_SIZE} "
                f"and {self.MAX_WINDOW_SIZE}ms"
            )
        
        old_size = self.default_window_size
        self.default_window_size = window_size
        
        _LOGGER.info(
            "Default window size changed: %dms -> %dms",
            old_size,
            window_size,
        )
    
    @staticmethod
    def estimate_optimal_window(events: List[MotionEvent]) -> int:
        """Estimate optimal window size based on event timing patterns.
        
        Analyzes historical events to suggest an appropriate window size
        that captures most related motions while avoiding false correlations.
        
        Args:
            events: Historical motion events
        
        Returns:
            Suggested window size in milliseconds
        """
        if len(events) < 3:
            return TimeWindowCorrelator.DEFAULT_WINDOW_SIZE
        
        # Calculate time differences between consecutive events
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        time_diffs = []
        
        for i in range(1, len(sorted_events)):
            diff_ms = (
                sorted_events[i].timestamp - sorted_events[i - 1].timestamp
            ).total_seconds() * 1000
            time_diffs.append(diff_ms)
        
        if not time_diffs:
            return TimeWindowCorrelator.DEFAULT_WINDOW_SIZE
        
        # Use 75th percentile as optimal window
        # (captures most related events without excessive correlation)
        sorted_diffs = sorted(time_diffs)
        percentile_75_idx = int(len(sorted_diffs) * 0.75)
        optimal_window = int(sorted_diffs[percentile_75_idx])
        
        # Clamp to valid range
        optimal_window = max(
            TimeWindowCorrelator.MIN_WINDOW_SIZE,
            min(optimal_window, TimeWindowCorrelator.MAX_WINDOW_SIZE),
        )
        
        _LOGGER.info(
            "Estimated optimal window size: %dms (from %d events)",
            optimal_window,
            len(events),
        )
        
        return optimal_window
