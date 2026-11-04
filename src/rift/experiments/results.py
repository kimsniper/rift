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

"""Experiment result types for RIFT applications."""

from dataclasses import dataclass, field
from typing import Mapping


MetricValue = bool | int | float | str


@dataclass(frozen=True)
class EpisodeResult:
    """Results and metadata from one experiment episode."""

    episode_id: str
    seed: int | None
    completed: bool
    duration: float
    metrics: Mapping[str, MetricValue] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentResult:
    """Collection of results from one experiment execution."""

    experiment_id: str
    episodes: tuple[EpisodeResult, ...]
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def completed(self) -> bool:
        """Return whether every episode completed successfully."""

        return bool(self.episodes) and all(
            episode.completed for episode in self.episodes
        )
