"""
Cue Correlation Analysis Module.

This module provides advanced correlation analysis capabilities for the
HA-MotionDirection integration, including statistical tracking, pattern
learning, and historical analysis of cue correlations.

Author: HA-MotionDirection Team
License: MIT
"""

import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from ..models.motion_event import MotionEvent
from ..models.sensor_node import SensorNode

if TYPE_CHECKING:
    from .hybrid_detector import CueEvent

_LOGGER = logging.getLogger(__name__)


@dataclass
class CorrelationStatistics:
    """Statistics for a specific motion-cue correlation pair."""
    
    motion_sensor_id: str
    cue_id: str
    total_correlations: int = 0
    successful_correlations: int = 0  # Where correlation led to correct direction
    avg_time_diff_ms: float = 0.0
    min_time_diff_ms: float = float('inf')
    max_time_diff_ms: float = 0.0
    avg_distance: float = 0.0
    confidence_score: float = 0.0
    last_seen: Optional[datetime] = None
    time_diffs: List[float] = field(default_factory=list)
    
    def update(self, time_diff_ms: float, distance: float, was_successful: bool = True):
        """Update statistics with a new correlation observation.
        
        Args:
            time_diff_ms: Time difference in milliseconds
            distance: Spatial distance
            was_successful: Whether the correlation led to correct prediction
        """
        self.total_correlations += 1
        if was_successful:
            self.successful_correlations += 1
        
        # Update time difference statistics
        self.time_diffs.append(time_diff_ms)
        if len(self.time_diffs) > 100:  # Keep last 100 observations
            self.time_diffs.pop(0)
        
        self.avg_time_diff_ms = sum(self.time_diffs) / len(self.time_diffs)
        self.min_time_diff_ms = min(self.min_time_diff_ms, time_diff_ms)
        self.max_time_diff_ms = max(self.max_time_diff_ms, time_diff_ms)
        
        # Update distance (running average)
        self.avg_distance = (
            (self.avg_distance * (self.total_correlations - 1) + distance)
            / self.total_correlations
        )
        
        # Update confidence score (success rate with recency bias)
        self.confidence_score = self.successful_correlations / self.total_correlations
        
        self.last_seen = datetime.now()
    
    def get_temporal_decay_factor(self, time_diff_ms: float, half_life_ms: float = 2000.0) -> float:
        """Calculate temporal decay factor based on time difference.
        
        Uses exponential decay: factor = e^(-λt) where λ = ln(2) / half_life
        
        Args:
            time_diff_ms: Time difference in milliseconds
            half_life_ms: Half-life for decay in milliseconds
        
        Returns:
            Decay factor between 0 and 1
        """
        decay_constant = math.log(2) / half_life_ms
        return math.exp(-decay_constant * time_diff_ms)
    
    def get_weighted_confidence(self, time_diff_ms: float) -> float:
        """Get confidence score weighted by temporal decay.
        
        Args:
            time_diff_ms: Current time difference
        
        Returns:
            Weighted confidence score
        """
        decay_factor = self.get_temporal_decay_factor(time_diff_ms)
        return self.confidence_score * decay_factor


@dataclass
class CorrelationPattern:
    """Identified correlation pattern."""
    
    pattern_type: str  # 'sequential', 'correlation', 'timing'
    motion_sensor_id: str
    cue_id: str
    description: str
    confidence: float
    occurrences: int
    avg_time_diff_ms: float
    suggested_hint: Optional[Dict] = None


