import hashlib
import json
import datetime
from decimal import Decimal
from backend.mongo import get_mongo_db

GENESIS_HASH = "0" * 64

def sanitize_for_mongo(obj):
    """Recursively converts Decimal to float/str and date to ISO strings so BSON accepts it."""
    if isinstance(obj, dict):
        return {k: sanitize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_mongo(x) for x in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj

def compute_hash(prev_hash: str, record: dict, action: str, ts_iso: str) -> str:
    """Computes a SHA-256 hash over canonical payload including previous hash."""
    clean_record = sanitize_for_mongo(record)
    payload = json.dumps(
        {
            "prev": prev_hash,
            "record": clean_record,
            "action": action,
            "ts": ts_iso
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_record(source_table: str, record_id: str, record_dict: dict, action: str = "INSERT"):
    """
    Appends an immutable audit log to MongoDB AuditTrail collection.
    Chains the SHA-256 hash with the latest record in the collection.
    """
    db = get_mongo_db()
    # Find the latest audit entry by insertion order / timestamp
    latest = db.AuditTrail.find_one(sort=[("_id", -1)])
    prev_hash = latest["curr_hash"] if latest else GENESIS_HASH

    ts_iso = datetime.datetime.utcnow().isoformat()
    clean_snapshot = sanitize_for_mongo(record_dict)
    curr_hash = compute_hash(prev_hash, clean_snapshot, action, ts_iso)

    audit_entry = {
        "record_id": record_id,
        "source_table": source_table,
        "prev_hash": prev_hash,
        "curr_hash": curr_hash,
        "timestamp": ts_iso,
        "action": action,
        "record_snapshot": clean_snapshot
    }

    db.AuditTrail.insert_one(audit_entry)
    audit_entry.pop("_id", None)
    return audit_entry

def verify_audit_chain():
    """
    Traverses the AuditTrail collection from first to last:
    1. Verifies that each entry's prev_hash equals the previous entry's curr_hash.
    2. Recomputes curr_hash over the snapshot to verify it has not been altered in MongoDB.
    Returns: {"intact": True, "total_records": N} or details of the first tampered entry.
    """
    db = get_mongo_db()
    records = list(db.AuditTrail.find().sort("_id", 1))

    if not records:
        return {"intact": True, "total_records": 0, "message": "Audit trail is empty (Genesis state)"}

    expected_prev = GENESIS_HASH

    for idx, doc in enumerate(records):
        doc_prev = doc.get("prev_hash")
        doc_curr = doc.get("curr_hash")
        snapshot = doc.get("record_snapshot", {})
        action = doc.get("action", "")
        ts = doc.get("timestamp", "")

        # Check 1: Chain link
        if doc_prev != expected_prev:
            return {
                "intact": False,
                "broken_at_index": idx,
                "record_id": doc.get("record_id"),
                "reason": f"Chain link broken: expected prev_hash '{expected_prev}', found '{doc_prev}'"
            }

        # Check 2: Hash integrity
        recalculated = compute_hash(doc_prev, snapshot, action, ts)
        if recalculated != doc_curr:
            return {
                "intact": False,
                "broken_at_index": idx,
                "record_id": doc.get("record_id"),
                "reason": f"Content tampered: stored curr_hash '{doc_curr}' does not match recalculated '{recalculated}'"
            }

        expected_prev = doc_curr

    return {
        "intact": True,
        "total_records": len(records),
        "latest_hash": expected_prev,
        "message": f"All {len(records)} audit records verified successfully. Chain is intact and tamper-evident."
    }

def get_recent_audit_logs(limit: int = 50):
    db = get_mongo_db()
    logs = list(db.AuditTrail.find({}, {"_id": 0}).sort("_id", -1).limit(limit))
    return logs
