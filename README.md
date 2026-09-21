
**ASTRA** ->  Autonomous Scientific Telescope Reasoning Architecture


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