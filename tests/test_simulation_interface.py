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

from rift.simulation import SimulationBackend


@dataclass(frozen=True)
class ExampleCommand:
    velocity: float


@dataclass(frozen=True)
class ExampleMeasurement:
    position: float


class ExampleSimulation:
    def __init__(self) -> None:
        self._time = 0.0
        self._position = 0.0
        self._velocity = 0.0
        self.closed = False

    @property
    def time(self) -> float:
        return self._time

    def reset(
        self,
        seed: int | None = None,
    ) -> ExampleMeasurement:
        del seed

        self._time = 0.0
        self._position = 0.0
        self._velocity = 0.0

        return ExampleMeasurement(position=self._position)

    def apply(self, command: ExampleCommand) -> None:
        self._velocity = command.velocity

    def step(self, duration: float) -> ExampleMeasurement:
        self._position += self._velocity * duration
        self._time += duration

        return ExampleMeasurement(position=self._position)

    def close(self) -> None:
        self.closed = True


def test_simulation_protocol_accepts_conforming_backend():
    simulation = ExampleSimulation()

    assert isinstance(simulation, SimulationBackend)
    assert simulation.reset(seed=7) == ExampleMeasurement(position=0.0)

    simulation.apply(ExampleCommand(velocity=2.0))

    assert simulation.step(0.5) == ExampleMeasurement(position=1.0)
    assert simulation.time == 0.5

    simulation.close()
    assert simulation.closed


def test_simulation_protocol_rejects_incomplete_backend():
    class IncompleteSimulation:
        @property
        def time(self) -> float:
            return 0.0

    assert not isinstance(IncompleteSimulation(), SimulationBackend)
