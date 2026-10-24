
import json
from dataclasses import asdict

from services.anomaly_detection.detectors import (
    RollingZScoreDetector,
    ZScoreDetector,
)
from services.anomaly_detection.evaluation import (
    evaluate_predictions,
)
from simulation.anomalies.injector import AnomalyInjector

from simulation.anomalies.models import AnomalyPattern, AnomalyProfile
from simulation.anomalies.injector import AnomalyInjector
from simulation.anomalies.profiles import (
    DOME_MOTOR_ANOMALY,
    TELESCOPE_MOTOR_OVERHEATING,
)


def build_normal_values(length: int) -> list[float]:
    """Create deterministic baseline measurements without anomalies."""
    offsets = [-0.2, -0.1, 0.0, 0.1, 0.2, 0.0, -0.1, 0.1]

    return [
        10.0 + offsets[index % len(offsets)]
        for index in range(length)
    ]


def build_spike_scenario() -> tuple[list[float], list[bool]]:
    """Create a normal series with one sudden spike."""
    values = build_normal_values(100)
    labels = [False] * len(values)

    anomaly_index = 60
    values[anomaly_index] = 14.0
    labels[anomaly_index] = True

    return values, labels



def build_gradual_drift_scenario() -> tuple[list[float], list[bool]]:
    """Build a gradual drift using ASTRA's actual anomaly profile."""
    baseline = build_normal_values(50)
    profile = TELESCOPE_MOTOR_OVERHEATING
    injector = AnomalyInjector()

    offsets = [-0.2, -0.1, 0.0, 0.1, 0.2, 0.0, -0.1, 0.1]
    drift_values: list[float] = []

    for step in range(1, profile.duration_steps + 1):
        normal_value = 10.0 + offsets[(49 + step) % len(offsets)]

        injected_value = injector.apply(
            value=normal_value,
            step=step,
            profile=profile,
        )

        drift_values.append(injected_value)

    values = baseline + drift_values
    labels = (
        [False] * len(baseline)
        + [True] * len(drift_values)
    )

    return values, labels



def evaluate_scenario(
    values: list[float],
    labels: list[bool],
) -> dict[str, dict[str, int | float]]:
    detectors = {
        "zscore": ZScoreDetector(threshold=3.0),
        "rolling_zscore": RollingZScoreDetector(
            window_size=20,
            threshold=3.0,
        ),
    }

    results: dict[str, dict[str, int | float]] = {}

    for name, detector in detectors.items():
        predictions = detector.detect(values)
        metrics = evaluate_predictions(labels, predictions)
        results[name] = asdict(metrics)

    return results





def main() -> None:
    spike_values, spike_labels = build_spike_scenario()
    drift_values, drift_labels = build_gradual_drift_scenario()

    profiles = {
        "sudden_spike": build_sudden_spike_profile(),
        "motor_overheating": TELESCOPE_MOTOR_OVERHEATING,
        "dome_oscillation": DOME_MOTOR_ANOMALY,
    }

    multi_scenario_results = {}

    for scenario_name, profile in profiles.items():
        values, labels = build_injected_scenario(profile)

        scenario_result = {
            "baseline_detectors": evaluate_scenario(values, labels),
        }

        if scenario_name != "sudden_spike":
            scenario_result["rolling_parameter_sweep"] = (
                run_rolling_parameter_sweep(values, labels)
            )

        multi_scenario_results[scenario_name] = scenario_result

    report = {
        "experiment": "ASTRA anomaly detector evaluation",
        "note": (
            "Deterministic synthetic data. "
            "Results do not represent real observatory performance. "
            "Parameter sweeps are exploratory, not independent validation."
        ),
        "baseline": {
            "sudden_spike": evaluate_scenario(
                spike_values,
                spike_labels,
            ),
            "gradual_drift": evaluate_scenario(
                drift_values,
                drift_labels,
            ),
        },
        "gradual_drift_parameter_sweep": run_rolling_parameter_sweep(
            drift_values,
            drift_labels,
        ),
        "multi_scenario_results": multi_scenario_results,
    }

    print(json.dumps(report, indent=2))




def run_rolling_parameter_sweep(
    values: list[float],
    labels: list[bool],
) -> list[dict[str, int | float]]:
    results: list[dict[str, int | float]] = []

    for window_size in [5, 10, 20]:
        for threshold in [1.5, 2.0, 2.5, 3.0]:
            detector = RollingZScoreDetector(
                window_size=window_size,
                threshold=threshold,
            )

            predictions = detector.detect(values)
            metrics = evaluate_predictions(labels, predictions)

            results.append(
                {
                    "window_size": window_size,
                    "threshold": threshold,
                    "true_positive": metrics.true_positive,
                    "false_positive": metrics.false_positive,
                    "false_negative": metrics.false_negative,
                    "precision": round(metrics.precision, 4),
                    "recall": round(metrics.recall, 4),
                    "f1_score": round(metrics.f1_score, 4),
                    "false_positive_rate": round(
                        metrics.false_positive_rate,
                        4,
                    ),
                }
            )

    return results


def build_injected_scenario(
    profile: AnomalyProfile,
    baseline_length: int = 50,
) -> tuple[list[float], list[bool]]:
    baseline = build_normal_values(baseline_length)
    injector = AnomalyInjector()

    offsets = [-0.2, -0.1, 0.0, 0.1, 0.2, 0.0, -0.1, 0.1]
    injected_values: list[float] = []

    for step in range(1, profile.duration_steps + 1):
        normal_value = 10.0 + offsets[
            (baseline_length + step - 1) % len(offsets)
        ]

        injected_values.append(
            injector.apply(
                value=normal_value,
                step=step,
                profile=profile,
            )
        )

    values = baseline + injected_values
    labels = (
        [False] * baseline_length
        + [True] * len(injected_values)
    )

    return values, labels


def build_sudden_spike_profile() -> AnomalyProfile:
    return AnomalyProfile(
        name="evaluation_sudden_spike",
        pattern=AnomalyPattern.SUDDEN_SPIKE,
        magnitude=4.0,
        duration_steps=1,
        severity="high",
        direction=1.0,
    )


if __name__ == "__main__":
    main()
