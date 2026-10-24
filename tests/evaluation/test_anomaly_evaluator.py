
import pytest

from anomaly_evaluator import (
    calculate_detection_delay,
)


def test_detection_delay_is_zero_when_anomaly_is_detected_immediately():
    labels = [False, False, True, True]
    predictions = [False, False, True, False]

    delay = calculate_detection_delay(labels, predictions)

    assert delay == 0


def test_detection_delay_counts_samples_until_first_detection():
    labels = [False, False, True, True, True]
    predictions = [False, False, False, False, True]

    delay = calculate_detection_delay(labels, predictions)

    assert delay == 2


def test_detection_delay_is_none_when_anomaly_is_never_detected():
    labels = [False, False, True, True]
    predictions = [False, False, False, False]

    delay = calculate_detection_delay(labels, predictions)

    assert delay is None


def test_detection_delay_is_none_when_no_anomaly_exists():
    labels = [False, False, False]
    predictions = [False, True, False]

    delay = calculate_detection_delay(labels, predictions)

    assert delay is None


def test_detection_delay_rejects_different_length_inputs():
    labels = [False, True]
    predictions = [False]

    with pytest.raises(ValueError):
        calculate_detection_delay(labels, predictions)
