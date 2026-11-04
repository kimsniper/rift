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

from rift.policies import Policy


@dataclass(frozen=True)
class Observation:
    error: float


@dataclass(frozen=True)
class Action:
    effort: float


class ExamplePolicy:
    def reset(self) -> None:
        pass

    def predict(
        self,
        observation: Observation,
        *,
        deterministic: bool = True,
    ) -> Action:
        scale = 1.0 if deterministic else 0.5
        return Action(effort=-observation.error * scale)


def test_policy_protocol_accepts_conforming_policy():
    policy = ExamplePolicy()

    assert isinstance(policy, Policy)
    assert policy.predict(
        Observation(error=2.0),
    ) == Action(effort=-2.0)


def test_policy_protocol_rejects_missing_predict():
    class IncompletePolicy:
        def reset(self) -> None:
            pass

    assert not isinstance(IncompletePolicy(), Policy)
