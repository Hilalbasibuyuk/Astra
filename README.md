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
ASTRA is a digital-twin-based autonomous observatory intelligence platform that continuously perceives telescope, environmental, and scientific data, detects anomalies and data-quality issues, dynamically replans observations, and uses tool-augmented multi-agent AI to provide explainable technical and scientific decision support.

---

                    ASTRONOMER
                        │
                        ▼
                 Natural Language
                        │
                        ▼
                 ┌─────────────┐
                 │    ASTRA    │
                 │ Supervisor  │
                 └──────┬──────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
    HEALTH           PLANNER          SCIENCE
    AGENT             AGENT            AGENT
       │                │                │
       ▼                ▼                ▼
    Anomaly          Scheduling       Data Quality
    Prediction       Replanning       Image Analysis
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                     RAG/MCP
                        │
                        ▼
                 Knowledge Base
                        │
                        ▼
                  DIGITAL TWIN
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
           Telescope   Dome    Weather
              │         │         │
              └─────────┼─────────┘
                        ▼
                  TELEMETRY
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           QuestDB            PostgreSQL
