from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
from llm_client import LLMClient
from utils import extract_signals

load_dotenv()

app = FastAPI(title="ErrorLens Backend (Intelligence Layer)")
llm = LLMClient()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Mock Splunk base URL
SPLUNK_BASE_URL = "http://localhost:8001"


# ─────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "ErrorLens Backend Running 🚀"}


# ─────────────────────────────────────────
# Intelligence Layer API
# ─────────────────────────────────────────
@app.post("/api/analyse")
def analyse(data: dict):
    """
    Core intelligence layer:
    - Filter impacted APIs
    - Fetch sample txnIds
    - Fetch raw logs
    - Build structured insights
    """

    service = data.get("service")
    apis = data.get("apis", [])

    impacted_apis = []

    for api in apis:
        endpoint = api.get("endpoint")
        status_breakdown = api.get("status_breakdown", {})

        error_500 = status_breakdown.get("500", 0)

        # 🔴 Step 1 — Filter noise
        if error_500 <= 2:
            continue

        # 🔥 Step 2 — Severity
        if error_500 > 10:
            severity = "HIGH"
        elif error_500 > 5:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # ─────────────────────────────────────
        # Step 3 — Fetch txnIds (sample only)
        # ─────────────────────────────────────
        txn_res = requests.get(
            f"{SPLUNK_BASE_URL}/splunk/errors/details",
            params={
                "service": service,
                "endpoint": endpoint,
                "status_code": 500
            }
        ).json()

        transactions = txn_res.get("transactions", [])
        txn_ids = [t["txn_id"] for t in transactions[:3]]  # SAMPLE ONLY

        # ─────────────────────────────────────
        # Step 4 — Fetch raw traces
        # ─────────────────────────────────────
        txn_details = []

        for txn_id in txn_ids:
            try:
                trace = requests.get(
                    f"{SPLUNK_BASE_URL}/splunk/raw-trace/{txn_id}",
                    params={"service": service} if service else None
                ).json()

                txn_details.append({
                    "txn_id": txn_id,
                    "trace": trace
                })

            except Exception as e:
                txn_details.append({
                    "txn_id": txn_id,
                    "error": str(e)
                })

        # ─────────────────────────────────────
        # Step 5 — Build structured response
        # ─────────────────────────────────────
        impacted_apis.append({
            "endpoint": endpoint,
            "error_count": error_500,
            "severity": severity,
            "sample_transactions": txn_details
        })

    # ─────────────────────────────────────────
    # Final Response
    # ─────────────────────────────────────────
    return {
        "service": service,
        "total_impacted_apis": len(impacted_apis),
        "impacted_apis": impacted_apis
    }


@app.post("/api/analyse-ai")
def analyse_ai(data: dict):
    service = data.get("service")
    endpoint = data.get("endpoint")
    txn_id = data.get("txn_id")

    if not txn_id:
        raise HTTPException(status_code=400, detail="txn_id is required")

    trace = data.get("trace")

    if not trace:
        trace_response = requests.get(
            f"{SPLUNK_BASE_URL}/splunk/raw-trace/{txn_id}",
            params={"service": service} if service else None,
            timeout=15
        )
        trace_response.raise_for_status()
        trace = trace_response.json()

    signals, context_logs = extract_signals(trace)

    prompt = f"""
You are a senior backend engineer debugging production issues.

Service: {service or "unknown"}
API: {endpoint or "unknown"}
Transaction ID: {txn_id}

Signals:
{signals}

Important Logs:
{context_logs}

Classify root cause into exactly one of:
1. BUG
2. DEPENDENCY
3. BAD_REQUEST
4. BUSINESS_RULE
5. UNKNOWN

Rules:
- DB errors, deadlock, Kafka outage, downstream timeouts -> DEPENDENCY
- Exception thrown in same service code path -> BUG
- 400 or malformed request -> BAD_REQUEST
- 409, 422, validation, insufficient funds, duplicate request -> BUSINESS_RULE
- If evidence is weak, use UNKNOWN

Return only valid JSON:
{{
  "root_cause": "...",
  "confidence": "HIGH|MEDIUM|LOW",
  "reason": "short explanation"
}}
"""

    try:
        analysis = llm.generate_json(prompt)
    except Exception as exc:
        analysis = {
            "root_cause": "UNKNOWN",
            "confidence": "LOW",
            "reason": str(exc)
        }

    return {
        "service": service,
        "endpoint": endpoint,
        "txn_id": txn_id,
        "signals": signals,
        "important_logs": context_logs,
        "analysis": analysis
    }
