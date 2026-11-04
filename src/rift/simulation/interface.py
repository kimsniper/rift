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

"""Simulation backend interfaces for RIFT applications."""

from typing import Protocol, TypeVar, runtime_checkable


CommandT = TypeVar("CommandT", contravariant=True)
MeasurementT = TypeVar("MeasurementT", covariant=True)


@runtime_checkable
class SimulationBackend(Protocol[CommandT, MeasurementT]):
    """Provide application-neutral access to a robot simulator."""

    @property
    def time(self) -> float:
        """Return the current simulation time in seconds."""

    def reset(self, seed: int | None = None) -> MeasurementT:
        """Reset the simulation and return the initial measurements."""

    def apply(self, command: CommandT) -> None:
        """Apply an application-defined command."""

    def step(self, duration: float) -> MeasurementT:
        """Advance the simulation and return updated measurements."""

    def close(self) -> None:
        """Release simulator resources."""
