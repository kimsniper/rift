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


@dataclass(frozen=True)
class ExampleState:
    position: float


@dataclass(frozen=True)
class ExampleCommand:
    effort: float


class ExampleController:
    def reset(self) -> None:
        pass

    def compute(
        self,
        state: ExampleState,
        dt: float,
    ) -> ExampleCommand:
        return ExampleCommand(effort=-state.position / dt)


def test_controller_protocol_accepts_conforming_controller():
    controller = ExampleController()

    assert isinstance(controller, Controller)
    assert controller.compute(
        ExampleState(position=0.2),
        dt=0.1,
    ) == ExampleCommand(effort=-2.0)


def test_controller_protocol_rejects_missing_compute():
    class IncompleteController:
        def reset(self) -> None:
            pass

    assert not isinstance(IncompleteController(), Controller)
