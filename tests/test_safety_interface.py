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

from rift.safety import (
    SafetyDecision,
    SafetyStatus,
    SafetySupervisor,
)


@dataclass(frozen=True)
class Command:
    effort: float


class EffortLimiter:
    def __init__(self, limit: float) -> None:
        self._limit = limit

    def reset(self) -> None:
        pass

    def evaluate(
        self,
        command: Command,
        *,
        timestamp: float,
    ) -> tuple[Command | None, SafetyDecision]:
        del timestamp

        limited = max(-self._limit, min(self._limit, command.effort))

        if limited == command.effort:
            return command, SafetyDecision(
                status=SafetyStatus.ACCEPTED,
            )

        return Command(effort=limited), SafetyDecision(
            status=SafetyStatus.MODIFIED,
            reason="Effort exceeded the configured limit.",
        )


def test_safety_supervisor_accepts_safe_command():
    supervisor = EffortLimiter(limit=1.0)

    assert isinstance(supervisor, SafetySupervisor)

    command, decision = supervisor.evaluate(
        Command(effort=0.5),
        timestamp=1.0,
    )

    assert command == Command(effort=0.5)
    assert decision.status is SafetyStatus.ACCEPTED


def test_safety_supervisor_limits_unsafe_command():
    supervisor = EffortLimiter(limit=1.0)

    command, decision = supervisor.evaluate(
        Command(effort=2.0),
        timestamp=1.0,
    )

    assert command == Command(effort=1.0)
    assert decision.status is SafetyStatus.MODIFIED
    assert decision.reason is not None
