-- =====================================================================
-- 002_views.sql: Analytical Views for Canteen Management Insights
-- Target Engine: MySQL 8.0+
-- Deliverable: Reusable SQL Views demonstrating GROUP BY, Window Functions,
-- and Date aggregations without ML.
-- =====================================================================

USE canteen_db;

-- 1. View: Average Leftover Percentage per Item per Weekday
CREATE OR REPLACE VIEW view_weekday_leftover_pct AS
SELECT 
    fi.item_id,
    fi.name AS item_name,
    DAYNAME(m.meal_date) AS weekday,
    COUNT(ml.log_id) AS sessions_count,
    ROUND(AVG(ml.leftover_qty * 100.0 / NULLIF(ml.qty_prepared, 0)), 1) AS avg_leftover_pct
FROM meal_log ml
JOIN meal m       ON m.meal_id = ml.meal_id
JOIN food_item fi ON fi.item_id = ml.item_id
GROUP BY fi.item_id, fi.name, DAYNAME(m.meal_date)
ORDER BY avg_leftover_pct DESC;

-- 2. View: Most Wasted Food Items in the Last 7 Days
CREATE OR REPLACE VIEW view_recent_weekly_wastage AS
SELECT 
    fi.item_id,
    fi.name AS item_name,
    fi.category,
    SUM(w.qty_wasted) AS total_wasted_qty,
    fi.unit
FROM wastage_log w
JOIN meal_log ml  ON ml.log_id = w.log_id
JOIN meal m       ON m.meal_id = ml.meal_id
JOIN food_item fi ON fi.item_id = ml.item_id
WHERE m.meal_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY fi.item_id, fi.name, fi.category, fi.unit
ORDER BY total_wasted_qty DESC;

-- 3. View: Monthly Spend per Vendor
CREATE OR REPLACE VIEW view_monthly_vendor_spend AS
SELECT 
    v.vendor_id,
    v.name AS vendor_name,
    DATE_FORMAT(p.purchase_date, '%Y-%m') AS purchase_month,
    COUNT(p.purchase_id) AS total_orders,
    SUM(p.cost) AS total_spend
FROM purchase p
JOIN vendor v ON v.vendor_id = p.vendor_id
GROUP BY v.vendor_id, v.name, DATE_FORMAT(p.purchase_date, '%Y-%m')
ORDER BY purchase_month DESC, total_spend DESC;

