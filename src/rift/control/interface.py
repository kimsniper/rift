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

"""Controller interfaces for RIFT applications."""

from typing import Protocol, TypeVar, runtime_checkable


StateT = TypeVar("StateT", contravariant=True)
CommandT = TypeVar("CommandT", covariant=True)


@runtime_checkable
class Controller(Protocol[StateT, CommandT]):
    """Convert an application-defined state into a command."""

    def reset(self) -> None:
        """Reset internal controller state."""

    def compute(self, state: StateT, dt: float) -> CommandT:
        """Compute a command from the current state."""
