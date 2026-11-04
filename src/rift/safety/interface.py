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

"""Safety interfaces for RIFT applications."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, TypeVar, runtime_checkable


CommandT = TypeVar("CommandT")


class SafetyStatus(str, Enum):
    """Result of evaluating a command against application safety rules."""

    ACCEPTED = "accepted"
    MODIFIED = "modified"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SafetyDecision:
    """Describe the outcome of a safety evaluation."""

    status: SafetyStatus
    reason: str | None = None


@runtime_checkable
class SafetySupervisor(Protocol[CommandT]):
    """Validate or modify commands before backend execution."""

    def reset(self) -> None:
        """Reset internal safety state."""

    def evaluate(
        self,
        command: CommandT,
        *,
        timestamp: float,
    ) -> tuple[CommandT | None, SafetyDecision]:
        """Evaluate a command and return the safe output and decision."""
