import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "canteen_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def test_mysql_connection():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            res = cur.fetchone()
        conn.close()
        return {"status": "ok", "message": "Connected to MySQL successfully", "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_food_items():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT item_id, name, category, unit, standard_recipe_cost FROM food_item ORDER BY name ASC")
            return cur.fetchall()

def get_staff_list():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT staff_id, name, role, shift, username FROM staff ORDER BY name ASC")
            return cur.fetchall()

def get_vendors():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT vendor_id, name, contact, item_category_supplied FROM vendor ORDER BY name ASC")
            return cur.fetchall()

def get_raw_materials():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT material_id, name, unit, perishable FROM raw_material ORDER BY name ASC")
            return cur.fetchall()

def get_or_create_meal(meal_date: str, meal_type: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT meal_id FROM meal WHERE meal_date = %s AND meal_type = %s", (meal_date, meal_type))
            row = cur.fetchone()
            if row:
                return row["meal_id"]
            cur.execute("INSERT INTO meal (meal_date, meal_type) VALUES (%s, %s)", (meal_date, meal_type))
            return cur.lastrowid

def record_meal_log(meal_date: str, meal_type: str, item_id: int, staff_id: int,
                    qty_prepared: int, qty_sold: int, price_per_unit: float, customer_count_est: int = None):
    meal_id = get_or_create_meal(meal_date, meal_type)
    with get_connection() as conn:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO meal_log (meal_id, item_id, staff_id, qty_prepared, qty_sold, price_per_unit, customer_count_est)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    staff_id = VALUES(staff_id),
                    qty_prepared = VALUES(qty_prepared),
                    qty_sold = VALUES(qty_sold),
                    price_per_unit = VALUES(price_per_unit),
                    customer_count_est = VALUES(customer_count_est)
            """
            cur.execute(sql, (meal_id, item_id, staff_id, qty_prepared, qty_sold, price_per_unit, customer_count_est))
            log_id = cur.lastrowid
            
            # Fetch the canonical inserted row (including generated leftover_qty)
            cur.execute("""
                SELECT ml.*, fi.name AS item_name, m.meal_date, m.meal_type
                FROM meal_log ml
                JOIN food_item fi ON fi.item_id = ml.item_id
                JOIN meal m ON m.meal_id = ml.meal_id
                WHERE ml.meal_id = %s AND ml.item_id = %s
            """, (meal_id, item_id))
            return cur.fetchone()

def record_wastage_log(log_id: int, qty_wasted: int, reason_code: str, disposal_method: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check leftover and any previously recorded wastage for this meal log
            cur.execute("""
                SELECT ml.leftover_qty, COALESCE(SUM(w.qty_wasted), 0) AS already_wasted
                FROM meal_log ml
                LEFT JOIN wastage_log w ON w.log_id = ml.log_id
                WHERE ml.log_id = %s
                GROUP BY ml.leftover_qty
            """, (log_id,))
            ml = cur.fetchone()
            if not ml:
                raise ValueError(f"Meal log #{log_id} does not exist.")
            
            remaining = ml["leftover_qty"] - int(ml["already_wasted"])
            if remaining <= 0:
                raise ValueError(f"All {ml['leftover_qty']} units of leftover for meal #{log_id} have already been accounted for.")
            if qty_wasted > remaining:
                raise ValueError(f"Cannot log {qty_wasted} units of waste. Only {remaining} units of leftover remain unaccounted for (Total leftover: {ml['leftover_qty']}, Already logged: {ml['already_wasted']}).")

            sql = """
                INSERT INTO wastage_log (log_id, qty_wasted, reason_code, disposal_method)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql, (log_id, qty_wasted, reason_code, disposal_method))
            wastage_id = cur.lastrowid
            cur.execute("SELECT * FROM wastage_log WHERE wastage_id = %s", (wastage_id,))
            return cur.fetchone()

def record_purchase(vendor_id: int, material_id: int, purchase_date: str,
                    qty_purchased: float, cost: float, batch_no: str = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO purchase (vendor_id, material_id, purchase_date, qty_purchased, cost, batch_no)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (vendor_id, material_id, purchase_date, qty_purchased, cost, batch_no))
            pid = cur.lastrowid
            cur.execute("""
                SELECT p.*, v.name AS vendor_name, rm.name AS material_name
                FROM purchase p
                JOIN vendor v ON v.vendor_id = p.vendor_id
                JOIN raw_material rm ON rm.material_id = p.material_id
                WHERE p.purchase_id = %s
            """, (pid,))
            return cur.fetchone()

# Analytical View Queries
def get_weekday_leftover_report():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM view_weekday_leftover_pct")
            return cur.fetchall()

def get_recent_weekly_wastage():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM view_recent_weekly_wastage")
            return cur.fetchall()

def get_monthly_vendor_spend():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM view_monthly_vendor_spend")
            return cur.fetchall()

def get_consecutive_high_leftover_items():
    """Finds items with leftover > 20% on each of their last 3 serving days using window functions."""
    query = """
    WITH daily AS (
      SELECT ml.item_id, fi.name AS item_name, m.meal_date,
             100.0 * SUM(ml.leftover_qty) / NULLIF(SUM(ml.qty_prepared), 0) AS leftover_pct
      FROM meal_log ml
      JOIN meal m ON m.meal_id = ml.meal_id
      JOIN food_item fi ON fi.item_id = ml.item_id
      GROUP BY ml.item_id, fi.name, m.meal_date
    ), flagged AS (
      SELECT item_id, item_name, meal_date, leftover_pct,
             SUM(CASE WHEN leftover_pct > 20.0 THEN 1 ELSE 0 END) OVER (
                 PARTITION BY item_id ORDER BY meal_date
                 ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
             ) AS hits
      FROM daily
    )
    SELECT item_id, item_name, meal_date, ROUND(leftover_pct, 1) AS leftover_pct
    FROM flagged WHERE hits = 3
    ORDER BY meal_date DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

def get_meal_logs_for_date(meal_date: str):
    query = """
        SELECT ml.log_id, m.meal_date, m.meal_type, fi.name AS item_name,
               ml.qty_prepared, ml.qty_sold, ml.leftover_qty, ml.price_per_unit,
               s.name AS logged_by,
               COALESCE(SUM(w.qty_wasted), 0) AS total_wasted,
               (ml.leftover_qty - COALESCE(SUM(w.qty_wasted), 0)) AS remaining_leftover
        FROM meal_log ml
        JOIN meal m ON m.meal_id = ml.meal_id
        JOIN food_item fi ON fi.item_id = ml.item_id
        JOIN staff s ON s.staff_id = ml.staff_id
        LEFT JOIN wastage_log w ON w.log_id = ml.log_id
        WHERE m.meal_date = %s
        GROUP BY ml.log_id, m.meal_date, m.meal_type, fi.name,
                 ml.qty_prepared, ml.qty_sold, ml.leftover_qty, ml.price_per_unit, s.name
        ORDER BY m.meal_type, fi.name;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (meal_date,))
            return cur.fetchall()

def clear_operational_logs():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE wastage_log;")
            cur.execute("TRUNCATE TABLE meal_log;")
            cur.execute("TRUNCATE TABLE meal;")
            cur.execute("TRUNCATE TABLE purchase;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            return {"status": "ok", "message": "MySQL operational logs cleared."}


