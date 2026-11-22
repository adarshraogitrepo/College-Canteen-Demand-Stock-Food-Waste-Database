-- =====================================================================
-- 001_schema.sql: College Canteen Demand, Stock & Food-Waste Database
-- Target Engine: MySQL 8.0+
-- Deliverable: Relational Schema in 3NF with constraints and foreign keys
-- =====================================================================

CREATE DATABASE IF NOT EXISTS canteen_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE canteen_db;

-- 1. Staff / User accounts (D1)
CREATE TABLE IF NOT EXISTS staff (
  staff_id      INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(80)  NOT NULL,
  role          ENUM('manager', 'chef', 'helper', 'counter') NOT NULL,
  shift         ENUM('morning', 'afternoon', 'evening') NOT NULL,
  username      VARCHAR(40)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- 2. Food items offered by the canteen (D2)
CREATE TABLE IF NOT EXISTS food_item (
  item_id              INT AUTO_INCREMENT PRIMARY KEY,
  name                 VARCHAR(80) NOT NULL UNIQUE,
  category             ENUM('veg', 'non_veg', 'beverage', 'snack') NOT NULL,
  unit                 VARCHAR(20) NOT NULL, -- e.g. plate, piece, cup
  standard_recipe_cost DECIMAL(8,2) NOT NULL CHECK (standard_recipe_cost >= 0)
) ENGINE=InnoDB;

-- 3. Raw materials procured for recipes (D2)
CREATE TABLE IF NOT EXISTS raw_material (
  material_id INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(80) NOT NULL UNIQUE,
  unit        VARCHAR(20) NOT NULL, -- e.g. kg, litre, piece
  perishable  BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;

-- 4. Recipe materials: M:N relationship REQUIRES (FOOD_ITEM <-> RAW_MATERIAL)
CREATE TABLE IF NOT EXISTS recipe_material (
  item_id                INT NOT NULL,
  material_id            INT NOT NULL,
  qty_required_per_unit  DECIMAL(10,3) NOT NULL CHECK (qty_required_per_unit > 0),
  PRIMARY KEY (item_id, material_id),
  FOREIGN KEY (item_id)     REFERENCES food_item(item_id)    ON DELETE CASCADE,
  FOREIGN KEY (material_id) REFERENCES raw_material(material_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 5. Raw material suppliers/vendors (D3)
CREATE TABLE IF NOT EXISTS vendor (
  vendor_id              INT AUTO_INCREMENT PRIMARY KEY,
  name                   VARCHAR(80) NOT NULL,
  contact                VARCHAR(20),
  item_category_supplied VARCHAR(60)
) ENGINE=InnoDB;

-- 6. Meal sessions (D4)
CREATE TABLE IF NOT EXISTS meal (
  meal_id   INT AUTO_INCREMENT PRIMARY KEY,
  meal_date DATE NOT NULL,
  meal_type ENUM('breakfast', 'lunch', 'snacks', 'dinner') NOT NULL,
  UNIQUE KEY uq_meal_date_type (meal_date, meal_type)
) ENGINE=InnoDB;

-- 7. Meal Log: Weak entity dependent on MEAL (D4)
CREATE TABLE IF NOT EXISTS meal_log (
  log_id             INT AUTO_INCREMENT PRIMARY KEY,
  meal_id            INT NOT NULL,
  item_id            INT NOT NULL,
  staff_id           INT NOT NULL,
  qty_prepared       INT NOT NULL CHECK (qty_prepared >= 0),
  qty_sold           INT NOT NULL CHECK (qty_sold >= 0),
  leftover_qty       INT GENERATED ALWAYS AS (qty_prepared - qty_sold) STORED,
  price_per_unit     DECIMAL(8,2) NOT NULL CHECK (price_per_unit >= 0),
  customer_count_est INT CHECK (customer_count_est IS NULL OR customer_count_est >= 0),
  UNIQUE KEY uq_meal_item (meal_id, item_id),
  CHECK (qty_sold <= qty_prepared),
  FOREIGN KEY (meal_id)  REFERENCES meal(meal_id)       ON DELETE CASCADE,
  FOREIGN KEY (item_id)  REFERENCES food_item(item_id)  ON DELETE RESTRICT,
  FOREIGN KEY (staff_id) REFERENCES staff(staff_id)     ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 8. Wastage Log: Weak entity dependent on MEAL_LOG (D5)
CREATE TABLE IF NOT EXISTS wastage_log (
  wastage_id      INT AUTO_INCREMENT PRIMARY KEY,
  log_id          INT NOT NULL,
  qty_wasted      INT NOT NULL CHECK (qty_wasted > 0),
  reason_code     ENUM('spoiled', 'over_prepared', 'quality_issue', 'other') NOT NULL,
  disposal_method ENUM('discarded', 'composted', 'donated', 'animal_feed', 'other') NOT NULL,
  FOREIGN KEY (log_id) REFERENCES meal_log(log_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Purchase of raw materials from vendors (D6)
-- APPROVED FIX: Linked to raw_material (material_id), not finished food_item
CREATE TABLE IF NOT EXISTS purchase (
  purchase_id   INT AUTO_INCREMENT PRIMARY KEY,
  vendor_id     INT NOT NULL,
  material_id   INT NOT NULL,
  purchase_date DATE NOT NULL,
  qty_purchased DECIMAL(10,2) NOT NULL CHECK (qty_purchased > 0),
  cost          DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
  batch_no      VARCHAR(30),
  FOREIGN KEY (vendor_id)   REFERENCES vendor(vendor_id)         ON DELETE RESTRICT,
  FOREIGN KEY (material_id) REFERENCES raw_material(material_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

