from services.anomaly_detection.detectors import (
    RollingZScoreDetector,
    ZScoreDetector,
)
from services.anomaly_detection.evaluation import (
    evaluate_predictions,
)


def test_zscore_detector_detects_outlier():
    detector = ZScoreDetector(threshold=2.0)

    values = [
        10.0,
        10.1,
        9.9,
        10.2,
        10.0,
        50.0,
    ]

    results = detector.detect(values)

    assert len(results) == len(values)
    assert results[-1] is True


def test_zscore_detector_returns_false_for_normal_data():
    detector = ZScoreDetector(threshold=3.0)

    values = [
        10.0,
        10.1,
        9.9,
        10.2,
        10.0,
    ]

    results = detector.detect(values)

    assert not any(results)


def test_rolling_zscore_detector():
    detector = RollingZScoreDetector(
        window_size=4,
        threshold=2.0,
    )

    values = [
        10.0,
        10.1,
        9.9,
        10.2,
        10.0,
        30.0,
    ]

    results = detector.detect(values)

    assert len(results) == len(values)
    assert results[-1] is True


def test_evaluation_metrics():
    ground_truth = [
        False,
        False,
        True,
        True,
        False,
    ]

    predictions = [
        False,
        True,
        True,
        False,
        False,
    ]

    metrics = evaluate_predictions(
        ground_truth,
        predictions,
    )

    assert metrics.true_positive == 1
    assert metrics.true_negative == 2
    assert metrics.false_positive == 1
    assert metrics.false_negative == 1

    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1_score == 0.5