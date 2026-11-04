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

"""Application-neutral control pipeline implementation."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from rift.control import Controller
from rift.estimation import Estimator
from rift.safety import SafetyDecision, SafetySupervisor
from rift.simulation import SimulationBackend
from rift.telemetry import TelemetryRecord, TelemetrySink


MeasurementT = TypeVar("MeasurementT")
StateT = TypeVar("StateT")
CommandT = TypeVar("CommandT")


class CommandRejectedError(RuntimeError):
    """Raised when the safety supervisor rejects a command."""


@dataclass(frozen=True)
class ControlCycleResult(
    Generic[MeasurementT, StateT, CommandT]
):
    """Result produced by one control-pipeline cycle."""

    time: float
    measurement: MeasurementT
    state: StateT
    requested_command: CommandT
    applied_command: CommandT
    safety: SafetyDecision


class ControlPipeline(Generic[MeasurementT, StateT, CommandT]):
    """Execute estimation, control, safety, and simulation as one cycle."""

    def __init__(
        self,
        *,
        simulation: SimulationBackend[CommandT, MeasurementT],
        estimator: Estimator[MeasurementT, StateT],
        controller: Controller[StateT, CommandT],
        safety: SafetySupervisor[CommandT],
        period: float,
        telemetry: TelemetrySink | None = None,
    ) -> None:
        if period <= 0.0:
            raise ValueError("Control period must be positive.")

        self._simulation = simulation
        self._estimator = estimator
        self._controller = controller
        self._safety = safety
        self._period = period
        self._telemetry = telemetry
        self._measurement: MeasurementT | None = None
        self._running = False

    @property
    def time(self) -> float:
        """Return the current simulation time."""

        return self._simulation.time

    @property
    def running(self) -> bool:
        """Return whether the pipeline is active."""

        return self._running

    @property
    def period(self) -> float:
        """Return the configured control period in seconds."""

        return self._period

    def start(self, *, seed: int | None = None) -> MeasurementT:
        """Reset all components and start the pipeline."""

        if self._running:
            raise RuntimeError("Control pipeline is already running.")

        self._estimator.reset()
        self._controller.reset()
        self._safety.reset()

        self._measurement = self._simulation.reset(seed=seed)
        self._running = True

        return self._measurement

    def step(
        self,
    ) -> ControlCycleResult[MeasurementT, StateT, CommandT]:
        """Execute one complete control cycle."""

        if not self._running:
            raise RuntimeError("Control pipeline is not running.")

        if self._measurement is None:
            raise RuntimeError(
                "Control pipeline has no current measurement."
            )

        state = self._estimator.update(
            self._measurement,
            self._period,
        )
        requested_command = self._controller.compute(
            state,
            self._period,
        )
        applied_command, decision = self._safety.evaluate(
            requested_command,
            timestamp=self._simulation.time,
        )

        if applied_command is None:
            raise CommandRejectedError(
                decision.reason or "Safety supervisor rejected command."
            )

        self._simulation.apply(applied_command)
        measurement = self._simulation.step(self._period)
        self._measurement = measurement

        result = ControlCycleResult(
            time=self._simulation.time,
            measurement=measurement,
            state=state,
            requested_command=requested_command,
            applied_command=applied_command,
            safety=decision,
        )

        if self._telemetry is not None:
            self._telemetry.publish(
                TelemetryRecord(
                    timestamp=result.time,
                    values={
                        "safety_status": result.safety.status.value,
                    },
                )
            )

        return result

    def stop(self) -> None:
        """Stop the pipeline and release owned resources."""

        if not self._running:
            return

        try:
            if self._telemetry is not None:
                self._telemetry.close()
        finally:
            self._simulation.close()
            self._running = False
            self._measurement = None

    def __enter__(
        self,
    ) -> "ControlPipeline[MeasurementT, StateT, CommandT]":
        """Return the pipeline for context-managed execution."""

        self.start()
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        """Stop the pipeline when leaving a context."""

        del exc_type, exc_value, traceback
        self.stop()
