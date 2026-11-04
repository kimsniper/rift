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

"""Application lifecycle interfaces for RIFT."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Application(Protocol):
    """Define the lifecycle of an application built on RIFT."""

    def configure(self) -> None:
        """Load and validate application configuration."""

    def start(self) -> None:
        """Start application components."""

    def stop(self) -> None:
        """Stop application components and release resources."""
