# Copyright 2026 Mezael Docoy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass

from rift.control import Controller
from rift.estimation import Estimator
from rift.safety import (
    SafetyDecision,
    SafetyStatus,
    SafetySupervisor,
)
from rift.simulation import SimulationBackend
from rift.telemetry import TelemetryRecord, TelemetrySink


@dataclass(frozen=True)
class Measurement:
    position: float


@dataclass(frozen=True)
class State:
    position: float


@dataclass(frozen=True)
class Command:
    velocity: float


class EstimatorImpl:
    def reset(self) -> None:
        pass

    def update(
        self,
        measurement: Measurement,
        dt: float,
    ) -> State:
        del dt
        return State(position=measurement.position)


class ControllerImpl:
    def reset(self) -> None:
        pass

    def compute(
        self,
        state: State,
        dt: float,
    ) -> Command:
        del dt
        return Command(velocity=-state.position)


class SafetyImpl:
    def reset(self) -> None:
        pass

    def evaluate(
        self,
        command: Command,
        *,
        timestamp: float,
    ) -> tuple[Command | None, SafetyDecision]:
        del timestamp

        velocity = max(-1.0, min(1.0, command.velocity))

        status = (
            SafetyStatus.ACCEPTED
            if velocity == command.velocity
            else SafetyStatus.MODIFIED
        )

        return (
            Command(velocity=velocity),
            SafetyDecision(status=status),
        )


class SimulationImpl:
    def __init__(self) -> None:
        self._time = 0.0
        self._position = 2.0
        self._velocity = 0.0

    @property
    def time(self) -> float:
        return self._time

    def reset(
        self,
        seed: int | None = None,
    ) -> Measurement:
        del seed
        self._time = 0.0
        self._position = 2.0
        self._velocity = 0.0
        return Measurement(position=self._position)

    def apply(self, command: Command) -> None:
        self._velocity = command.velocity

    def step(self, duration: float) -> Measurement:
        self._position += self._velocity * duration
        self._time += duration
        return Measurement(position=self._position)

    def close(self) -> None:
        pass


class TelemetryImpl:
    def __init__(self) -> None:
        self.records: list[TelemetryRecord] = []

    def publish(self, record: TelemetryRecord) -> None:
        self.records.append(record)

    def close(self) -> None:
        pass


def test_application_defined_types_flow_through_core_interfaces():
    estimator = EstimatorImpl()
    controller = ControllerImpl()
    safety = SafetyImpl()
    simulation = SimulationImpl()
    telemetry = TelemetryImpl()

    assert isinstance(estimator, Estimator)
    assert isinstance(controller, Controller)
    assert isinstance(safety, SafetySupervisor)
    assert isinstance(simulation, SimulationBackend)
    assert isinstance(telemetry, TelemetrySink)

    measurement = simulation.reset(seed=7)
    state = estimator.update(measurement, dt=0.1)
    requested_command = controller.compute(state, dt=0.1)
    safe_command, decision = safety.evaluate(
        requested_command,
        timestamp=simulation.time,
    )

    assert decision.status is SafetyStatus.MODIFIED
    assert safe_command is not None

    simulation.apply(safe_command)
    measurement = simulation.step(0.1)

    telemetry.publish(
        TelemetryRecord(
            timestamp=simulation.time,
            values={
                "position": measurement.position,
                "velocity": safe_command.velocity,
                "safety_status": decision.status.value,
            },
        )
    )

    assert measurement.position == 1.9
    assert telemetry.records[0].values == {
        "position": 1.9,
        "velocity": -1.0,
        "safety_status": "modified",
    }
