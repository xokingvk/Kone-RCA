"""
Reasoning Layer
---------------
Combines fault data + retrieved context to produce a ranked root-cause
diagnosis with confidence scores and a repair checklist.

Two modes:
  - offline_reason(): rule-based simulation, works with zero API key/internet.
    Good for a reliable, fast demo video.
  - llm_reason(): real call to Claude via the Anthropic API, used when
    ANTHROPIC_API_KEY is set, for a "real AI reasoning" version of the demo.
"""

import os
import json


def offline_reason(fault_code, sensor_readings, retrieved_context):
    """
    Lightweight rule-based reasoning simulation. Mirrors the structure an
    LLM call would return, so the rest of the pipeline / UI doesn't change
    when swapping in the real LLM.
    """
    causes = []

    if fault_code == "E-104":
        temp = sensor_readings.get("bearing_temp_c", 0)
        vib = sensor_readings.get("vibration_mm_s", 0)
        if temp > 70 and vib > 3.5:
            causes = [
                {"cause": "Worn traction motor bearing", "confidence": 0.87,
                 "reasoning": "Bearing temperature and vibration both exceed normal thresholds, matching resolved case H001."},
                {"cause": "Motor winding insulation breakdown", "confidence": 0.09,
                 "reasoning": "Possible but less likely given vibration signature points to mechanical cause."},
                {"cause": "Faulty current sensor", "confidence": 0.04,
                 "reasoning": "Would not typically correlate with elevated temperature and vibration together."},
            ]
        else:
            causes = [
                {"cause": "Building power quality / voltage sag", "confidence": 0.78,
                 "reasoning": "Overcurrent code present without temperature/vibration anomaly, matching manual M005 guidance."},
                {"cause": "Faulty current sensor", "confidence": 0.15,
                 "reasoning": "Sensor readings appear otherwise normal, low but non-zero possibility."},
                {"cause": "Mechanical binding", "confidence": 0.07,
                 "reasoning": "Unlikely given normal bearing temperature and vibration."},
            ]
    elif fault_code == "E-210":
        vib = sensor_readings.get("door_header_vibration_mm_s", 0)
        if vib > 2.5:
            causes = [
                {"cause": "Worn door roller", "confidence": 0.82,
                 "reasoning": "Door header vibration exceeds 2.5 mm/s threshold with clear sensor beam, matching resolved case H002."},
                {"cause": "Track misalignment", "confidence": 0.13,
                 "reasoning": "Often co-occurs with roller wear; recommend inspecting track during repair."},
                {"cause": "Sensor beam fault", "confidence": 0.05,
                 "reasoning": "Beam status reports clear, making this less likely."},
            ]
        else:
            causes = [
                {"cause": "Sensor beam obstruction/fault", "confidence": 0.65,
                 "reasoning": "Low vibration reading shifts likelihood toward electronic/sensor cause."},
                {"cause": "Software/logic fault in door controller", "confidence": 0.25,
                 "reasoning": "Possible if no mechanical or sensor anomaly is found on inspection."},
                {"cause": "Worn door roller", "confidence": 0.10,
                 "reasoning": "Less likely given vibration is within normal range."},
            ]
    elif fault_code == "E-305":
        resp = sensor_readings.get("solenoid_response_ms", 0)
        wear = sensor_readings.get("brake_pad_wear_pct", 0)
        if resp > 150:
            causes = [
                {"cause": "Brake solenoid degradation", "confidence": 0.84,
                 "reasoning": f"Solenoid response time {resp}ms exceeds 150ms threshold, matching resolved case H003."},
                {"cause": "Contaminated brake surface (oil ingress)", "confidence": 0.10,
                 "reasoning": "Cannot be ruled out without visual inspection."},
                {"cause": "Worn brake pads", "confidence": 0.06,
                 "reasoning": f"Pad wear at {wear}% is within normal range, making this less likely."},
            ]
        else:
            causes = [
                {"cause": "Worn brake pads", "confidence": 0.70,
                 "reasoning": f"Pad wear at {wear}% with normal solenoid response points to pad wear as primary cause."},
                {"cause": "Contaminated brake surface", "confidence": 0.20,
                 "reasoning": "Possible secondary factor, recommend visual check."},
                {"cause": "Brake solenoid degradation", "confidence": 0.10,
                 "reasoning": "Solenoid response is within normal range, low likelihood."},
            ]
    else:
        causes = [
            {"cause": "Unclassified fault -- manual inspection required", "confidence": 0.50,
             "reasoning": "No matching rule pattern found in current knowledge base."}
        ]

    top_cause = causes[0]
    checklist = _generate_checklist(fault_code, top_cause["cause"])

    return {
        "ranked_causes": causes,
        "top_confidence": top_cause["confidence"],
        "repair_checklist": checklist,
        "retrieved_sources": [c["id"] for c in retrieved_context],
    }


