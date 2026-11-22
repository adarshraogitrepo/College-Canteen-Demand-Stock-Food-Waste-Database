import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.sql import (
    test_mysql_connection, get_food_items, get_staff_list,
    get_vendors, get_raw_materials, record_meal_log, record_wastage_log,
    record_purchase, get_weekday_leftover_report, get_recent_weekly_wastage,
    get_monthly_vendor_spend, get_consecutive_high_leftover_items,
    get_meal_logs_for_date, get_connection, clear_operational_logs
)
from backend.mongo import (
    test_mongo_connection, upsert_daily_context, get_daily_context,
    get_all_contexts, add_feedback_note, get_feedback_for_log, clear_mongo_logs
)
from backend.audit import (
    append_audit_record, verify_audit_chain, get_recent_audit_logs
)

app = FastAPI(
    title="College Canteen Demand, Stock & Food-Waste Database System",
    description="Integrated MySQL + MongoDB backend with SHA-256 hash-chain audit trail.",
    version="1.0.0"
)

# CORS middleware for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------------
class MealLogRequest(BaseModel):
    meal_date: str = Field(..., example="2026-11-22")
    meal_type: str = Field(..., example="lunch") # breakfast, lunch, snacks, dinner
    item_id: int
    staff_id: int
    qty_prepared: int = Field(..., ge=0)
    qty_sold: int = Field(..., ge=0)
    price_per_unit: float = Field(..., ge=0)
    customer_count_est: Optional[int] = None

class WastageLogRequest(BaseModel):
    log_id: int
    qty_wasted: int = Field(..., gt=0)
    reason_code: str # spoiled, over_prepared, quality_issue, other
    disposal_method: str # discarded, composted, donated, animal_feed, other

class PurchaseRequest(BaseModel):
    vendor_id: int
    material_id: int
    purchase_date: str = Field(..., example="2026-11-22")
    qty_purchased: float = Field(..., gt=0)
    cost: float = Field(..., ge=0)
    batch_no: Optional[str] = None

class DailyContextRequest(BaseModel):
    date: str
    weather: str = "sunny"
    is_holiday: bool = False
    exam_period: bool = False
    special_event: Optional[str] = ""
    notes: Optional[str] = ""

class FeedbackRequest(BaseModel):
    log_id: int
    staff_id: Optional[int] = None
    source: str = "staff" # staff or student
    note_text: str

# -------------------------------------------------------------
# Health Check & Master Data
# -------------------------------------------------------------
@app.get("/api/health")
def health_check():
    mysql_stat = test_mysql_connection()
    mongo_stat = test_mongo_connection()
    return {
        "status": "online",
        "mysql": mysql_stat,
        "mongodb": mongo_stat
    }

@app.get("/api/master/items")
def list_items():
    return get_food_items()

@app.get("/api/master/staff")
def list_staff():
    return get_staff_list()

@app.get("/api/master/vendors")
def list_vendors():
    return get_vendors()

@app.get("/api/master/raw-materials")
def list_raw_materials():
    return get_raw_materials()

