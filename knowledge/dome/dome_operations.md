# Observatory Dome Operations and Diagnostics

## Purpose

This document describes general concepts for monitoring and diagnosing an observatory dome. It supports ASTRA's analysis of dome telemetry and its assessment of possible operational anomalies.

## Dome Azimuth and Rotation

Dome azimuth represents the dome's angular orientation. Rotation speed describes how quickly its orientation changes.

Unexpected dome motion or a mismatch between the requested and measured orientation may be associated with:

- Increased mechanical friction.
- Motor or drive-system problems.
- Encoder or position-feedback faults.
- Communication delays.
- Incorrect motion commands or configuration.
- Environmental conditions affecting operation.

The interpretation of azimuth and rotation speed depends on the dome's control system and coordinate conventions.

## Dome Motor Temperature

An increase in dome motor temperature may indicate increased mechanical load, insufficient cooling, extended operation, or a motor-control problem.

Temperature should be evaluated using:

- The recent temperature trend.
- Motor current and rotation behavior, if available.
- The dome's operating state.
- The manufacturer's documented operating limits.
- Existing warnings and fault indicators.

A high temperature reading should not be assigned a definitive root cause without supporting evidence.

## Shutter State

The shutter state indicates whether the dome opening is closed, open, moving, or in another state defined by the control system.

The reported state should be checked against the requested state and the current operating procedure.

Unexpected shutter behavior may be associated with mechanical obstruction, drive-system faults, sensor problems, or communication failures.

ASTRA should distinguish between a commanded state and a measured state whenever both are available.

## Dome Motor Anomaly

Possible indicators of abnormal dome motor behavior include:

- Increasing motor temperature.
- Unexpected changes in rotation speed.
- Irregular or oscillating motion.
- A discrepancy between requested and measured azimuth.
- Repeated warnings or communication errors.

Multiple indicators can provide stronger diagnostic evidence than an isolated reading, but they do not necessarily establish a single root cause.

## Dome Diagnostic Procedure

When a dome anomaly is detected:

1. Retrieve the latest dome telemetry and recent history.
2. Inspect azimuth, rotation speed, motor temperature, and shutter state.
3. Check the current device status and any active alarms.
4. Compare measurements with the dome's documented operating limits.
5. Review telescope and weather conditions for relevant context.
6. Recommend an operator inspection if the anomaly persists or the available evidence is insufficient.

## Safety and Operational Boundaries

Dome movement and shutter operation can present physical and equipment risks. ASTRA must not issue movement commands, open or close the shutter, or bypass interlocks solely on the basis of an LLM-generated recommendation.

Any control action must pass through the approved control interface, equipment-specific safety checks, and the required operator-approval process.