from collections.abc import Sequence

import statistics


class ZScoreDetector:
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold

    def detect(
        self,
        values: Sequence[float],
    ) -> list[bool]:
        if len(values) < 2:
            return [False] * len(values)

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev == 0:
            return [False] * len(values)

        return [
            abs((value - mean) / stdev) > self.threshold
            for value in values
        ]

class RollingZScoreDetector:
    def __init__(
        self,
        window_size: int = 20,
        threshold: float = 3.0,
    ):
        self.window_size = window_size
        self.threshold = threshold

    def detect(
        self,
        values: Sequence[float],
    ) -> list[bool]:
        results: list[bool] = []

        for index, value in enumerate(values):
            start = max(0, index - self.window_size)

            window = list(values[start:index])

            if len(window) < 2:
                results.append(False)
                continue

            mean = statistics.mean(window)
            stdev = statistics.stdev(window)

            if stdev == 0:
                results.append(False)
                continue

            z_score = abs((value - mean) / stdev)

            results.append(z_score > self.threshold)

        return results