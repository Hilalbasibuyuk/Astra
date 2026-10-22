from typing import Any

from services.anomaly_detection.service import AnomalyDetectionService
from services.rag.generator import RAGAnswerService
from services.telemetry.query_service import TelemetryQueryService


TELESCOPE_METRICS = (
    "tracking_error",
    "motor_temperature",
    "motor_current",
    "vibration",
)


class TelescopeDiagnosticsService:
    """Combines telescope telemetry, anomaly detection and RAG."""

    def __init__(
        self,
        telemetry_service: TelemetryQueryService,
        anomaly_service: AnomalyDetectionService | None = None,
        rag_service: RAGAnswerService | None = None,
    ) -> None:
        self.telemetry_service = telemetry_service
        self.anomaly_service = (
            anomaly_service or AnomalyDetectionService()
        )
        self.rag_service = rag_service

    def analyze(
        self,
        telescope_id: str,
        history_limit: int = 100,
        rag_limit: int = 5,
    ) -> dict[str, Any]:
        # QuestDB returns history newest-first. Detectors must process
        # observations chronologically.
        history = self.telemetry_service.get_telescope_history(
            telescope_id=telescope_id,
            limit=history_limit,
        )

        if not history:
            raise LookupError(
                f"No telemetry found for telescope '{telescope_id}'."
            )

        chronological = list(reversed(history))
        latest = history[0]

        metrics: dict[str, Any] = {}
        anomaly_details: list[dict[str, Any]] = []

        for metric in TELESCOPE_METRICS:
            values = [
                float(row[metric])
                for row in chronological
                if row.get(metric) is not None
            ]

            # Keep the indices aligned with the actual observations.
            rows = [
                row
                for row in chronological
                if row.get(metric) is not None
            ]

            zscore_flags = self.anomaly_service.detect_zscore(values)
            rolling_flags = (
                self.anomaly_service.detect_rolling_zscore(values)
            )

            latest_value = latest.get(metric)
            latest_is_anomalous = False

            if latest_value is not None and rows:
                latest_timestamp = latest["timestamp"]

                latest_index = next(
                    (
                        index
                        for index in range(len(rows) - 1, -1, -1)
                        if rows[index]["timestamp"] == latest_timestamp
                    ),
                    None,
                )

                if latest_index is not None:
                    latest_is_anomalous = (
                        zscore_flags[latest_index]
                        or rolling_flags[latest_index]
                    )

            detected_count = sum(
                1
                for z_flag, rolling_flag in zip(
                    zscore_flags, rolling_flags
                )
                if z_flag or rolling_flag
            )

            metrics[metric] = {
                "latest_value": latest_value,
                "latest_is_anomalous": latest_is_anomalous,
                "detected_points": detected_count,
                "observations_used": len(values),
            }

            if latest_is_anomalous:
                anomaly_details.append(
                    {
                        "metric": metric,
                        "latest_value": latest_value,
                        "zscore_detected": bool(
                            zscore_flags[latest_index]
                        ),
                        "rolling_zscore_detected": bool(
                            rolling_flags[latest_index]
                        ),
                    }
                )

        explanation = None
        sources: list[dict[str, Any]] = []

        if anomaly_details and self.rag_service is not None:
            anomaly_summary = "; ".join(
                f"{item['metric']}={item['latest_value']} "
                f"(Z-score={item['zscore_detected']}, "
                f"Rolling Z-score="
                f"{item['rolling_zscore_detected']})"
                for item in anomaly_details
            )

            query = (
                "Analyze the following telescope telemetry observations. "
                "Explain what the documented operating procedures say "
                "about these detected anomalies. Distinguish observed "
                "measurements from possible explanations. Do not claim "
                "a root cause unless the sources establish it.\n\n"
                f"Telescope ID: {telescope_id}\n"
                f"Latest status: {latest.get('status')}\n"
                f"Latest timestamp: {latest.get('timestamp')}\n"
                f"Latest detected anomalies: {anomaly_summary}"
            )

            rag_result = self.rag_service.answer(
                query=query,
                limit=rag_limit,
            )

            explanation = rag_result["answer"]
            sources = rag_result["sources"]

        return {
            "telescope_id": telescope_id,
            "latest_timestamp": latest["timestamp"],
            "latest_status": latest.get("status"),
            "observations_used": len(chronological),
            "latest_telemetry": latest,
            "metrics": metrics,
            "anomalies": anomaly_details,
            "is_anomalous": bool(anomaly_details),
            "explanation": explanation,
            "sources": sources,
        }