# -------------------------------------------------------------
# Operational Data Entry (with Tamper-Evident Audit Logging)
# -------------------------------------------------------------
@app.post("/api/meals/log")
def create_meal_log(req: MealLogRequest):
    if req.qty_sold > req.qty_prepared:
        raise HTTPException(
            status_code=400,
            detail="Business Rule Violation: Quantity sold cannot exceed quantity prepared."
        )
    try:
        saved_row = record_meal_log(
            meal_date=req.meal_date,
            meal_type=req.meal_type,
            item_id=req.item_id,
            staff_id=req.staff_id,
            qty_prepared=req.qty_prepared,
            qty_sold=req.qty_sold,
            price_per_unit=req.price_per_unit,
            customer_count_est=req.customer_count_est
        )
        
        # Tamper-Evident Audit Logging in MongoDB
        record_id = f"meal_log:{saved_row['log_id']}"
        audit_entry = append_audit_record(
            source_table="meal_log",
            record_id=record_id,
            record_dict=saved_row,
            action="INSERT/UPDATE"
        )
        
        return {
            "status": "success",
            "meal_log": saved_row,
            "audit_hash": audit_entry["curr_hash"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meals/wastage")
def create_wastage_log(req: WastageLogRequest):
    try:
        saved_row = record_wastage_log(
            log_id=req.log_id,
            qty_wasted=req.qty_wasted,
            reason_code=req.reason_code,
            disposal_method=req.disposal_method
        )
        # Tamper-Evident Audit Logging
        record_id = f"wastage_log:{saved_row['wastage_id']}"
        audit_entry = append_audit_record(
            source_table="wastage_log",
            record_id=record_id,
            record_dict=saved_row,
            action="INSERT"
        )
        return {
            "status": "success",
            "wastage_log": saved_row,
            "audit_hash": audit_entry["curr_hash"]
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/purchases")
def create_purchase(req: PurchaseRequest):
    try:
        saved_row = record_purchase(
            vendor_id=req.vendor_id,
            material_id=req.material_id,
            purchase_date=req.purchase_date,
            qty_purchased=req.qty_purchased,
            cost=req.cost,
            batch_no=req.batch_no
        )
        # Tamper-Evident Audit Logging
        record_id = f"purchase:{saved_row['purchase_id']}"
        audit_entry = append_audit_record(
            source_table="purchase",
            record_id=record_id,
            record_dict=saved_row,
            action="INSERT"
        )
        return {
            "status": "success",
            "purchase": saved_row,
            "audit_hash": audit_entry["curr_hash"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meals/daily/{meal_date}")
def get_daily_meal_logs(meal_date: str):
    return get_meal_logs_for_date(meal_date)

# -------------------------------------------------------------
# MongoDB Context & Feedback
# -------------------------------------------------------------
@app.post("/api/context")
def save_daily_context(req: DailyContextRequest):
    return upsert_daily_context(
        date_str=req.date,
        weather=req.weather,
        is_holiday=req.is_holiday,
        exam_period=req.exam_period,
        special_event=req.special_event,
        notes=req.notes
    )

@app.get("/api/context/{date_str}")
def get_context_for_date(date_str: str):
    ctx = get_daily_context(date_str)
    return ctx or {}

@app.get("/api/context")
def list_all_contexts():
    return get_all_contexts()

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    return add_feedback_note(
        log_id=req.log_id,
        staff_id=req.staff_id,
        source=req.source,
        note_text=req.note_text
    )

@app.get("/api/feedback/{log_id}")
def list_feedback_for_log(log_id: int):
    return get_feedback_for_log(log_id)

# -------------------------------------------------------------
# Reporting & Insights (Views, Window Functions & Cross-Store Join)
# -------------------------------------------------------------
@app.get("/api/reports/weekday-leftover")
def report_weekday_leftover():
    return get_weekday_leftover_report()

@app.get("/api/reports/weekly-wastage")
def report_weekly_wastage():
    return get_recent_weekly_wastage()

@app.get("/api/reports/vendor-spend")
def report_vendor_spend():
    return get_monthly_vendor_spend()

@app.get("/api/reports/consecutive-anomalies")
def report_anomalies():
    return get_consecutive_high_leftover_items()

@app.get("/api/reports/exam-context-analysis")
def report_exam_context():
    """
    Demonstrates Cross-Store Analysis (MySQL + MongoDB):
    Fetches dates from MongoDB where exam_period is True, then passes them
    to MySQL with parameterized IN clause to compare exam vs regular days.
    """
    all_contexts = get_all_contexts()
    exam_dates = [c["date"] for c in all_contexts if c.get("exam_period")]

    with get_connection() as conn:
        with conn.cursor() as cur:
            if exam_dates:
                format_strings = ','.join(['%s'] * len(exam_dates))
                query = f"""
                    SELECT 
                        CASE WHEN m.meal_date IN ({format_strings}) THEN 'Exam Period' ELSE 'Normal Days' END AS period_type,
                        COUNT(DISTINCT m.meal_id) AS total_meals,
                        ROUND(AVG(ml.leftover_qty * 100.0 / NULLIF(ml.qty_prepared, 0)), 1) AS avg_leftover_pct
                    FROM meal_log ml
                    JOIN meal m ON m.meal_id = ml.meal_id
                    GROUP BY period_type
                """
                cur.execute(query, tuple(exam_dates))
            else:
                query = """
                    SELECT 'All Days' AS period_type,
                           COUNT(DISTINCT m.meal_id) AS total_meals,
                           ROUND(AVG(ml.leftover_qty * 100.0 / NULLIF(ml.qty_prepared, 0)), 1) AS avg_leftover_pct
                    FROM meal_log ml
                    JOIN meal m ON m.meal_id = ml.meal_id
                    GROUP BY period_type
                """
                cur.execute(query)
            comparison = cur.fetchall()

    return {
        "exam_dates_in_mongo": exam_dates,
        "comparison": comparison
    }

# -------------------------------------------------------------
# Tamper-Evidence & Audit Verification
# -------------------------------------------------------------
@app.get("/api/audit/verify")
def verify_audit():
    """Traverses MongoDB audit trail and validates SHA-256 chain and integrity."""
    return verify_audit_chain()

@app.get("/api/audit/logs")
def fetch_audit_logs(limit: int = 50):
    return get_recent_audit_logs(limit)

@app.delete("/api/admin/clear-logs")
def clear_all_operational_logs():
    sql_res = clear_operational_logs()
    mongo_res = clear_mongo_logs()
    return {
        "status": "success",
        "message": "All operational logs (meals, wastage, purchases, audit trail, feedback, context) cleared. Master data preserved.",
        "mysql": sql_res,
        "mongodb": mongo_res
    }

# -------------------------------------------------------------
# Serve Frontend Static Files
# -------------------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

