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

from rift.application import Application


class ExampleApplication:
    def __init__(self) -> None:
        self.configured = False
        self.running = False

    def configure(self) -> None:
        self.configured = True

    def start(self) -> None:
        if not self.configured:
            raise RuntimeError("Application is not configured.")

        self.running = True

    def stop(self) -> None:
        self.running = False


def test_application_protocol_accepts_lifecycle():
    application = ExampleApplication()

    assert isinstance(application, Application)

    application.configure()
    application.start()

    assert application.configured
    assert application.running

    application.stop()
    assert not application.running


def test_application_protocol_rejects_incomplete_application():
    class IncompleteApplication:
        def start(self) -> None:
            pass

    assert not isinstance(IncompleteApplication(), Application)
