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

import pytest

from rift.runtime import CommandRejectedError, ControlPipeline
from rift.safety import SafetyDecision, SafetyStatus
from rift.telemetry import TelemetryRecord


@dataclass(frozen=True)
class Measurement:
    position: float


@dataclass(frozen=True)
class State:
    position: float


@dataclass(frozen=True)
class Command:
    velocity: float


class ExampleSimulation:
    def __init__(self) -> None:
        self._time = 0.0
        self._position = 0.0
        self._velocity = 0.0
        self.seed: int | None = None
        self.closed = False

    @property
    def time(self) -> float:
        return self._time

    def reset(
        self,
        seed: int | None = None,
    ) -> Measurement:
        self.seed = seed
        self._time = 0.0
        self._position = 2.0
        self._velocity = 0.0
        self.closed = False
        return Measurement(position=self._position)

    def apply(self, command: Command) -> None:
        self._velocity = command.velocity

    def step(self, duration: float) -> Measurement:
        self._position += self._velocity * duration
        self._time += duration
        return Measurement(position=self._position)

    def close(self) -> None:
        self.closed = True


class ExampleEstimator:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def update(
        self,
        measurement: Measurement,
        dt: float,
    ) -> State:
        assert dt > 0.0
        return State(position=measurement.position)


class ExampleController:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def compute(
        self,
        state: State,
        dt: float,
    ) -> Command:
        assert dt > 0.0
        return Command(velocity=-state.position)


class LimitingSafety:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1

    def evaluate(
        self,
        command: Command,
        *,
        timestamp: float,
    ) -> tuple[Command | None, SafetyDecision]:
        assert timestamp >= 0.0

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


class RejectingSafety:
    def reset(self) -> None:
        pass

    def evaluate(
        self,
        command: Command,
        *,
        timestamp: float,
    ) -> tuple[Command | None, SafetyDecision]:
        del command, timestamp

        return (
            None,
            SafetyDecision(
                status=SafetyStatus.REJECTED,
                reason="Command rejected for test.",
            ),
        )


class MemoryTelemetry:
    def __init__(self) -> None:
        self.records: list[TelemetryRecord] = []
        self.closed = False

    def publish(self, record: TelemetryRecord) -> None:
        self.records.append(record)

    def close(self) -> None:
        self.closed = True


def build_pipeline(
    *,
    safety: LimitingSafety | RejectingSafety | None = None,
    telemetry: MemoryTelemetry | None = None,
) -> tuple[
    ControlPipeline[Measurement, State, Command],
    ExampleSimulation,
    ExampleEstimator,
    ExampleController,
]:
    simulation = ExampleSimulation()
    estimator = ExampleEstimator()
    controller = ExampleController()

    pipeline = ControlPipeline(
        simulation=simulation,
        estimator=estimator,
        controller=controller,
        safety=safety or LimitingSafety(),
        telemetry=telemetry,
        period=0.1,
    )

    return pipeline, simulation, estimator, controller


def test_pipeline_rejects_invalid_period():
    pipeline, simulation, estimator, controller = build_pipeline()
    del pipeline

    with pytest.raises(
        ValueError,
        match="Control period must be positive",
    ):
        ControlPipeline(
            simulation=simulation,
            estimator=estimator,
            controller=controller,
            safety=LimitingSafety(),
            period=0.0,
        )


def test_pipeline_requires_start_before_step():
    pipeline, _, _, _ = build_pipeline()

    with pytest.raises(
        RuntimeError,
        match="Control pipeline is not running",
    ):
        pipeline.step()


def test_pipeline_starts_components_and_uses_seed():
    pipeline, simulation, estimator, controller = build_pipeline()

    measurement = pipeline.start(seed=17)

    assert pipeline.running
    assert pipeline.time == 0.0
    assert pipeline.period == 0.1
    assert measurement == Measurement(position=2.0)
    assert simulation.seed == 17
    assert estimator.reset_count == 1
    assert controller.reset_count == 1


def test_pipeline_executes_estimation_control_safety_and_simulation():
    telemetry = MemoryTelemetry()
    pipeline, _, _, _ = build_pipeline(telemetry=telemetry)

    pipeline.start(seed=3)
    result = pipeline.step()

    assert result.time == pytest.approx(0.1)
    assert result.state == State(position=2.0)
    assert result.requested_command == Command(velocity=-2.0)
    assert result.applied_command == Command(velocity=-1.0)
    assert result.measurement.position == pytest.approx(1.9)
    assert result.safety.status is SafetyStatus.MODIFIED

    assert telemetry.records == [
        TelemetryRecord(
            timestamp=0.1,
            values={"safety_status": "modified"},
        ),
    ]


def test_pipeline_uses_latest_measurement_on_next_cycle():
    pipeline, _, _, _ = build_pipeline()

    pipeline.start()
    first = pipeline.step()
    second = pipeline.step()

    assert first.state == State(position=2.0)
    assert second.state.position == pytest.approx(1.9)
    assert second.measurement.position == pytest.approx(1.8)
    assert second.time == pytest.approx(0.2)


def test_pipeline_raises_when_safety_rejects_command():
    pipeline, _, _, _ = build_pipeline(
        safety=RejectingSafety(),
    )

    pipeline.start()

    with pytest.raises(
        CommandRejectedError,
        match="Command rejected for test",
    ):
        pipeline.step()


def test_pipeline_cannot_start_twice():
    pipeline, _, _, _ = build_pipeline()

    pipeline.start()

    with pytest.raises(
        RuntimeError,
        match="already running",
    ):
        pipeline.start()


def test_pipeline_stop_is_idempotent():
    telemetry = MemoryTelemetry()
    pipeline, simulation, _, _ = build_pipeline(
        telemetry=telemetry,
    )

    pipeline.start()
    pipeline.stop()
    pipeline.stop()

    assert not pipeline.running
    assert simulation.closed
    assert telemetry.closed


def test_pipeline_context_manager_releases_resources():
    telemetry = MemoryTelemetry()
    pipeline, simulation, _, _ = build_pipeline(
        telemetry=telemetry,
    )

    with pipeline as active_pipeline:
        assert active_pipeline.running
        active_pipeline.step()

    assert not pipeline.running
    assert simulation.closed
    assert telemetry.closed
