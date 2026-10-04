# AXORA — Working Intelligence Prototype

## What was added
- FastAPI backend with CORS enabled for local frontend development.
- Synthetic machine telemetry generator for a controlled hackathon demo.
- Transparent baseline-deviation risk engine.
- `/api/health`, `/api/telemetry`, `/api/analyze`, and `/api/dashboard` endpoints.
- `api-client.js` showing the frontend integration contract.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:
   `python -m pip install -r requirements.txt`
4. Start the API:
   - Windows: double-click `run_backend.bat`
   - macOS/Linux: `./run_backend.sh`
5. API: `http://127.0.0.1:8000`
6. API docs: `http://127.0.0.1:8000/docs`

## Important demo note
The current model is an explainable prototype risk engine, not a validated industrial ML model. It is deliberately transparent so judges can understand the signal-to-risk relationship. Replace `infer()` with a trained model once a real labeled dataset is available.

## Architecture
Machine/process telemetry → feature deviations → risk inference → recommendations → AXORA dashboard.
