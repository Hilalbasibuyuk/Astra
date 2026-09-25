import csv
from pathlib import Path
from typing import Iterable

from services.telemetry.models import (
    TelescopeTelemetry,
    CameraTelemetry,
    WeatherTelemetry,
    DomeTelemetry,
)
from services.anomaly_detection.models import AnomalyLabel


class DatasetGenerator:
    """Exports simulated telemetry and anomaly labels to CSV files."""

    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_telescope(
        self,
        records: Iterable[TelescopeTelemetry],
    ) -> Path:
        return self._export(
            records,
            self.output_dir / "telescope_telemetry.csv",
        )

    def export_camera(
        self,
        records: Iterable[CameraTelemetry],
    ) -> Path:
        return self._export(
            records,
            self.output_dir / "camera_telemetry.csv",
        )

    def export_weather(
        self,
        records: Iterable[WeatherTelemetry],
    ) -> Path:
        return self._export(
            records,
            self.output_dir / "weather_telemetry.csv",
        )

    def export_dome(
        self,
        records: Iterable[DomeTelemetry],
    ) -> Path:
        return self._export(
            records,
            self.output_dir / "dome_telemetry.csv",
        )

    def export_labels(
        self,
        records: Iterable[AnomalyLabel],
    ) -> Path:
        return self._export(
            records,
            self.output_dir / "anomaly_labels.csv",
        )

    @staticmethod
    def _export(records: Iterable, path: Path) -> Path:
        records = list(records)

        if not records:
            raise ValueError("Cannot export an empty dataset.")

        rows = [
            record.model_dump(mode="json")
            for record in records
        ]

        fieldnames = list(rows[0].keys())

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(rows)

        return path