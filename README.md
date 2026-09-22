# ASTRA

Astronomical Sensor Telemetry & Real-time Analytics platform.

## Project Structure

```
astra/
├── apps/api/            # REST / WebSocket API layer
├── services/
│   ├── telemetry/       # Telemetry ingestion & streaming
│   └── anomaly/         # Anomaly detection service
├── simulation/
│   ├── telescope/       # Telescope simulator
│   ├── camera/          # Camera simulator
│   ├── weather/         # Weather condition simulator
│   └── dome/            # Dome control simulator
├── database/
│   ├── postgres/        # Relational schema & migrations
│   └── questdb/         # Time-series schema & queries
├── tests/               # Integration & unit tests
├── infrastructure/
│   └── docker/          # Dockerfiles & compose overrides
└── docs/                # Architecture & API documentation
```

## Quick Start

```bash
cp .env.example .env
docker-compose up -d
```