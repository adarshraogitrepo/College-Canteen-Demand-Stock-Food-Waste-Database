// =====================================================================
// mongo_init.js: MongoDB Collections & Indexes Initialization
// Run in mongosh or via MongoDB Compass
// =====================================================================

// Switch to (or create) canteen_nosql database
const dbName = "canteen_nosql";
const canteenDb = db.getSiblingDB(dbName);

// 1. DailyContext Collection
// Stores contextual variables: weather, exam period, holidays, special campus events
if (!canteenDb.getCollectionNames().includes("DailyContext")) {
  canteenDb.createCollection("DailyContext");
}
// Unique index on date ensures only one context record per calendar day
canteenDb.DailyContext.createIndex({ "date": 1 }, { unique: true });

// Sample document structure:
// {
//   "date": "2026-11-22",
//   "weather": "sunny",
//   "is_holiday": false,
//   "exam_period": true,
//   "special_event": "Inter-college Sports Meet",
//   "notes": "Higher evening footfall expected"
// }

// 2. FeedbackNotes Collection
// Stores unstructured notes from staff/students linked to a specific meal_log in SQL
if (!canteenDb.getCollectionNames().includes("FeedbackNotes")) {
  canteenDb.createCollection("FeedbackNotes");
}
canteenDb.FeedbackNotes.createIndex({ "log_id": 1 });
canteenDb.FeedbackNotes.createIndex({ "timestamp": -1 });

// Sample document structure:
// {
//   "log_id": 1,
//   "staff_id": 1,
//   "source": "staff",
//   "timestamp": new Date(),
//   "note_text": "Rice was slightly salty, customers gave feedback during lunch",
//   "tags": ["salty"]
// }

// 3. AuditTrail Collection
// Tamper-evident SHA-256 hash-chained log for meal_log, wastage_log, purchase
if (!canteenDb.getCollectionNames().includes("AuditTrail")) {
  canteenDb.createCollection("AuditTrail");
}
canteenDb.AuditTrail.createIndex({ "timestamp": 1 });
canteenDb.AuditTrail.createIndex({ "record_id": 1 });

// Sample genesis/first document:
// {
//   "record_id": "genesis",
//   "source_table": "system",
//   "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
//   "curr_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
//   "timestamp": new Date(),
//   "action": "INIT"
// }

print("canteen_nosql database and collections initialized successfully.");

