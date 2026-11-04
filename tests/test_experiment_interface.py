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

from rift.experiments import (
    EpisodeResult,
    ExperimentResult,
    ExperimentRunner,
)


class ExampleExperiment:
    def run(self) -> ExperimentResult:
        return ExperimentResult(
            experiment_id="example",
            episodes=(
                EpisodeResult(
                    episode_id="seed-1",
                    seed=1,
                    completed=True,
                    duration=5.0,
                    metrics={"error": 0.1},
                ),
            ),
            metadata={"backend": "example"},
        )


def test_experiment_runner_returns_result():
    runner = ExampleExperiment()

    assert isinstance(runner, ExperimentRunner)

    result = runner.run()

    assert result.experiment_id == "example"
    assert result.completed
    assert result.episodes[0].metrics["error"] == 0.1


def test_experiment_requires_nonempty_completed_episodes():
    result = ExperimentResult(
        experiment_id="empty",
        episodes=(),
    )

    assert not result.completed
