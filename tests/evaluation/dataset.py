
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    question: str
    expected_source_paths: tuple[str, ...]
    reference_answer: str


EVALUATION_DATASET = [
    # Telescope diagnostics
    EvaluationCase(
        case_id="telescope-tracking-001",
        question="What can cause a sustained increase in telescope tracking error?",
        expected_source_paths=(
            "telescope/tracking_and_motor.md",
        ),
        reference_answer=(
            "Possible causes include mechanical friction, motor issues, "
            "incorrect tracking parameters, encoder or feedback problems, "
            "communication delays, and environmental disturbances."
        ),
    ),
    EvaluationCase(
        case_id="telescope-motor-002",
        question="What can a gradual increase in telescope motor temperature indicate?",
        expected_source_paths=(
            "telescope/tracking_and_motor.md",
        ),
        reference_answer=(
            "It may indicate increased mechanical load, insufficient cooling, "
            "demanding operation, drive-system friction, or electrical or "
            "motor-control problems. The exact cause requires more evidence."
        ),
    ),
    EvaluationCase(
        case_id="telescope-current-003",
        question="What might simultaneous increases in telescope motor current and temperature suggest?",
        expected_source_paths=(
            "telescope/tracking_and_motor.md",
        ),
        reference_answer=(
            "The combination may be consistent with increased mechanical "
            "load or resistance, but it does not establish a definitive "
            "root cause."
        ),
    ),

    # Camera diagnostics
    EvaluationCase(
        case_id="camera-temperature-001",
        question="What can an unexpected increase in camera sensor temperature indicate?",
        expected_source_paths=(
            "camera/camera_operations.md",
        ),
        reference_answer=(
            "Possible explanations include cooling degradation, insufficient "
            "ventilation, elevated ambient temperature, a changed temperature "
            "setpoint, heat transfer from nearby equipment, or measurement "
            "and communication problems."
        ),
    ),
    EvaluationCase(
        case_id="camera-exposure-002",
        question="Which settings should be checked when image brightness changes unexpectedly?",
        expected_source_paths=(
            "camera/camera_operations.md",
        ),
        reference_answer=(
            "Check exposure time, gain, sensor temperature, cooling status, "
            "saturation and underexposure indicators, observing conditions, "
            "and recent configuration changes."
        ),
    ),
    EvaluationCase(
        case_id="camera-quality-003",
        question="What factors can degrade astronomical image quality?",
        expected_source_paths=(
            "camera/camera_operations.md",
        ),
        reference_answer=(
            "Possible factors include atmospheric seeing, cloud cover, focus, "
            "tracking, camera temperature, detector noise, exposure and gain "
            "settings, saturation, optical contamination, and alignment."
        ),
    ),

    # Dome diagnostics
    EvaluationCase(
        case_id="dome-azimuth-001",
        question="What can cause a mismatch between requested and measured dome azimuth?",
        expected_source_paths=(
            "dome/dome_operations.md",
        ),
        reference_answer=(
            "Possible causes include mechanical friction, motor or drive "
            "problems, encoder or position-feedback faults, communication "
            "delays, incorrect commands, or configuration issues."
        ),
    ),
    EvaluationCase(
        case_id="dome-temperature-002",
        question="What should be checked when dome motor temperature increases?",
        expected_source_paths=(
            "dome/dome_operations.md",
        ),
        reference_answer=(
            "Review the temperature trend, motor current and rotation behavior "
            "if available, operating state, documented equipment limits, "
            "warnings, and fault indicators."
        ),
    ),
    EvaluationCase(
        case_id="dome-shutter-003",
        question="How should an unexpected dome shutter state be investigated?",
        expected_source_paths=(
            "dome/dome_operations.md",
        ),
        reference_answer=(
            "Compare the reported shutter state with the requested state and "
            "operating procedure. Potential causes include obstruction, drive "
            "faults, sensor problems, or communication failures."
        ),
    ),

    # Weather and observing conditions
    EvaluationCase(
        case_id="weather-clouds-001",
        question="How can increasing cloud cover affect astronomical observations?",
        expected_source_paths=(
            "weather/observation_conditions.md",
        ),
        reference_answer=(
            "Increasing cloud cover may reduce transparency, intermittently "
            "obstruct the target, deteriorate observing conditions, and "
            "require reassessment of the observation plan."
        ),
    ),
    EvaluationCase(
        case_id="weather-wind-002",
        question="How should a sudden increase in wind speed be assessed?",
        expected_source_paths=(
            "weather/observation_conditions.md",
        ),
        reference_answer=(
            "Assess the equipment manufacturer's limits, site safety "
            "procedures, current telescope and dome state, and the rate "
            "and duration of the wind change."
        ),
    ),
    EvaluationCase(
        case_id="weather-humidity-003",
        question="What operational concern may be associated with high humidity?",
        expected_source_paths=(
            "weather/observation_conditions.md",
        ),
        reference_answer=(
            "High humidity may increase condensation risk under some "
            "conditions. It should be interpreted alongside dew-point "
            "monitoring, equipment specifications, and local procedures."
        ),
    ),
    EvaluationCase(
        case_id="cross-domain-image-quality-001",
        question="What should be investigated when astronomical image quality deteriorates?",
        expected_source_paths=(
            "camera/camera_operations.md",
            "weather/observation_conditions.md",
            "telescope/tracking_and_motor.md",
        ),
        reference_answer=(
            "Investigate camera configuration and temperature, atmospheric "
            "seeing and cloud conditions, telescope focus and tracking, "
            "and relevant telemetry. A single image-quality change does "
            "not identify one definitive cause."
        ),
    ),
]
