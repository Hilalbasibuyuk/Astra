# Telescope Tracking and Motor Diagnostics

## Purpose

This document describes common diagnostic checks for telescope tracking errors and motor temperature increases. It provides general troubleshooting guidance for the ASTRA observatory intelligence platform.

## Telescope Tracking Error

Tracking error represents the difference between the desired telescope position and its measured position. The meaning and units of this metric depend on the telescope control system.

A sustained increase in tracking error may be associated with:

- Mechanical friction or increased resistance in the drive system.
- Motor current or temperature rising above its usual operating range.
- Incorrect tracking parameters or calibration.
- Encoder or position-feedback problems.
- Communication delays between the control system and the telescope.
- Wind or other environmental disturbances.

A single high reading does not necessarily indicate a persistent fault. Check the recent history, compare related metrics, and verify the sensor's validity before drawing a conclusion.

## Motor Temperature

Motor temperature should be evaluated against the equipment manufacturer's operating limits and the telescope's established baseline.

A gradual temperature increase may be associated with:

- Increased mechanical load.
- Insufficient cooling or ventilation.
- Extended operation under demanding conditions.
- Drive-system friction.
- Electrical or motor-control problems.

Do not use a generic temperature threshold as a universal safety limit. The applicable limit must come from the specific equipment documentation.

## Motor Current and Temperature Together

An increase in both motor current and temperature may be consistent with increased mechanical load or resistance. However, this relationship alone is not sufficient to identify a root cause.

Recommended diagnostic sequence:

1. Inspect the recent temperature and current time series.
2. Compare the measurements with their normal operating baselines.
3. Check tracking error and telescope status over the same time interval.
4. Review alarms and relevant equipment documentation.
5. Escalate to an authorized operator or maintenance procedure when necessary.

## Safety

ASTRA provides diagnostic assistance. It must not override telescope-controller interlocks, manufacturer limits, or approved observatory procedures. Any physical intervention must follow the observatory's authorized safety process.