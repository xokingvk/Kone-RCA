"""
RCA Assistant - Pipeline Simulation
------------------------------------
Runs the full Ingestion -> Retrieval (RAG) -> Reasoning (LLM) pipeline
against synthetic elevator fault scenarios and prints each stage clearly.

Built for screen-recording: run this, record your terminal, and you have
a working demo video of the pipeline for your PPT / submission.

Usage:
    python simulate.py                 # offline rule-based reasoning (no API key needed)
    python simulate.py --llm           # use real Claude API reasoning (needs ANTHROPIC_API_KEY)
    python simulate.py --scenario 2    # run only scenario #2
    python simulate.py --delay 1.5     # slow down output for recording (seconds between steps)
"""

import argparse
import time
import sys

sys.path.insert(0, "backend")

from backend.ingest import load_fault_scenarios
from backend.retrieval import RetrievalLayer
from backend.reasoning import offline_reason, llm_reason


def pause(seconds):
    if seconds > 0:
        time.sleep(seconds)


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def run_scenario(scenario, retriever, use_llm, delay):
    print_header(f"SCENARIO: {scenario['scenario_name']}")

    # Stage 1: Ingestion
    print("\n[1/3] INGESTION LAYER")
    print(f"   Fault code        : {scenario['fault_code']}")
    print(f"   Description       : {scenario['fault_description']}")
    print(f"   Sensor readings   : {scenario['sensor_readings']}")
    pause(delay)

    # Stage 2: Retrieval (RAG)
    print("\n[2/3] RETRIEVAL LAYER (RAG)")
    query = retriever.build_query(
        scenario["fault_code"], scenario["fault_description"], scenario["sensor_readings"]
    )
    results = retriever.retrieve(query, top_k=3)
    for r in results:
        print(f"   [{r['id']}] (score={r['relevance_score']}) {r['title']}")
    pause(delay)

    # Stage 3: Reasoning (LLM)
    print("\n[3/3] REASONING LAYER" + (" (Claude API)" if use_llm else " (offline simulation)"))
    reasoner = llm_reason if use_llm else offline_reason
    diagnosis = reasoner(scenario["fault_code"], scenario["sensor_readings"], results)

    print("\n   RANKED ROOT CAUSES:")
    for i, c in enumerate(diagnosis["ranked_causes"], 1):
        print(f"   {i}. {c['cause']}  (confidence: {c['confidence']*100:.0f}%)")
        print(f"      -> {c['reasoning']}")
    pause(delay)

    print("\n   REPAIR CHECKLIST:")
    for step in diagnosis["repair_checklist"]:
        print(f"   [ ] {step}")

    print(f"\n   >> DIAGNOSIS CONFIDENCE: {diagnosis['top_confidence']*100:.0f}%")
    print(f"   >> Sources used: {', '.join(diagnosis['retrieved_sources'])}")
    pause(delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="Use real Claude API reasoning")
    parser.add_argument("--scenario", type=int, default=None, help="Run only scenario N (1-indexed)")
    parser.add_argument("--delay", type=float, default=0.8, help="Seconds to pause between pipeline stages")
    args = parser.parse_args()

    print_header("AUTONOMOUS FAULT ISOLATION & RCA ASSISTANT")
    print("  KONE ELEVATE'26 | Problem Statement #13 | Pipeline Simulation")

    scenarios = load_fault_scenarios()
    retriever = RetrievalLayer()

    if args.scenario:
        scenarios = [scenarios[args.scenario - 1]]

    for scenario in scenarios:
        run_scenario(scenario, retriever, args.llm, args.delay)
        pause(args.delay)

    print_header("SIMULATION COMPLETE")


if __name__ == "__main__":
    main()
