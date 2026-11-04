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

"""Runtime interfaces for RIFT applications."""

from typing import Protocol, TypeVar, runtime_checkable


ResultT = TypeVar("ResultT", covariant=True)


@runtime_checkable
class Runtime(Protocol[ResultT]):
    """Execute an application through a specific runtime backend."""

    @property
    def time(self) -> float:
        """Return the current runtime time in seconds."""

    @property
    def running(self) -> bool:
        """Return whether the runtime is active."""

    def start(self) -> None:
        """Initialize and start the runtime."""

    def step(self) -> ResultT:
        """Execute one runtime cycle and return its result."""

    def stop(self) -> None:
        """Stop the runtime and release its resources."""
