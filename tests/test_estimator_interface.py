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

from rift.estimation import Estimator


@dataclass(frozen=True)
class ExampleMeasurement:
    position: float


@dataclass(frozen=True)
class ExampleState:
    position: float
    velocity: float


class ExampleEstimator:
    def __init__(self) -> None:
        self._previous_position = 0.0

    def reset(self) -> None:
        self._previous_position = 0.0

    def update(
        self,
        measurement: ExampleMeasurement,
        dt: float,
    ) -> ExampleState:
        velocity = (
            measurement.position - self._previous_position
        ) / dt
        self._previous_position = measurement.position

        return ExampleState(
            position=measurement.position,
            velocity=velocity,
        )


def test_estimator_protocol_accepts_conforming_estimator():
    estimator = ExampleEstimator()

    assert isinstance(estimator, Estimator)
    assert estimator.update(
        ExampleMeasurement(position=0.2),
        dt=0.1,
    ) == ExampleState(
        position=0.2,
        velocity=2.0,
    )


def test_estimator_protocol_rejects_missing_update():
    class IncompleteEstimator:
        def reset(self) -> None:
            pass

    assert not isinstance(IncompleteEstimator(), Estimator)
