"""
Ingestion Layer
---------------
Loads fault codes, sensor readings, and technician notes into a normalized
format for the retrieval layer. In this simulation, ingestion is just
validated JSON loading; in production this would connect to live IoT
telemetry streams and a technician-facing intake form.
"""

import json
import os

FAULT_SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fault_scenarios.json")


def load_fault_scenarios(path=FAULT_SCENARIOS_PATH):
    with open(path, "r") as f:
        scenarios = json.load(f)

    for s in scenarios:
        assert "fault_code" in s, "Missing fault_code in scenario"
        assert "sensor_readings" in s, "Missing sensor_readings in scenario"

    return scenarios
