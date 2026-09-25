from collections.abc import Sequence

from services.anomaly_detection.detectors import (
    RollingZScoreDetector,
    ZScoreDetector,
)


class AnomalyDetectionService:
    def __init__(
        self,
        zscore_detector: ZScoreDetector | None = None,
        rolling_detector: RollingZScoreDetector | None = None,
    ):
        self.zscore_detector = (
            zscore_detector
            or ZScoreDetector()
        )

        self.rolling_detector = (
            rolling_detector
            or RollingZScoreDetector()
        )

    def detect_zscore(
        self,
        values: Sequence[float],
    ) -> list[bool]:
        return self.zscore_detector.detect(values)

    def detect_rolling_zscore(
        self,
        values: Sequence[float],
    ) -> list[bool]:
        return self.rolling_detector.detect(values)