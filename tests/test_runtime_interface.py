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

from rift.runtime import Runtime


@dataclass(frozen=True)
class ExampleResult:
    cycle: int
    time: float


class ExampleRuntime:
    def __init__(self, period: float = 0.1) -> None:
        self._period = period
        self._time = 0.0
        self._cycle = 0
        self._running = False

    @property
    def time(self) -> float:
        return self._time

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True

    def step(self) -> ExampleResult:
        if not self._running:
            raise RuntimeError("Runtime is not active.")

        self._cycle += 1
        self._time += self._period

        return ExampleResult(
            cycle=self._cycle,
            time=self._time,
        )

    def stop(self) -> None:
        self._running = False


def test_runtime_protocol_accepts_conforming_runtime():
    runtime = ExampleRuntime()

    assert isinstance(runtime, Runtime)
    assert not runtime.running

    runtime.start()

    assert runtime.running
    assert runtime.step() == ExampleResult(
        cycle=1,
        time=0.1,
    )
    assert runtime.time == 0.1

    runtime.stop()
    assert not runtime.running


def test_runtime_protocol_rejects_incomplete_runtime():
    class IncompleteRuntime:
        @property
        def time(self) -> float:
            return 0.0

    assert not isinstance(IncompleteRuntime(), Runtime)
