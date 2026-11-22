# College Canteen Demand, Stock & Food-Waste Database System

> A hybrid relational (MySQL 8) and document (MongoDB) database management system designed to optimize canteen preparation, record food wastage, manage procurement, and maintain a tamper-evident audit trail.
> 
> **Course:** Database Management Systems (Theory and Lab), Code: **CD252IA**  
> **Target Alignment:** UN Sustainable Development Goal 12.3 (Food Waste Reduction)

---

## 🏗️ System Architecture

The system implements a dual-store architecture according to data structure needs:

1. **Relational Layer (MySQL 8 — Normalized to 3NF):**
   - **Master Data:** Staff accounts, food items (menu), raw materials, recipe compositions, vendors.
   - **Transactional Data:** Daily meal sessions, item-level preparation and sales logs, food wastage records, raw-material purchase invoices.
   - **Database-Enforced Integrity:** `CHECK (qty_sold <= qty_prepared)`, non-negative costs, stored generated column for `leftover_qty`, and cascading referential integrity.
2. **Document Layer (MongoDB):**
   - `DailyContext`: Variable external factors (weather, exam periods, holidays, campus events).
   - `FeedbackNotes`: Unstructured customer and staff feedback with keyword-matched tags.
   - `AuditTrail`: Append-only, SHA-256 hash-chained block records ensuring tamper-evident tracking.
3. **Application & API Layer:**
   - Python FastAPI server providing parameterized SQL queries and cross-store data correlation.
4. **User Interface:**
   - Single-page interface for meal logging, wastage recording, context logging, analytical reports, and live cryptographic audit verification.

---

## 🚀 Key Features

- **Engine-Computed Derived Attributes:** Leftovers are computed directly on disk by MySQL (`leftover_qty = qty_prepared - qty_sold`).
- **Cryptographic Audit Trail:** Blockchain-inspired SHA-256 hash chaining where every transaction block references the previous block's hash. A built-in verification algorithm verifies chain continuity and detects tampering.
- **Explainable Analytics (No ML):** Operational insights using pure SQL Views, aggregations, and window functions (`OVER (PARTITION BY ... ROWS BETWEEN ...)`).
- **Cross-Store Joins:** Queries MongoDB for campus exam dates and correlates them against MySQL meal logs to analyze wastage variations during exam seasons.
- **Recipe Explosion (M:N Relationship):** Normalizes dish-ingredient mapping via an associative entity (`recipe_material`) to compute raw stock consumption.

---

## 📁 Repository Structure

```
├── db/
│   ├── 001_schema.sql                 # 3NF DDL schema with constraints and foreign keys
│   ├── 002_views.sql                  # Analytical SQL views (leftover %, wastage, vendor spend)
│   ├── seed_dummy_DO_NOT_SUBMIT.sql   # Development test data (not to be submitted as collected data)
│   └── mongo_init.js                  # MongoDB collection and unique index setup
├── backend/
│   ├── main.py                        # FastAPI endpoints and static mount
│   ├── sql.py                         # Parameterized MySQL database connector
│   ├── mongo.py                       # MongoDB connector and keyword-based feedback tagger
│   └── audit.py                       # SHA-256 hash-chain algorithm and chain validator
├── frontend/
│   ├── index.html                     # Responsive single-page dashboard
│   ├── style.css                      # Modern CSS layout
│   └── app.js                         # API integration and real-time validation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Sample environment configuration
├── .gitignore                         # Git exclusion rules
├── PROJECT_CONTEXT.md                 # Single source of truth & course documentation
└── README.md
```

---

## 🛠️ Quick Setup Guide

### 1. Prerequisites
- **MySQL Server 8.0+** & **MySQL Workbench**
- **MongoDB Community Server** & **MongoDB Compass**
- **Python 3.10+**

### 2. Database Initialization
1. In **MySQL Workbench**, open and execute:
   - `db/001_schema.sql` (Creates database `canteen_db` and tables)
   - `db/002_views.sql` (Creates analytical views)
   - *(Optional for testing)*: `db/seed_dummy_DO_NOT_SUBMIT.sql`
2. In **MongoDB Compass**, connect to `mongodb://localhost:27017/` and create:
   - Database: `canteen_nosql`
   - Collections: `DailyContext`, `FeedbackNotes`, `AuditTrail`
   - Add a Unique Index on `DailyContext.date`

### 3. Backend Setup
1. Clone the repository and navigate to the root directory:
   ```bash
   git clone https://github.com/adarshraogitrepo/College-Canteen-Demand-Stock-Food-Waste-Database.git
   cd College-Canteen-Demand-Stock-Food-Waste-Database
   ```
2. Create and configure your `.env` file:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=canteen_db

   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DATABASE=canteen_nosql
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```
5. Open your browser at **`http://localhost:8000`**.

