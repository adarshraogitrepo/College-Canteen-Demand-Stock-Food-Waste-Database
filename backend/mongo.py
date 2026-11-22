import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DATABASE", "canteen_nosql")

def get_mongo_db():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return client[MONGODB_DB_NAME]

def test_mongo_connection():
    try:
        db = get_mongo_db()
        # Ping the server
        db.command("ping")
        return {"status": "ok", "message": "Connected to MongoDB successfully", "collections": db.list_collection_names()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 1. DailyContext Management
def upsert_daily_context(date_str: str, weather: str, is_holiday: bool,
                         exam_period: bool, special_event: str = "", notes: str = ""):
    db = get_mongo_db()
    doc = {
        "date": date_str,
        "weather": weather,
        "is_holiday": bool(is_holiday),
        "exam_period": bool(exam_period),
        "special_event": special_event,
        "notes": notes,
        "updated_at": datetime.utcnow()
    }
    res = db.DailyContext.update_one(
        {"date": date_str},
        {"$set": doc},
        upsert=True
    )
    return {"date": date_str, "upserted": res.upserted_id is not None}

def get_daily_context(date_str: str):
    db = get_mongo_db()
    doc = db.DailyContext.find_one({"date": date_str}, {"_id": 0})
    return doc

def get_all_contexts():
    db = get_mongo_db()
    return list(db.DailyContext.find({}, {"_id": 0}).sort("date", -1))

# 2. FeedbackNotes Management
KEYWORD_TAGS = ["stale", "spoiled", "cold", "salty", "undercooked", "shortage", "finished", "overproduced", "queue", "late"]

def auto_tag_feedback(note_text: str):
    """Keyword-based tagging as required by DBMS Project rules (NO ML)."""
    text_lower = note_text.lower()
    matched = [kw for kw in KEYWORD_TAGS if kw in text_lower]
    return matched

def add_feedback_note(log_id: int, staff_id: int, source: str, note_text: str):
    db = get_mongo_db()
    tags = auto_tag_feedback(note_text)
    doc = {
        "log_id": int(log_id),
        "staff_id": int(staff_id) if staff_id else None,
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "note_text": note_text,
        "tags": tags
    }
    res = db.FeedbackNotes.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc

def get_feedback_for_log(log_id: int):
    db = get_mongo_db()
    notes = list(db.FeedbackNotes.find({"log_id": int(log_id)}, {"_id": 0}))
    return notes

