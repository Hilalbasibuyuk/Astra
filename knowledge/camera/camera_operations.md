# Observatory Camera Operations and Diagnostics

## Purpose

This document describes general operating concepts and troubleshooting procedures for astronomical imaging cameras. It provides diagnostic guidance for the ASTRA observatory intelligence platform.

## Camera Sensor Temperature

The sensor temperature affects detector behavior, image noise, and the stability of astronomical observations. Many scientific cameras use active cooling to maintain a target temperature.

An unexpected increase in sensor temperature may be associated with:

- Cooling system performance degradation.
- Insufficient ventilation or elevated ambient temperature.
- A change in the configured sensor temperature setpoint.
- Excessive heat transfer from surrounding equipment.
- Sensor temperature measurement or communication problems.

The expected operating temperature depends on the camera model, detector technology, and observing configuration. ASTRA should use equipment-specific documentation rather than assuming a universal target temperature.

## Exposure Time and Gain

Exposure time determines how long the detector collects light during an observation. Gain affects how the detector's signal is converted into digital values, according to the camera's implementation.

Changes in exposure time or gain can influence image brightness, noise characteristics, and the risk of saturation.

When image quality changes unexpectedly, inspect:

- Exposure time and gain settings.
- Sensor temperature and cooling status.
- Image saturation and underexposure indicators.
- The observing target and environmental conditions.
- Recent configuration changes.

Do not interpret a change in image brightness as evidence of hardware failure without checking the acquisition settings and environmental context.

## Image Quality Degradation

Image quality may be affected by several independent factors:

- Atmospheric seeing and turbulence.
- Cloud cover or changing transparency.
- Telescope focus and tracking accuracy.
- Camera temperature and detector noise.
- Exposure time, gain, and saturation.
- Optical contamination or alignment problems.

A decrease in an image-quality metric should be evaluated alongside relevant telescope, weather, and camera telemetry.

## Camera Diagnostic Procedure

When image quality degrades or sensor temperature increases:

1. Check the camera's current status and recent telemetry.
2. Compare sensor temperature with its normal baseline and documented operating limits.
3. Review exposure time, gain, and acquisition configuration.
4. Inspect weather and telescope tracking metrics.
5. Check camera alarms and manufacturer documentation.
6. Record the relevant measurements and escalate persistent faults to an authorized operator.

## Safety and Operational Boundaries

ASTRA provides diagnostic recommendations and decision support. It must not independently change camera settings, disable cooling protections, or override hardware interlocks without an explicitly authorized and validated control process.