def _generate_checklist(fault_code, top_cause):
    checklists = {
        "Worn traction motor bearing": [
            "Isolate power and lock out traction machine",
            "Inspect bearing for pitting, discoloration, or play",
            "Measure bearing temperature under test load",
            "Replace bearing if wear confirmed",
            "Re-run VFD diagnostic cycle to confirm current draw is normal",
        ],
        "Building power quality / voltage sag": [
            "Log incoming supply voltage over a 24hr period",
            "Cross-reference sag events with building peak demand times",
            "Check VFD input capacitor health",
            "Escalate to building electrical team if sag confirmed",
        ],
        "Worn door roller": [
            "Inspect door rollers for flat spots or wear",
            "Check track alignment with level",
            "Replace worn rollers",
            "Cycle door 10x and confirm vibration reading drops below 2.5 mm/s",
        ],
        "Sensor beam obstruction/fault": [
            "Clean door sensor beam lens",
            "Check beam alignment",
            "Test beam continuity",
            "Replace sensor module if fault persists",
        ],
        "Brake solenoid degradation": [
            "Measure solenoid response time under load",
            "Inspect solenoid coil resistance",
            "Replace solenoid if response time exceeds 150ms",
            "Re-test brake holding torque at rated car load",
        ],
        "Worn brake pads": [
            "Measure pad thickness against OEM spec",
            "Inspect for uneven wear pattern",
            "Replace pads if below minimum threshold",
            "Re-test brake holding torque",
        ],
    }
    return checklists.get(top_cause, ["Manual inspection required -- no automated checklist available for this cause."])


def llm_reason(fault_code, sensor_readings, retrieved_context):
    """
    Real LLM call via Anthropic API. Requires ANTHROPIC_API_KEY env var.
    Falls back to offline_reason() if the call fails for any reason
    (e.g. no key set), so the demo never breaks.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return offline_reason(fault_code, sensor_readings, retrieved_context)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        context_text = "\n\n".join(f"[{c['id']}] {c['title']}: {c['text']}" for c in retrieved_context)
        prompt = f"""You are an elevator fault diagnosis assistant. Given the fault data and retrieved
knowledge base context below, return ONLY valid JSON (no markdown, no preamble) with this schema:
{{
  "ranked_causes": [{{"cause": str, "confidence": float (0-1), "reasoning": str}}, ...] (top 3, sorted by confidence desc),
  "repair_checklist": [str, ...]
}}

Fault code: {fault_code}
Sensor readings: {json.dumps(sensor_readings)}

Retrieved context:
{context_text}
"""
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        parsed["top_confidence"] = parsed["ranked_causes"][0]["confidence"]
        parsed["retrieved_sources"] = [c["id"] for c in retrieved_context]
        return parsed
    except Exception as e:
        print(f"[reasoning] LLM call failed ({e}), falling back to offline reasoning.")
        return offline_reason(fault_code, sensor_readings, retrieved_context)