class CueCorrelationAnalyzer:
    """Analyzes and tracks cue correlations over time.
    
    This class provides statistical analysis of cue correlations,
    pattern learning, and insights for improving detection accuracy.
    """
    
    def __init__(self):
        """Initialize the correlation analyzer."""
        self._stats: Dict[Tuple[str, str], CorrelationStatistics] = {}
        self._correlation_history: List[Tuple[datetime, str, str, float, float]] = []
        self._max_history_size = 10000
        
    def record_correlation(
        self,
        motion_event: MotionEvent,
        cue_event: "CueEvent",
        was_successful: bool = True,
    ) -> None:
        """Record a correlation observation.
        
        Args:
            motion_event: Motion event
            cue_event: Correlated cue event
            was_successful: Whether correlation led to correct prediction
        """
        motion_id = motion_event.sensor.entity_id
        cue_id = cue_event.cue.id
        
        # Calculate metrics
        time_diff_ms = abs(
            (cue_event.timestamp - motion_event.timestamp).total_seconds() * 1000
        )
        distance = self._calculate_distance(
            motion_event.sensor.position,
            cue_event.cue.position,
        )
        
        # Get or create statistics
        key = (motion_id, cue_id)
        if key not in self._stats:
            self._stats[key] = CorrelationStatistics(
                motion_sensor_id=motion_id,
                cue_id=cue_id,
            )
        
        # Update statistics
        self._stats[key].update(time_diff_ms, distance, was_successful)
        
        # Record in history
        self._correlation_history.append(
            (datetime.now(), motion_id, cue_id, time_diff_ms, distance)
        )
        
        # Prune history if needed
        if len(self._correlation_history) > self._max_history_size:
            self._correlation_history = self._correlation_history[-self._max_history_size:]
        
        _LOGGER.debug(
            "Recorded correlation: motion=%s, cue=%s, time_diff=%.0fms, distance=%.1f, success=%s",
            motion_id,
            cue_id,
            time_diff_ms,
            distance,
            was_successful,
        )
    
    def analyze_correlations(
        self,
        floorplan_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_correlation: float = 0.5,
    ) -> Dict:
        """Analyze correlations for a time period.
        
        Args:
            floorplan_id: Floorplan ID to analyze
            start_time: Start of analysis period
            end_time: End of analysis period
            min_correlation: Minimum confidence threshold
        
        Returns:
            Analysis results dictionary
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(days=7)
        if end_time is None:
            end_time = datetime.now()
        
        # Filter history by time period
        filtered_history = [
            entry for entry in self._correlation_history
            if start_time <= entry[0] <= end_time
        ]
        
        # Aggregate statistics
        results = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "total_correlations": len(filtered_history),
            "unique_pairs": len(self._stats),
            "high_confidence_pairs": [],
            "low_confidence_pairs": [],
            "temporal_patterns": [],
            "spatial_patterns": [],
        }
        
        # Analyze each correlation pair
        for key, stats in self._stats.items():
            if stats.confidence_score >= min_correlation:
                results["high_confidence_pairs"].append({
                    "motion_sensor": stats.motion_sensor_id,
                    "cue": stats.cue_id,
                    "confidence": round(stats.confidence_score, 3),
                    "total_occurrences": stats.total_correlations,
                    "avg_time_diff_ms": round(stats.avg_time_diff_ms, 1),
                    "avg_distance": round(stats.avg_distance, 1),
                })
            elif stats.total_correlations >= 5:  # Only report low confidence if enough data
                results["low_confidence_pairs"].append({
                    "motion_sensor": stats.motion_sensor_id,
                    "cue": stats.cue_id,
                    "confidence": round(stats.confidence_score, 3),
                    "total_occurrences": stats.total_correlations,
                    "suggestion": "Consider removing or reconfiguring this cue",
                })
        
        # Identify temporal patterns
        results["temporal_patterns"] = self._identify_temporal_patterns(filtered_history)
        
        # Identify spatial patterns
        results["spatial_patterns"] = self._identify_spatial_patterns()
        
        _LOGGER.info(
            "Correlation analysis completed: %d total, %d high confidence, %d low confidence",
            results["total_correlations"],
            len(results["high_confidence_pairs"]),
            len(results["low_confidence_pairs"]),
        )
        
        return results
    
    def learn_patterns(
        self,
        confidence_threshold: float = 0.75,
        min_occurrences: int = 10,
    ) -> List[CorrelationPattern]:
        """Learn correlation patterns from historical data.
        
        Args:
            confidence_threshold: Minimum confidence for pattern
            min_occurrences: Minimum occurrences to consider
        
        Returns:
            List of identified patterns
        """
        patterns = []
        
        for key, stats in self._stats.items():
            if (
                stats.confidence_score >= confidence_threshold
                and stats.total_correlations >= min_occurrences
            ):
                # Determine pattern type based on timing
                if stats.avg_time_diff_ms < 500:
                    pattern_type = "sequential"
                    description = f"Cue {stats.cue_id} consistently occurs within 500ms"
                elif stats.avg_time_diff_ms < 2000:
                    pattern_type = "correlation"
                    description = f"Cue {stats.cue_id} correlates within 2 seconds"
                else:
                    pattern_type = "timing"
                    description = f"Cue {stats.cue_id} shows consistent timing pattern"
                
                # Create suggested hint
                suggested_hint = {
                    "cue_id": stats.cue_id,
                    "correlation_window_ms": int(stats.max_time_diff_ms * 1.2),
                    "confidence": round(stats.confidence_score, 2),
                }
                
                pattern = CorrelationPattern(
                    pattern_type=pattern_type,
                    motion_sensor_id=stats.motion_sensor_id,
                    cue_id=stats.cue_id,
                    description=description,
                    confidence=stats.confidence_score,
                    occurrences=stats.total_correlations,
                    avg_time_diff_ms=stats.avg_time_diff_ms,
                    suggested_hint=suggested_hint,
                )
                patterns.append(pattern)
                
                _LOGGER.debug(
                    "Learned pattern: %s for motion=%s, cue=%s (confidence=%.2f)",
                    pattern_type,
                    stats.motion_sensor_id,
                    stats.cue_id,
                    stats.confidence_score,
                )
        
        return patterns
    
    def get_correlation_confidence(
        self,
        motion_sensor_id: str,
        cue_id: str,
        time_diff_ms: float,
    ) -> float:
        """Get confidence score for a specific correlation.
        
        Args:
            motion_sensor_id: Motion sensor ID
            cue_id: Cue ID
            time_diff_ms: Time difference in milliseconds
        
        Returns:
            Confidence score (0-1)
        """
        key = (motion_sensor_id, cue_id)
        if key not in self._stats:
            return 0.5  # Default confidence for unknown pairs
        
        stats = self._stats[key]
        return stats.get_weighted_confidence(time_diff_ms)
    
    def get_statistics(
        self,
        motion_sensor_id: Optional[str] = None,
        cue_id: Optional[str] = None,
    ) -> List[CorrelationStatistics]:
        """Get correlation statistics.
        
        Args:
            motion_sensor_id: Filter by motion sensor
            cue_id: Filter by cue
        
        Returns:
            List of statistics
        """
        results = []
        for key, stats in self._stats.items():
            if motion_sensor_id and stats.motion_sensor_id != motion_sensor_id:
                continue
            if cue_id and stats.cue_id != cue_id:
                continue
            results.append(stats)
        return results
    
    def _identify_temporal_patterns(
        self,
        history: List[Tuple[datetime, str, str, float, float]],
    ) -> List[Dict]:
        """Identify temporal patterns in correlation history.
        
        Args:
            history: Filtered correlation history
        
        Returns:
            List of temporal patterns
        """
        patterns = []
        
        # Group by hour of day
        hourly_counts = defaultdict(int)
        for entry in history:
            hour = entry[0].hour
            hourly_counts[hour] += 1
        
        # Find peak hours
        if hourly_counts:
            max_count = max(hourly_counts.values())
            peak_hours = [
                hour for hour, count in hourly_counts.items()
                if count >= max_count * 0.8
            ]
            
            if peak_hours:
                patterns.append({
                    "type": "time_of_day",
                    "description": f"Peak correlation activity during hours: {peak_hours}",
                    "hours": peak_hours,
                    "occurrences": sum(hourly_counts[h] for h in peak_hours),
                })
        
        return patterns
    
    def _identify_spatial_patterns(self) -> List[Dict]:
        """Identify spatial patterns in correlations.
        
        Returns:
            List of spatial patterns
        """
        patterns = []
        
        # Group by average distance ranges
        distance_groups = {
            "very_close": [],  # < 50
            "close": [],  # 50-100
            "moderate": [],  # 100-200
            "distant": [],  # > 200
        }
        
        for key, stats in self._stats.items():
            if stats.avg_distance < 50:
                group = "very_close"
            elif stats.avg_distance < 100:
                group = "close"
            elif stats.avg_distance < 200:
                group = "moderate"
            else:
                group = "distant"
            
            distance_groups[group].append((stats, key))
        
        # Report dominant patterns
        for group, items in distance_groups.items():
            if len(items) >= 3:  # At least 3 correlations in this distance range
                patterns.append({
                    "type": "spatial_clustering",
                    "distance_range": group,
                    "count": len(items),
                    "description": f"{len(items)} correlation pairs in {group} distance range",
                })
        
        return patterns
    
    @staticmethod
    def _calculate_distance(
        pos1: Tuple[float, float],
        pos2: Tuple[float, float],
    ) -> float:
        """Calculate Euclidean distance between two positions.
        
        Args:
            pos1: First position
            pos2: Second position
        
        Returns:
            Distance
        """
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
