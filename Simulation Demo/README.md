# Autonomous Fault Isolation & RCA Assistant
KONE ELEVATE'26 | Problem Statement #13

## What this is
A working Python simulation of the 3-layer pipeline (Ingestion -> Retrieval/RAG -> Reasoning/LLM)
described in the proposal. Runs standalone with synthetic elevator fault data — no API key required
for the base demo.

## Quick start
```bash
pip install -r requirements.txt
python simulate.py                  # runs all 4 fault scenarios, offline reasoning
python simulate.py --scenario 1     # run just one scenario
python simulate.py --delay 1.5      # slow down for screen recording
python simulate.py --llm            # use real Claude API (needs ANTHROPIC_API_KEY env var)
```

## Visual demo (recommended for video)
`visualize.py` is a Pygame window showing the pipeline animate live: stage bar lighting up
top to bottom, retrieved knowledge-base entries appearing, and confidence bars filling in
for each ranked root cause.

```bash
python visualize.py
```
Controls: `SPACE` = next scenario, `R` = restart animation, `ESC` = quit.

**Note:** Pygame needs a real display — run this locally (not in Colab, which has no screen).
Just record your screen while it runs through 1-2 scenarios (~10-15 sec each).

## For the terminal demo video (alternative)
1. Open a terminal, increase font size for readability on recording.
2. `pip install -r requirements.txt`
3. Run: `python simulate.py --delay 1.2`
4. Screen record the terminal output (QuickTime / OBS / Windows Game Bar all work).
5. Optionally narrate each stage as it prints: ingestion -> retrieval -> reasoning -> checklist.
6. Keep it under 90 seconds — 1-2 scenarios is enough to prove the pipeline works.

## Notes on the tech stack vs. this simulation
- The retrieval layer here uses TF-IDF + cosine similarity (scikit-learn) instead of
  FAISS + sentence-transformers, so the demo runs instantly with no large model downloads.
  Swappable — same interface, described in the full proposal as the production stack.
- Reasoning defaults to a rule-based offline mode so the demo works with zero setup.
  Pass `--llm` with `ANTHROPIC_API_KEY` set to use real Claude reasoning instead.

## Structure
```
rca-assistant/
├── simulate.py              # main CLI demo — run this
├── backend/
│   ├── ingest.py             # loads fault scenarios
│   ├── retrieval.py          # RAG retrieval (TF-IDF)
│   └── reasoning.py          # rule-based + real LLM reasoning
├── data/
│   ├── knowledge_base/manuals.json   # synthetic manuals + resolved fault history
│   └── fault_scenarios.json          # synthetic fault scenarios to run
└── requirements.txt
```
