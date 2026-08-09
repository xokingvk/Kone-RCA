*Autonomous Fault Isolation & Root Cause Analysis Assistant*
KONE ELEVATE'26 Hackathon | Problem Statement #13

## Problem

When an elevator throws a fault code, the code itself rarely tells the full story — the same code can point to several different root causes, and today, correctly identifying which one requires a technician's years of built-up experience. When that experience isn't available on-site, diagnosis slows down, repairs get delayed, and elevators stay out of service longer than necessary.

## The Gap

- Root-cause diagnosis today lives mostly in senior technicians' tacit experience, not in any reusable system.
- Service manuals contain the answers but aren't searchable in a way that maps live symptoms to likely causes quickly.
- Fault codes alone are ambiguous — existing systems display the code but don't reason across sensor context, documentation, and history to narrow down the actual cause.
- No feedback loop exists to learn from past resolved faults.

## Proposed Solution

An intelligent assistant that reasons through fault data the way an expert technician would — not just searching, but diagnosing.

- Retrieves relevant service knowledge and historical resolution patterns, then ranks the most likely root causes with clear explanations and next-step actions
- Primary target: field service teams, supporting real-time on-site diagnosis
- Future direction (beyond current build): live IoT integration, predictive maintenance, and deployment across KONE's service ecosystem

## Architecture
Fault Code / Sensor Input (Frontend)
|
v
Node.js + Express (App Backend)
| Internal REST API
v
Python + FastAPI (AI Microservice)
|
v
Retrieval Layer (RAG) <--> Knowledge Base (FAISS)
| Manuals + Fault History
v
LLM Reasoning Layer (Groq / DeepSeek API)
|
v
Technician Output
Diagnosis + Confidence + Repair Checklist + Feedback
(Stored in MongoDB)
 ## Tech Stack

*Programming Languages, Frameworks & Tools*
- HTML, CSS, JavaScript — technician-facing diagnostic interface
- Node.js + Express — application backend handling user interaction and session/history management
- Python + FastAPI — dedicated AI microservice handling retrieval and reasoning logic

*APIs, Libraries & Platforms*
- MongoDB — stores fault records, technician-confirmed diagnoses, and historical resolution data
- FAISS — vector similarity search for matching fault queries to relevant manuals and fault history
- Sentence-Transformers — embedding generation for semantic retrieval
- Groq API / DeepSeek API — LLM reasoning, root-cause ranking, and explanation generation
- Internal REST API — connects the Node/Express app layer to the Python AI microservice

*Hardware / Special Technologies*
- Not required for the current prototype — fully software-based simulation
- Future scope: edge deployment on IoT gateway hardware near elevator controllers for real-time sensor integration

## Data Sources

Our knowledge base is grounded in public elevator and motor fault-diagnosis data rather than synthetic guesses:

- ElevatorFaultDetection dataset — real elevator fault categories (Door Failure, Motor Malfunction, Sensor Error, Brake Failure) and severity levels (Minor, Moderate, Critical), used as the structural backbone of our fault taxonomy
- Public synchronous motor fault dataset (Technion) — real motor electrical fault types with phase voltage/current recordings, used to ground mock sensor readings
- Published VFD troubleshooting guidance (Elevator World) — used as reference for writing realistic manual-style knowledge base entries
- Mock historical fault-resolution cases, hand-curated to demonstrate the retrieval and feedback pipeline

Note: RAG does not require model training — no model is fine-tuned. The knowledge base is a retrieval index the LLM searches at query time.

## How It Works (Demo Flow)

1. Technician enters a fault code and sensor readings via the UI.
2. Node/Express backend receives the request and calls the Python AI microservice.
3. The AI microservice embeds the query and retrieves the top-k relevant manual sections and past similar fault cases from FAISS.
4. Retrieved context + fault data is passed to the LLM (Groq/DeepSeek), which reasons through possible causes.
5. Output: ranked root causes with confidence scores, explanation, and a repair checklist — returned to the technician via Node/Express.
6. Technician can confirm/correct the diagnosis, stored in MongoDB — feeding back into future retrieval relevance.

## Impact & Benefits

- KONE Field Technicians — faster, more consistent diagnosis that doesn't depend on years of accumulated experience
- KONE (Business) — fewer repeat site visits, lower mean-time-to-repair, meaningful service-cost reduction at scale
- Building Owners & Facility Managers — less elevator downtime, less tenant disruption, better SLA compliance
- Riders — faster fault resolution means fewer safety-critical issues left unresolved
- KONE's Institutional Knowledge — every resolved fault makes the system smarter over time

## Future Scope

- Live IoT sensor stream integration for real-time, fully autonomous fault detection
- Continuous learning from technician feedback to sharpen retrieval and reasoning accuracy
- Predictive maintenance — flagging likely failures before they happen
- Edge-deployable lightweight version for low-latency, offline-capable diagnosis
- Native integration with KONE's service ticketing/CMMS systems

## Team

- B.Vishnuvardhan
- B.kamaleshwaran
- F.Kevin Cris
- P.John Ezra
