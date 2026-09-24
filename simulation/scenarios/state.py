from dataclasses import dataclass

from simulation.scenarios.models import ScenarioType


@dataclass
class ScenarioState:
    scenario: ScenarioType = ScenarioType.NORMAL
    step_count: int = 0
    active: bool = False

    def start(self, scenario: ScenarioType) -> None:
        self.scenario = scenario
        self.step_count = 0
        self.active = scenario != ScenarioType.NORMAL

    def stop(self) -> None:
        self.scenario = ScenarioType.NORMAL
        self.step_count = 0
        self.active = False

    def next_step(self) -> int:
        self.step_count += 1
        return self.step_count