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

from rift.telemetry import TelemetryRecord, TelemetrySink


class MemoryTelemetrySink:
    def __init__(self) -> None:
        self.records: list[TelemetryRecord] = []
        self.closed = False

    def publish(self, record: TelemetryRecord) -> None:
        self.records.append(record)

    def close(self) -> None:
        self.closed = True


def test_telemetry_sink_accepts_records():
    sink = MemoryTelemetrySink()
    record = TelemetryRecord(
        timestamp=1.5,
        values={
            "position": 0.2,
            "active": True,
            "mode": "simulation",
        },
    )

    assert isinstance(sink, TelemetrySink)

    sink.publish(record)
    sink.close()

    assert sink.records == [record]
    assert sink.closed


def test_telemetry_sink_rejects_incomplete_sink():
    class IncompleteSink:
        def close(self) -> None:
            pass

    assert not isinstance(IncompleteSink(), TelemetrySink)
