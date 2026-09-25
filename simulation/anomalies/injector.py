import math

from simulation.anomalies.models import (
    AnomalyPattern,
    AnomalyProfile,
)


class AnomalyInjector:
    def apply(
        self,
        value: float,
        step: int,
        profile: AnomalyProfile,
    ) -> float:

        if step <= 0:
            return value

        if step > profile.duration_steps:
            return value

        direction = profile.direction

        if profile.pattern == AnomalyPattern.SUDDEN_SPIKE:
            return value + (
                direction * profile.magnitude
            )

        if profile.pattern == AnomalyPattern.GRADUAL_DRIFT:
            progress = step / profile.duration_steps

            return value + (
                direction
                * profile.magnitude
                * progress
            )

        if profile.pattern == AnomalyPattern.STUCK_SENSOR:
            return value

        if profile.pattern == AnomalyPattern.OSCILLATION:
            return value + (
                direction
                * profile.magnitude
                * math.sin(step)
            )

        return value