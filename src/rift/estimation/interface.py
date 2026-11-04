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

"""Estimator interfaces for RIFT applications."""

from typing import Protocol, TypeVar, runtime_checkable


MeasurementT = TypeVar("MeasurementT", contravariant=True)
StateT = TypeVar("StateT", covariant=True)


@runtime_checkable
class Estimator(Protocol[MeasurementT, StateT]):
    """Convert application-defined measurements into an estimated state."""

    def reset(self) -> None:
        """Reset internal estimator state."""

    def update(
        self,
        measurement: MeasurementT,
        dt: float,
    ) -> StateT:
        """Update and return the estimated state."""
