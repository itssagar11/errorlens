def extract_signals(trace: dict):
    signals = {
        "status": None,
        "exceptions": [],
        "errors": [],
        "warnings": [],
        "keywords": []
    }

    important_logs = []

    for svc in trace.get("raw_logs", []):
        for log in svc.get("logs", []):
            if not log.strip():
                continue

            if "status=" in log:
                try:
                    signals["status"] = log.split("status=")[1].split()[0]
                except Exception:
                    pass

            if "Exception" in log:
                signals["exceptions"].append(log)
                important_logs.append(log)

            if "ERROR" in log:
                signals["errors"].append(log)
                important_logs.append(log)

            if "WARN" in log:
                signals["warnings"].append(log)
                important_logs.append(log)

            lower = log.lower()

            if "deadlock" in lower:
                signals["keywords"].append("deadlock")
                important_logs.append(log)

            if "timeout" in lower:
                signals["keywords"].append("timeout")
                important_logs.append(log)

            if "duplicate" in lower or "idempotency" in lower:
                signals["keywords"].append("duplicate")
                important_logs.append(log)

            if "invalid" in lower or "bad request" in lower:
                signals["keywords"].append("invalid_request")
                important_logs.append(log)

            if "insufficient" in lower or "balance" in lower:
                signals["keywords"].append("business_rule")
                important_logs.append(log)

            if "downstream" in lower or "calling" in lower:
                signals["keywords"].append("downstream_call")

    signals["keywords"] = sorted(set(signals["keywords"]))

    return signals, important_logs[:10]
