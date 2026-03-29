"""
ErrorLens - Mock Splunk API (FINAL)

Features:
- Parse Spring Boot logs
- Aggregate errors per API
- Drill-down to txnIds
- Full distributed trace
- Service health check
- Error frequency
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dateutil import parser as date_parser
from typing import Optional
import os
import json
import re

app = FastAPI(title="ErrorLens Mock Splunk", version="4.0")

# ─────────────────────────────────────────
# CORS
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(BASE_DIR, "data", "logs")
HEALTH_FILE = os.path.join(BASE_DIR, "data", "service_health.json")


def list_services():
    if not os.path.exists(LOGS_DIR):
        return []

    return sorted(
        file.replace(".log", "")
        for file in os.listdir(LOGS_DIR)
        if file.endswith(".log")
    )

# ─────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────
def parse_log_file(filepath, service):
    logs = []

    if not os.path.exists(filepath):
        return logs

    with open(filepath, "r") as f:
        lines = f.readlines()

    current = None
    stack = []

    pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+\-]\d{2}:\d{2})\s+'
        r'(ERROR|WARN|INFO|DEBUG)\s+'
        r'\d+\s+---\s+\[([^\]]+)\]\s+'
        r'([\w.]+)\s+:\s+(.+)$'
    )

    for line in lines:
        line = line.rstrip()
        match = pattern.match(line)

        if match:
            if current:
                current["stack_trace"] = "\n".join(stack) if stack else None
                logs.append(current)
                stack = []

            timestamp, level, thread, logger, msg = match.groups()

            txn = re.search(r'txnId=([\w\-]+)', msg)
            status = re.search(r'status=(\d{3})', msg)
            endpoint = re.search(r'endpoint=([/\w\-]+)', msg)
            downstream = re.search(r'downstream=([\w\-]+)', msg)

            current = {
                "timestamp": timestamp,
                "level": level,
                "service": service,
                "message": msg,
                "txn_id": txn.group(1) if txn else None,
                "status_code": int(status.group(1)) if status else None,
                "endpoint": endpoint.group(1) if endpoint else None,
                "downstream_service": downstream.group(1) if downstream else None,
                "exception_type": None,
                "stack_trace": None
            }

        elif current:
            s = line.strip()
            if s:
                if current["exception_type"] is None and not s.startswith("at "):
                    current["exception_type"] = s.split(":")[0]
                stack.append(line)

    if current:
        current["stack_trace"] = "\n".join(stack) if stack else None
        logs.append(current)

    return [l for l in logs if l["level"] in ("ERROR", "WARN")]


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
def load_logs():
    all_logs = []

    if not os.path.exists(LOGS_DIR):
        return all_logs

    for file in os.listdir(LOGS_DIR):
        if file.endswith(".log"):
            service = file.replace(".log", "")
            path = os.path.join(LOGS_DIR, file)

            parsed = parse_log_file(path, service)
            all_logs.extend(parsed)

            print(f"{service}: {len(parsed)} logs")

    return all_logs


def load_health():
    if not os.path.exists(HEALTH_FILE):
        return []

    with open(HEALTH_FILE) as f:
        return json.load(f)


ALL_LOGS = load_logs()
SERVICE_HEALTH = load_health()

# ─────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────
@app.get("/get/services")
def root():
    return {
        "services": list_services(),
        "total_logs": len(ALL_LOGS)
    }

@app.get("/splunk/error")
def dashboard(
    service: str,
    start_time: str = Query(..., description="ISO timestamp e.g. 2026-03-25T00:00:00+05:30"),
    end_time: str = Query(..., description="ISO timestamp e.g. 2026-03-28T23:59:59+05:30")
):
    """
    Returns all APIs for a service in a date range.
    Each API has a breakdown of error codes and their counts.
    
    Response:
    [
        {
            "api": "/api/payments/process",
            "total_errors": 10,
            "error_breakdown": [
                { "status_code": 500, "count": 7 },
                { "status_code": 400, "count": 3 }
            ]
        }
    ]
    """
    start_dt = date_parser.parse(start_time)
    end_dt = date_parser.parse(end_time)

    # Filter by service and date range
    logs = [
        l for l in ALL_LOGS
        if l["service"] == service
        and start_dt <= date_parser.parse(l["timestamp"]) <= end_dt
    ]

    # Group by endpoint → status_code → count
    agg = {}

    for l in logs:
        endpoint = l.get("endpoint") or "UNKNOWN"
        status = l.get("status_code") or "NA"

        if endpoint not in agg:
            agg[endpoint] = {}

        if status not in agg[endpoint]:
            agg[endpoint][status] = 0

        agg[endpoint][status] += 1

    # Format response
    result = []
    for endpoint, status_counts in agg.items():
        result.append({
            "api": endpoint,
            "total_errors": sum(status_counts.values()),
            "error_breakdown": [
                {"status_code": code, "count": count}
                for code, count in sorted(status_counts.items())
            ]
        })

    # Sort by total errors descending
    result.sort(key=lambda x: x["total_errors"], reverse=True)

    return {
        "service": service,
        "start_time": start_time,
        "end_time": end_time,
        "total_apis_affected": len(result),
        "total_errors": sum(r["total_errors"] for r in result),
        "data": result
    }

# ─────────────────────────────────────────
# 🔥 AGGREGATION (SERVICE → APIs)
# ─────────────────────────────────────────
@app.get("/splunk/aggregate/apis")
def aggregate_apis(service: str, status_code: Optional[int] = None):

    logs = [l for l in ALL_LOGS if l["service"] == service]

    if status_code:
        logs = [l for l in logs if l.get("status_code") == status_code]

    agg = {}

    for l in logs:
        endpoint = l.get("endpoint")
        if not endpoint:
            continue

        if endpoint not in agg:
            agg[endpoint] = {
                "endpoint": endpoint,
                "count": 0,
                "status_breakdown": {}
            }

        agg[endpoint]["count"] += 1

        status = l.get("status_code") or "NA"

        if status not in agg[endpoint]["status_breakdown"]:
            agg[endpoint]["status_breakdown"][status] = 0

        agg[endpoint]["status_breakdown"][status] += 1

    result = list(agg.values())
    result.sort(key=lambda x: x["count"], reverse=True)

    return {
        "service": service,
        "total_apis": len(result),
        "data": result
    }


# ─────────────────────────────────────────
# 🔥 DRILL-DOWN (API → txnIds)
# ─────────────────────────────────────────
@app.get("/splunk/errors/details")
def details(service: str,
            endpoint: str,
            status_code: Optional[int] = None):

    logs = [l for l in ALL_LOGS if l["service"] == service]

    logs = [l for l in logs if l.get("endpoint") == endpoint]

    if status_code:
        logs = [l for l in logs if l.get("status_code") == status_code]

    txn_map = {}

    for l in logs:
        txn = l.get("txn_id")
        if not txn:
            continue

        if txn not in txn_map:
            txn_map[txn] = {
                "txn_id": txn,
                "timestamp": l["timestamp"],
                "error": l.get("exception_type"),
                "status_code": l.get("status_code")
            }

    return {
        "count": len(txn_map),
        "transactions": list(txn_map.values())
    }


# ─────────────────────────────────────────
# 🔥 TRACE (txnId → full flow)
# ─────────────────────────────────────────
@app.get("/splunk/raw-trace/{txn_id}")
def get_raw_trace(txn_id: str):

    result = []

    for file in os.listdir(LOGS_DIR):
        if not file.endswith(".log"):
            continue

        service = file.replace(".log", "")
        filepath = os.path.join(LOGS_DIR, file)

        with open(filepath, "r") as f:
            lines = f.readlines()

        collected = []
        capture = False

        for i, line in enumerate(lines):
            if f"txnId={txn_id}" in line:
                capture = True

            if capture:
                collected.append(line.rstrip())

                # keep collecting until next txn starts OR file ends
                if i + 1 < len(lines):
                    next_line = lines[i + 1]

                    # if next line has DIFFERENT txn → stop
                    if "txnId=" in next_line and f"txnId={txn_id}" not in next_line:
                        capture = False
                else:
                    break

        if collected:
            result.append({
                "service": service,
                "logs": collected
            })

    return {
        "txn_id": txn_id,
        "raw_logs": result
    }


# ─────────────────────────────────────────
# SERVICE HEALTH
# ─────────────────────────────────────────
@app.get("/splunk/health/{service}")
def health(service: str, timestamp: Optional[str] = None):

    records = [h for h in SERVICE_HEALTH if h["service"] == service]

    if timestamp:
        t = date_parser.parse(timestamp)

        down = any(
            date_parser.parse(h["start_time"]) <= t <= date_parser.parse(h["end_time"])
            for h in records
        )

        return {"service": service, "was_down": down}

    return {"service": service, "records": records}


# ─────────────────────────────────────────
# FREQUENCY
# ─────────────────────────────────────────
@app.get("/splunk/frequency")
def frequency(exception_type: Optional[str] = None):

    logs = ALL_LOGS

    if exception_type:
        logs = [
            l for l in logs
            if l.get("exception_type") and exception_type.lower() in l["exception_type"].lower()
        ]

    return {
        "count": len(logs),
        "is_recurring": len(logs) > 3
    }
