-- =====================================================================
-- seed_dummy_DO_NOT_SUBMIT.sql
-- WARNING: Development and testing dummy data only.
-- Do NOT submit this file as collected data in your final report.
-- =====================================================================

USE canteen_db;

-- 1. Insert Staff (Manager, Chef, Counter, Helper)
-- (Passwords are placeholders; in production/backend these will be bcrypt hashes)
INSERT INTO staff (staff_id, name, role, shift, username, password_hash) VALUES
(1, 'Ramesh Kumar', 'manager', 'morning', 'ramesh_mgr', '$2b$12$eXampleHashPlaceHolderManager123'),
(2, 'Suresh Sharma', 'chef', 'morning', 'suresh_chef', '$2b$12$eXampleHashPlaceHolderChef123'),
(3, 'Anita Devi', 'counter', 'afternoon', 'anita_counter', '$2b$12$eXampleHashPlaceHolderCounter123'),
(4, 'Manoj Gowda', 'helper', 'evening', 'manoj_helper', '$2b$12$eXampleHashPlaceHolderHelper123')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Insert Food Items (Menu)
INSERT INTO food_item (item_id, name, category, unit, standard_recipe_cost) VALUES
(1, 'Masala Dosa', 'snack', 'plate', 25.00),
(2, 'Veg Meals (Thali)', 'veg', 'plate', 40.00),
(3, 'Chicken Biryani', 'non_veg', 'plate', 75.00),
(4, 'Filter Coffee', 'beverage', 'cup', 10.00),
(5, 'Samosa', 'snack', 'piece', 12.00)
ON DUPLICATE KEY UPDATE standard_recipe_cost=VALUES(standard_recipe_cost);

-- 3. Insert Raw Materials
INSERT INTO raw_material (material_id, name, unit, perishable) VALUES
(1, 'Rice (Sona Masoori)', 'kg', FALSE),
(2, 'Toor Dal', 'kg', FALSE),
(3, 'Cooking Oil', 'litre', FALSE),
(4, 'Potatoes', 'kg', TRUE),
(5, 'Chicken (Fresh)', 'kg', TRUE),
(6, 'Milk', 'litre', TRUE),
(7, 'Coffee Powder', 'kg', FALSE)
ON DUPLICATE KEY UPDATE perishable=VALUES(perishable);

-- 4. Insert Recipe Materials (M:N linking)
INSERT INTO recipe_material (item_id, material_id, qty_required_per_unit) VALUES
-- Masala Dosa: 0.08 kg Rice, 0.05 kg Potatoes, 0.01 L Oil
(1, 1, 0.080),
(1, 4, 0.050),
(1, 3, 0.010),
-- Veg Meals: 0.15 kg Rice, 0.04 kg Toor Dal, 0.02 L Oil
(2, 1, 0.150),
(2, 2, 0.040),
(2, 3, 0.020),
-- Chicken Biryani: 0.18 kg Rice, 0.20 kg Chicken, 0.03 L Oil
(3, 1, 0.180),
(3, 5, 0.200),
(3, 3, 0.030),
-- Filter Coffee: 0.015 kg Coffee Powder, 0.100 L Milk
(4, 7, 0.015),
(4, 6, 0.100)
ON DUPLICATE KEY UPDATE qty_required_per_unit=VALUES(qty_required_per_unit);

-- 5. Insert Vendors
INSERT INTO vendor (vendor_id, name, contact, item_category_supplied) VALUES
(1, 'Sri Lakshmi Groceries', '9876543210', 'Grains, Dals, Spices'),
(2, 'Green Valley Vegetables', '9876543211', 'Fresh Vegetables'),
(3, 'Nandini Milk Agency', '9876543212', 'Dairy Products'),
(4, 'City Poultry Farms', '9876543213', 'Chicken & Eggs')
ON DUPLICATE KEY UPDATE contact=VALUES(contact);

-- 6. Insert Raw Material Purchases
INSERT INTO purchase (purchase_id, vendor_id, material_id, purchase_date, qty_purchased, cost, batch_no) VALUES
(1, 1, 1, '2026-11-15', 100.00, 4800.00, 'BATCH-RICE-01'),
(2, 1, 2, '2026-11-15', 50.00, 6000.00, 'BATCH-DAL-01'),
(3, 2, 4, '2026-11-18', 40.00, 1200.00, 'BATCH-POT-03'),
(4, 3, 6, '2026-11-19', 30.00, 1500.00, 'BATCH-MILK-19'),
(5, 4, 5, '2026-11-20', 25.00, 4500.00, 'BATCH-CHK-20')
ON DUPLICATE KEY UPDATE cost=VALUES(cost);

-- 7. Insert Meals (Breakfast, Lunch, etc.)
INSERT INTO meal (meal_id, meal_date, meal_type) VALUES
(1, '2026-11-18', 'breakfast'),
(2, '2026-11-18', 'lunch'),
(3, '2026-11-19', 'breakfast'),
(4, '2026-11-19', 'lunch'),
(5, '2026-11-20', 'lunch')
ON DUPLICATE KEY UPDATE meal_date=VALUES(meal_date);

-- 8. Insert Meal Logs (Quantities prepared & sold; leftover_qty is auto-computed!)
INSERT INTO meal_log (log_id, meal_id, item_id, staff_id, qty_prepared, qty_sold, price_per_unit, customer_count_est) VALUES
-- 2026-11-18 Breakfast: Dosa & Coffee
(1, 1, 1, 2, 80, 72, 35.00, 65),     -- Leftover = 8
(2, 1, 4, 2, 100, 95, 15.00, 90),    -- Leftover = 5
-- 2026-11-18 Lunch: Veg Meals & Biryani
(3, 2, 2, 2, 120, 90, 60.00, 85),    -- Leftover = 30
(4, 2, 3, 2, 60, 58, 120.00, 55),    -- Leftover = 2
-- 2026-11-19 Breakfast
(5, 3, 1, 2, 90, 85, 35.00, 80),     -- Leftover = 5
-- 2026-11-19 Lunch (Rainy day / lower turnout)
(6, 4, 2, 2, 130, 80, 60.00, 75),    -- Leftover = 50 (High wastage)
(7, 4, 3, 2, 70, 50, 120.00, 48),    -- Leftover = 20
-- 2026-11-20 Lunch
(8, 5, 2, 2, 110, 98, 60.00, 92),    -- Leftover = 12
(9, 5, 3, 2, 65, 61, 120.00, 59)     -- Leftover = 4
ON DUPLICATE KEY UPDATE qty_sold=VALUES(qty_sold);

-- 9. Insert Wastage Logs (wasted portion of leftovers)
INSERT INTO wastage_log (wastage_id, log_id, qty_wasted, reason_code, disposal_method) VALUES
(1, 1, 6, 'over_prepared', 'discarded'),
(2, 3, 25, 'over_prepared', 'animal_feed'),
(3, 6, 45, 'over_prepared', 'composted'),
(4, 7, 18, 'spoiled', 'discarded'),
(5, 8, 10, 'over_prepared', 'animal_feed')
ON DUPLICATE KEY UPDATE qty_wasted=VALUES(qty_wasted);

