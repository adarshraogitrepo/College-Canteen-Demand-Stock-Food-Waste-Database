# PROJECT_CONTEXT.md — College Canteen Demand, Stock & Food-Waste Database

> Single source of truth for this project. Read it fully before writing any code.
> Status tags used below: **[DECIDED]** = agreed by the student, do not change without asking.
> **[SUGGESTED]** = recommended default, may be changed. **[OPEN]** = unresolved, ask before assuming.

---

## 0. Rules for the AI agent (read first)

1. **This is a DBMS course project, not an ML project.** Do not add machine-learning, deep-learning, or forecasting libraries or models. Insight comes from SQL views/queries and simple rules. [DECIDED]
2. **Database design is the main deliverable.** Keep the schema normalized to 3NF, keep the SQL + NoSQL split exactly as described in section 5. Do not "simplify" it into one store. [DECIDED]
3. **No special hardware, no blockchain infrastructure.** Tamper-evidence is a hash-chained audit log inside MongoDB (section 6.3). [DECIDED]
4. **Data must be real and self-collected** (entered by hand from the canteen). Synthetic seed data is allowed **only** for development/testing and must live in a clearly named file (`db/seed_dummy_DO_NOT_SUBMIT.sql`). Never present dummy rows as collected data. [DECIDED]
5. **Schema, ER diagram, DFDs and synopsis are already drafted and must stay consistent.** If you want to change a table, column, relationship or process, stop and ask first, and list which documents would need updating. [DECIDED]
6. **Security basics are mandatory** (syllabus asks for it): parameterised queries only, hashed passwords, role-based access, least-privilege DB users. See section 9.
7. Build in small, reviewable steps (one feature per commit) so weekly progress can be shown. Put every SQL change in `db/` as a numbered migration file.
8. Prefer plain, explainable code. The student must be able to explain every line in a viva.

---

## 1. Course and submission context

| Item | Detail |
|---|---|
| Course | Database Management Systems (Theory and Lab), code **CD252IA**, Semester V, Professional Core Course (common to CS & IS, AI, CD) |
| Credits / hours | 3:0:1, 45L + 30P |
| Marks | CIE 100 + 50, SEE 100 + 50 |
| Lab component | **Part A: open-ended mini project**, batch of **two students**, topic finalised **in consultation with faculty**, must be carried out **in the college only** |
| Reference text | Elmasri & Navathe, *Fundamentals of Database Systems*, 6th ed. (so use its ER/Chen notation conventions) |

**Mini project tasks required by the syllabus:**
- Understand the domain and derive the complete data requirement specification.
- Design the project with an **integrated SQL + NoSQL database solution**.
- **Normalize the relational design up to 3NF.**
- Appreciate the importance of **security** for database systems.
- Documentation and report submission.
- Use a **recent trend** (Blockchain, NLP, AI, ML, AR, VR etc.) and address **societal concern** issues.

**Guidelines from the syllabus:**
- Database: MySQL, DB2, Oracle, SQL Server, MongoDB (any NoSQL DB), or any DBMS tool.
- Front end: Java, VC++, C#, Python, or web interface (HTML, JavaScript).
- Use database programming such as Embedded SQL / Dynamic SQL / SQLJ.

**Course outcomes the project should demonstrate:**
CO1 understand relational, NoSQL and distributed architecture needs. CO2 apply logical database design principles to real-time issues. CO3 analyse and design database systems using relational, NoSQL and Big Data concepts. CO4 develop applications using relational and NoSQL databases. CO5 demonstrate database applications using various technologies.

**Syllabus units (for mapping features to marks):**
Unit I intro + ER model (entities, weak entities, relationship types, structural constraints). Unit II ER-to-relational mapping, relational model, relational algebra. Unit III SQL (DDL, constraints, queries), functional dependencies, normal forms to BCNF. Unit IV transactions, serializability, two-phase locking. Unit V NoSQL (aggregate/key-value/document models, sharding, replication), Big Data (Hadoop, MapReduce).

---

## 2. Topic

**College Canteen Demand, Stock & Food-Waste Database System** [DECIDED]

**Problem.** A college canteen decides daily how much food to prepare and how much raw material to buy, usually by intuition. Over-preparation causes food waste and financial loss; under-preparation causes shortages. There is no structured record of what was prepared, sold, wasted and purchased, nor of the context (holiday, exam period, weather, events) behind each day.

**Problem statement (boxed text in the synopsis).**
To design and implement, entirely from self-collected data, a hybrid relational–NoSQL database system that normalizes a college canteen's daily food preparation, sales, wastage and raw-material purchase records; integrates variable contextual data (day of week, holidays, exam periods, weather, special events, staff and student feedback) relevant to demand and waste; and surfaces actionable, query-driven insight into wastage patterns and purchasing needs, without depending on a trained machine-learning model, specialised monitoring hardware, or blockchain infrastructure.

**Objectives.**
1. Normalized relational schema (3NF) for preparation, sales, wastage and purchases at item level.
2. Real data collected by hand at the college canteen over the semester.
3. NoSQL (MongoDB) layer for variable contextual data and free-text feedback.
4. Answer operational questions ("which items are wasted most and when?", "does wastage rise in exam periods?") with SQL views, joins, GROUP BY and window functions, not a predictive model.
5. Lightweight hash-chained audit trail so wastage/purchase records cannot be silently altered.
6. Simple interface usable by canteen staff; feedback linked to the specific meal and date.

**Scope.**
- In: food items, quantity prepared/sold/leftover, customer counts, raw material purchases and vendors, staff/student feedback, daily context, one semester, one canteen.
- Out: ML/DL models, computer vision or IoT measurement, RFID/NFC billing, blockchain/distributed ledger, food-donation logistics.
- "Recent trend" checkbox is satisfied by the hash-chained audit log (blockchain-inspired, not a real ledger).
- **Societal concern:** food waste reduction (aligns with UN SDG 12.3).

**Data fields to collect per meal/day** (from the student's own plan): food item, quantity prepared, quantity sold/consumed, leftover quantity, number of customers, price, day of week, holiday/exam/event flag, weather if relevant. Also raw-material purchases (vendor, material, quantity, cost, batch).

---

## 3. Optional feature under consideration [OPEN]

**Natural-language query interface** for the canteen owner (plain-English question -> validated read-only SQL -> plain-English answer). Not yet approved. If it is built, these constraints apply:
- Uses an existing LLM purely for translation; **no model training or fine-tuning**.
- **Fixed set of ~5–8 pre-validated query templates**, not open-ended text-to-SQL.
- **SELECT only**, table/column allow-list, no writes of any kind, clear "data unavailable" message otherwise.
- Log every request in a `QueryLog` collection `{query_text, generated_sql, timestamp, status}`.
- It must not appear as the headline of the project; it is a convenience front end over the SQL layer.
- Do not start this until the core system (sections 5–8) works. Ask the student first.

---

## 4. Technology stack [SUGGESTED, student has not chosen]

| Layer | Suggested default | Notes |
|---|---|---|
| Relational DB | **MySQL 8+** | Needs 8+ for window functions and generated columns. PostgreSQL is an acceptable alternative. |
| NoSQL DB | **MongoDB** (local or Atlas free tier) | Document model, matches syllabus Unit V. |
| Backend | **Python 3.11 + FastAPI** | `pymysql`/`mysql-connector-python` for SQL, `pymongo` for MongoDB. Use **parameterised (dynamic) SQL** to satisfy the "database programming" guideline. |
| Frontend | Plain **HTML + CSS + JavaScript** served by the backend | Mobile-friendly staff data-entry form, manager dashboard/reports page, "verify audit trail" button. |
| Auth | Session or JWT, **bcrypt/argon2** password hashing | See section 9. |

Everything must run **locally** (the project must be carried out in the college and demoed there). Do not make the demo depend on internet access or paid APIs.

---

## 5. Data architecture

### 5.1 Split of responsibility

| Store | Technology | Contents |
|---|---|---|
| D1 USER ACCOUNTS (STAFF) | SQL | staff and login data |
| D2 MENU & RECIPE | SQL | FOOD_ITEM, RAW_MATERIAL, RECIPE_MATERIAL |
| D3 VENDOR | SQL | vendors |
| D4 MEAL & MEAL_LOG | SQL | meals and per-item meal logs |
| D5 WASTAGE_LOG | SQL | wastage records |
| D6 PURCHASE | SQL | raw-material purchases |
| D7 DAILY_CONTEXT | MongoDB | weather, holiday, exam period, events, notes |
| D8 FEEDBACK_NOTES | MongoDB | free-text staff/student feedback with tags |
| D9 AUDIT_TRAIL | MongoDB | hash-chained tamper-evident log |

Why NoSQL for the last three: structure varies day to day (context), free text with variable tags (feedback), append-only chained documents (audit).

### 5.2 ER model (Chen notation, already drawn) [DECIDED]

**Entities and attributes**

| Entity | Type | Attributes (PK underlined in diagram) |
|---|---|---|
| STAFF | strong | **staff_id**, name, role, shift |
| MEAL | strong | **meal_id**, date, meal_type |
| FOOD_ITEM | strong | **item_id**, name, category, unit, standard_recipe_cost |
| RAW_MATERIAL | strong | **material_id**, name, unit, perishable |
| VENDOR | strong | **vendor_id**, name, contact, item_category_supplied |
| MEAL_LOG | **weak** (depends on MEAL) | *log_id* (partial key), meal_id (FK), item_id (FK), staff_id (FK), qty_prepared, qty_sold, **leftover_qty (derived = qty_prepared − qty_sold)**, price_per_unit, customer_count_est |
| PURCHASE | strong | **purchase_id**, vendor_id (FK), item_id (FK, see issue 1 below), date, qty_purchased, cost, batch_no |
| WASTAGE_LOG | **weak** (depends on MEAL_LOG) | *wastage_id* (partial key), log_id (FK), qty_wasted, reason_code, disposal_method |

**Relationships**

| Relationship | Between | Cardinality | Notes |
|---|---|---|---|
| HAS | MEAL – MEAL_LOG | 1 : M | **identifying** (double diamond) |
| FOR | FOOD_ITEM – MEAL_LOG | 1 : M | |
| RECORDS | STAFF – MEAL_LOG | 1 : M | who logged the entry (accountability) |
| INCURS | MEAL_LOG – WASTAGE_LOG | 1 : M | **identifying** (double diamond) |
| REQUIRES | FOOD_ITEM – RAW_MATERIAL | **M : N** | relationship attribute `qty_required_per_unit`; becomes table RECIPE_MATERIAL |
| PROCURED_AS | FOOD_ITEM – PURCHASE | 1 : M | see issue 1 below |
| SUPPLIES | VENDOR – PURCHASE | 1 : M | |

### 5.3 Known issues in the drafted design — resolve before coding

1. **PURCHASE should reference RAW_MATERIAL, not FOOD_ITEM.** [DECIDED — approved by student] A canteen buys raw materials (rice, oil, onions), not finished dishes. The correct design is `PURCHASE.material_id -> RAW_MATERIAL`, relationship **RAW_MATERIAL 1:M PURCHASE**. The DDL uses `material_id`. The ER diagram and synopsis text should reflect this.
2. **`customer_count_est` placement.** If it is footfall for the whole meal, it depends only on `meal_id` and violates 2NF inside MEAL_LOG (belongs in MEAL). If it is customers served per item, it stays in MEAL_LOG. Student must decide; DDL keeps it in MEAL_LOG.
3. **Weak-entity key mapping.** Textbook mapping of a weak entity gives a composite PK (e.g. `(meal_id, log_no)`). The DDL uses a surrogate `log_id` PK plus `meal_id NOT NULL ... ON DELETE CASCADE` and a `UNIQUE(meal_id, item_id)`, which preserves existence dependency and keeps foreign keys simple. Be ready to explain this in the viva.
4. **Login needs credentials.** STAFF has no `username` / `password_hash` in the ER diagram. DDL adds them as a marked security extension; the ER diagram should list them if kept.
5. **FeedbackNotes** documents carry `staff_id`, but the objectives mention student feedback too. Suggested extension: add `source: "staff" | "student"` and allow `staff_id` to be null.

### 5.4 Relational schema — suggested DDL (MySQL 8) [SUGGESTED]

```sql
CREATE DATABASE IF NOT EXISTS canteen_db CHARACTER SET utf8mb4;
USE canteen_db;

CREATE TABLE staff (
  staff_id      INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(80)  NOT NULL,
  role          ENUM('manager','chef','helper','counter') NOT NULL,
  shift         ENUM('morning','afternoon','evening') NOT NULL,
  username      VARCHAR(40)  NOT NULL UNIQUE,      -- security extension (not yet in ER)
  password_hash VARCHAR(255) NOT NULL              -- security extension (not yet in ER)
);

CREATE TABLE food_item (
  item_id              INT AUTO_INCREMENT PRIMARY KEY,
  name                 VARCHAR(80) NOT NULL UNIQUE,
  category             ENUM('veg','non_veg','beverage','snack') NOT NULL,
  unit                 VARCHAR(20) NOT NULL,          -- plate, piece, cup ...
  standard_recipe_cost DECIMAL(8,2) NOT NULL CHECK (standard_recipe_cost >= 0)
);

CREATE TABLE raw_material (
  material_id INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(80) NOT NULL UNIQUE,
  unit        VARCHAR(20) NOT NULL,                   -- kg, litre, piece ...
  perishable  BOOLEAN NOT NULL DEFAULT FALSE
);

-- M:N relationship REQUIRES (FOOD_ITEM <-> RAW_MATERIAL)
CREATE TABLE recipe_material (
  item_id                INT NOT NULL,
  material_id            INT NOT NULL,
  qty_required_per_unit  DECIMAL(10,3) NOT NULL CHECK (qty_required_per_unit > 0),
  PRIMARY KEY (item_id, material_id),
  FOREIGN KEY (item_id)     REFERENCES food_item(item_id)    ON DELETE CASCADE,
  FOREIGN KEY (material_id) REFERENCES raw_material(material_id)
);

CREATE TABLE vendor (
  vendor_id              INT AUTO_INCREMENT PRIMARY KEY,
  name                   VARCHAR(80) NOT NULL,
  contact                VARCHAR(20),
  item_category_supplied VARCHAR(60)
);

CREATE TABLE meal (
  meal_id   INT AUTO_INCREMENT PRIMARY KEY,
  meal_date DATE NOT NULL,                            -- ER attribute "date"
  meal_type ENUM('breakfast','lunch','snacks','dinner') NOT NULL,
  UNIQUE (meal_date, meal_type)
);

-- weak entity (depends on MEAL)
CREATE TABLE meal_log (
  log_id             INT AUTO_INCREMENT PRIMARY KEY,
  meal_id            INT NOT NULL,
  item_id            INT NOT NULL,
  staff_id           INT NOT NULL,
  qty_prepared       INT NOT NULL CHECK (qty_prepared >= 0),
  qty_sold           INT NOT NULL CHECK (qty_sold >= 0),
  leftover_qty       INT GENERATED ALWAYS AS (qty_prepared - qty_sold) STORED,   -- derived attribute
  price_per_unit     DECIMAL(8,2) NOT NULL,
  customer_count_est INT,
  UNIQUE (meal_id, item_id),
  CHECK (qty_sold <= qty_prepared),
  FOREIGN KEY (meal_id)  REFERENCES meal(meal_id)       ON DELETE CASCADE,
  FOREIGN KEY (item_id)  REFERENCES food_item(item_id),
  FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

-- weak entity (depends on MEAL_LOG)
CREATE TABLE wastage_log (
  wastage_id      INT AUTO_INCREMENT PRIMARY KEY,
  log_id          INT NOT NULL,
  qty_wasted      INT NOT NULL CHECK (qty_wasted > 0),
  reason_code     ENUM('spoiled','over_prepared','quality_issue','other') NOT NULL,
  disposal_method ENUM('discarded','composted','donated','animal_feed','other') NOT NULL,
  FOREIGN KEY (log_id) REFERENCES meal_log(log_id) ON DELETE CASCADE
);
-- Rule to enforce in app logic or a trigger: SUM(qty_wasted) per log_id <= meal_log.leftover_qty

CREATE TABLE purchase (
  purchase_id   INT AUTO_INCREMENT PRIMARY KEY,
  vendor_id     INT NOT NULL,
  material_id   INT NOT NULL,                         -- see issue 1 (ER currently says item_id)
  purchase_date DATE NOT NULL,                        -- ER attribute "date"
  qty_purchased DECIMAL(10,2) NOT NULL CHECK (qty_purchased > 0),
  cost          DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
  batch_no      VARCHAR(30),
  FOREIGN KEY (vendor_id)   REFERENCES vendor(vendor_id),
  FOREIGN KEY (material_id) REFERENCES raw_material(material_id)
);
```

### 5.5 Normalization story (Weeks 6–7 deliverable) [SUGGESTED]

Start from the "natural" flat sheet a canteen would keep: `date, meal_type, item_name, category, unit, standard_cost, qty_prepared, qty_sold, price, customers, staff_name, staff_role, shift, wastage_qty, wastage_reason, disposal`. Show functional dependencies and decompose 1NF -> 2NF -> 3NF into the schema above:

- `item_id -> name, category, unit, standard_recipe_cost`
- `meal_id -> meal_date, meal_type` and `(meal_date, meal_type) -> meal_id`
- `(meal_id, item_id) -> staff_id, qty_prepared, qty_sold, price_per_unit, customer_count_est`
- `staff_id -> name, role, shift`
- `(item_id, material_id) -> qty_required_per_unit`
- `vendor_id -> name, contact, item_category_supplied`
- `purchase_id -> vendor_id, material_id, purchase_date, qty_purchased, cost, batch_no`

Show which anomalies each split removes (update anomaly on item cost, insertion anomaly for a new item with no meals yet, deletion anomaly on removing the last log of an item). Check BCNF for each table.

### 5.6 MongoDB collections [DECIDED structure, SUGGESTED details]

```jsonc
// DailyContext  (one document per date; unique index on date)
{ "date": "2026-11-03", "weather": "rainy", "is_holiday": false,
  "exam_period": true, "special_event": "Tech fest day 1", "notes": "Power cut at lunch" }

// FeedbackNotes  (linked to a meal log; tags filled by simple keyword matching, NOT ML)
{ "log_id": 412, "staff_id": 3, "source": "staff",
  "timestamp": "2026-11-03T13:05:00", "note_text": "Rice was stale by 2pm",
  "tags": ["stale", "overproduced"] }

// AuditTrail  (hash chain; append-only)
{ "record_id": "meal_log:412", "source_table": "meal_log", "log_id": 412,
  "prev_hash": "<64 hex chars>", "curr_hash": "<64 hex chars>",
  "timestamp": "2026-11-03T13:06:00", "action": "INSERT" }
```

Keyword tagging dictionary (extend as needed): `stale, spoiled, cold, salty, undercooked, shortage, finished, overproduced, queue, late`.

---

## 6. System behaviour

### 6.1 Users and roles
- **Canteen Staff**: log in, enter meal preparation/sales/wastage for the current day, add notes.
- **Canteen Manager (Owner)**: everything staff can do, plus master data (menu, recipes, vendors, staff accounts), reports/insights, audit verification.
- **Vendor** and **Students/Customers** are external entities only (supply details and feedback come in through staff/manager entry or a feedback form); they have no login.

### 6.2 Functional modules (map 1:1 to the Level-1 DFD processes)

| # | Process | What it does | Reads / writes |
|---|---|---|---|
| 1.0 | Authenticate & Manage Users | login, role check, staff account management | D1 |
| 2.0 | Manage Master Data | CRUD for food items, raw materials, recipes, vendors | writes D2, D3 |
| 3.0 | Record Meal Prep, Sales & Wastage | 3.1 validate entry (item exists, qty >= 0, sold <= prepared), 3.2 create/find MEAL, 3.3 write MEAL_LOG and compute leftover, 3.4 write WASTAGE_LOG (wasted <= leftover) | reads D2; read/write D4; writes D5 |
| 4.0 | Record Purchases & Stock | record raw-material purchases against a vendor | reads D2, D3; writes D6 |
| 5.0 | Capture Daily Context, Notes & Feedback | store context per date, keyword-tag notes, link to a meal log | reads D4; writes D7, D8 |
| 6.0 | Maintain Audit Trail | 6.1 detect new/changed records, 6.2 fetch previous hash, 6.3 compute hash, 6.4 store audit record, 6.5 verify chain | reads D4, D5, D6; read/write D9 |
| 7.0 | Generate Insights & Reports | 7.1 accept request, 7.2 wastage & sales metrics, 7.3 purchases & vendor spend, 7.4 link context & feedback, 7.5 detect anomalies, 7.6 compile report | reads D2–D8 |

### 6.3 Audit trail algorithm (hash chain) [SUGGESTED]

```python
import hashlib, json

GENESIS = "0" * 64

def compute_hash(prev_hash: str, record: dict, action: str, ts_iso: str) -> str:
    payload = json.dumps(
        {"prev": prev_hash, "record": record, "action": action, "ts": ts_iso},
        sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

- On every INSERT/UPDATE of `meal_log`, `wastage_log`, `purchase`: read the latest AuditTrail document (or `GENESIS`), compute `curr_hash` over the canonical record, insert a new AuditTrail document.
- **Verify**: walk the chain in order; for each document check `prev_hash` equals the previous `curr_hash`, and recompute the hash from the *current* SQL row. Report "chain intact" or the first tampered `record_id`.
- Audit documents are append-only; the application DB user has no update/delete rights on that collection.

### 6.4 Insight queries to implement (no ML) [SUGGESTED]

```sql
-- (a) Average leftover % per item per weekday
SELECT fi.name, DAYNAME(m.meal_date) AS weekday,
       ROUND(100 * AVG(ml.leftover_qty / NULLIF(ml.qty_prepared, 0)), 1) AS avg_leftover_pct
FROM meal_log ml
JOIN meal m       ON m.meal_id = ml.meal_id
JOIN food_item fi ON fi.item_id = ml.item_id
GROUP BY fi.item_id, fi.name, DAYNAME(m.meal_date)
ORDER BY avg_leftover_pct DESC;

-- (b) Items with leftover > 20% on each of their last 3 serving days (window function)
WITH daily AS (
  SELECT ml.item_id, m.meal_date,
         100 * SUM(ml.leftover_qty) / NULLIF(SUM(ml.qty_prepared), 0) AS leftover_pct
  FROM meal_log ml JOIN meal m ON m.meal_id = ml.meal_id
  GROUP BY ml.item_id, m.meal_date
), flagged AS (
  SELECT item_id, meal_date, leftover_pct,
         SUM(leftover_pct > 20) OVER (PARTITION BY item_id ORDER BY meal_date
                                      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS hits
  FROM daily
)
SELECT item_id, meal_date FROM flagged WHERE hits = 3;   -- "consecutive serving days", not calendar days

-- (c) Most wasted item in the last 7 days
SELECT fi.name, SUM(w.qty_wasted) AS total_wasted
FROM wastage_log w
JOIN meal_log ml  ON ml.log_id = w.log_id
JOIN meal m       ON m.meal_id = ml.meal_id
JOIN food_item fi ON fi.item_id = ml.item_id
WHERE m.meal_date >= CURDATE() - INTERVAL 7 DAY
GROUP BY fi.item_id, fi.name ORDER BY total_wasted DESC LIMIT 1;

-- (d) Spend per vendor per month
SELECT v.name, DATE_FORMAT(p.purchase_date, '%Y-%m') AS month, SUM(p.cost) AS total_spend
FROM purchase p JOIN vendor v ON v.vendor_id = p.vendor_id
GROUP BY v.vendor_id, v.name, month ORDER BY month, total_spend DESC;
```

**(e) Exam / holiday effect (cross-store).** Fetch dates from MongoDB `DailyContext` where `exam_period` (or `is_holiday`) is true, pass them as a parameterised list to SQL, and compare average leftover % on those dates vs other dates. Do the join in the application layer (SQL and MongoDB are separate stores).

Also expose each of (a)–(d) as a named SQL **view** where possible, so the report can show views as a Unit III feature.

---

## 7. DFD set (design is final, notation must be redone) 

**Notation requirement [DECIDED]:** a previous DFD submission in Gane-Sarson notation (rounded-rectangle processes) was **rejected**. Redraw all DFDs following the **GeeksforGeeks DFD notation** (Yourdon–DeMarco style): **rectangle = external entity, circle (bubble) = process, open rectangle / two parallel lines = data store, labelled arrow = data flow.** Number processes 1.0…, 3.1…. Keep the content below unchanged.

**External entities:** Canteen Staff, Canteen Manager (Owner), Vendor, Students/Customers.

**Level 0 (context):** one process "Canteen Demand, Stock & Food-Waste Database System".
- Staff -> system: login credentials; meal, sales & wastage entries; daily context & staff notes. System -> Staff: login result; entry confirmation / validation errors.
- Manager -> system: login credentials; master data (menu, recipe, vendor, staff); report & audit-verification requests. System -> Manager: reports, anomaly alerts, audit verification result, login result.
- Vendor -> system: supply details & invoice. System -> Vendor: purchase receipt acknowledgement.
- Students -> system: feedback & complaints.

**Level 1:** processes 1.0–7.0 and stores D1–D9 exactly as in section 6.2 and 5.1. Notes: D2 and D3 are drawn twice (marked `*`) to avoid long crossing lines. Process 6.0 reads D4, D5, D6 directly; process 7.0 reads D2, D3, D4, D5, D6, D7, D8.

**Level 2 (three diagrams):**
- **3.0** -> 3.1 Validate Entry, 3.2 Record Meal, 3.3 Record Meal Log & Compute Leftover, 3.4 Record Wastage. Flows: entry -> 3.1 (reads D2 item details) -> validated entry -> 3.2 (read/write D4) -> meal_id -> 3.3 (writes D4) -> log_id + leftover -> 3.4 (writes D5); confirmations from 3.3 and 3.4 to Staff; validation errors from 3.1 to Staff.
- **6.0** -> 6.1 Detect New/Changed Records (reads D4, D5, D6), 6.2 Fetch Previous Hash (reads D9), 6.3 Compute Record Hash, 6.4 Store Audit Record (writes D9), 6.5 Verify Hash Chain (Manager request in, reads D9, gets current record content from 6.1, verification result out).
- **7.0** -> 7.1 Accept & Validate Request, 7.2 Compute Wastage & Sales Metrics (reads D2, D4, D5), 7.3 Analyse Purchases & Vendor Spend (reads D6, D3), 7.4 Link Context & Feedback (reads D7, D8), 7.5 Detect Anomalies (leftover > 20%), 7.6 Compile & Deliver Report.

Balancing rule: every Level-2 diagram must keep exactly the inputs/outputs of its Level-1 parent.

---

## 8. Literature survey summary (for the report; 10 IEEE Xplore papers, 2022–2025)

| # | Paper | Year | What it is / key limitation vs this project |
|---|---|---|---|
| 1 | Ifham et al., *Machine Learning Based Approach to Reduce Food Wastage*, ICAC | 2023 | Bundle of ML modules (wastage, demand, near-expiry pricing). No database design described; output is opaque predictions. IEEE doc 10417516 |
| 2 | Kumar, Pilania, Dagar, *Food Demand Forecasting using ML Approaches*, ICSCSA | 2025 | Seven classifiers compared; best (LDA) only 71.9% accurate. No data-structure discussion, no context features. IEEE 11171212 |
| 3 | *A Strategic Analysis of Food Demand Using ML and Explainable AI* | 2024 | Kaggle dataset + XAI; assumes a pre-cleaned dataset; explains the model, not the data. IEEE 10543689 |
| 4 | *Predictive Analytics in Food Supply Chain and Waste Management* | ~2026 | LSTM/XGBoost/RF on restaurant data; needs large history. IEEE 11386707 |
| 5 | Jia, Shi, Wan, Hao, *Monitoring Food Waste in School Canteens Based on RGB-D Images* | 2024/25 | Depth cameras + segmentation model; hardware/cost barrier; no link to preparation or purchasing. IEEE 10948771 |
| 6 | Joshi, Kasaju, Karki, Aryal, Chhetri, *Smart Canteen Management System*, MysuruCon | 2022 | RFID billing only; no prepared/sold/wasted data. IEEE 9971803 |
| 7 | Patil, Nikam, Nair, Raut, Lobo, *Sustainable Food Waste Management and Tracking System Using Blockchain* | 2023 | Traceability of donated leftovers; needs blockchain + QR/NFC; wrong problem (redistribution). IEEE 10141799 |
| 8 | Gaidhani, Varsha, Agrawal, Pote, Pande, *Web Application to Track Food Quality and Service in the Hostel Mess*, GCAT | 2023 | Ratings/reviews only; disconnected from operational records. IEEE 10353498 |
| 9 | *A Holistic Approach to Food Waste Management: Full-Stack Technologies…* | 2025 | Reporting dashboards; database design not a contribution. IEEE 10397029 |
| 10 | *A Comprehensive Analysis: Smart Food Waste Management System* | 2025 | Diagnoses traceability/accountability gaps, implements nothing. IEEE 11337031 |

Link pattern: `https://ieeexplore.ieee.org/document/<doc number>/`.
**Reference-list caveat:** authors/DOI for papers 3, 4, 9, 10 were not retrievable (IEEE pages did not render), and year/venue for 3, 4, 5, 9, 10 should be checked on the IEEE page before submission.

**Research gap (the project's novelty claim):** ML papers assume a clean dataset already exists and still carry error; hardware papers need capital investment; the blockchain paper solves redistribution, not internal decisions; feedback/reporting tools leave data disconnected from operations; the diagnostic paper names the accountability gap but builds nothing. **No reviewed work treats the database itself, built from scratch on self-collected data with no ML, hardware or blockchain, as the thing worth designing well.**

---

## 9. Security requirements (syllabus: "appreciate the importance of security")

- Passwords stored only as bcrypt/argon2 hashes; never log or return them.
- Role-based access control (staff vs manager) enforced in the backend, not just the UI.
- **Parameterised queries everywhere** (this doubles as the "Dynamic SQL" requirement); never build SQL by string concatenation. Sanitise MongoDB query inputs (no raw operators from user input).
- Separate DB users: an application user with only the privileges it needs (no DROP/ALTER), a read-only user for reports, and no update/delete on the AuditTrail collection.
- Input validation mirrors the DB constraints (quantities >= 0, sold <= prepared, wasted <= leftover).
- Keep credentials in a `.env` file excluded from version control.
- Student feedback is anonymous; do not store names or IDs of students.
- Be ready to demonstrate the audit trail catching a manually edited row.

---

## 10. Suggested repository layout [SUGGESTED]

```
canteen-db/
├─ PROJECT_CONTEXT.md          # this file
├─ README.md
├─ .env.example
├─ db/
│  ├─ 001_schema.sql
│  ├─ 002_views.sql
│  ├─ 003_triggers_or_checks.sql
│  ├─ seed_dummy_DO_NOT_SUBMIT.sql
│  └─ mongo_init.js            # collections, indexes (unique DailyContext.date)
├─ backend/
│  ├─ main.py                  # FastAPI app
│  ├─ auth.py  roles.py
│  ├─ sql.py   mongo.py        # parameterised access layer
│  ├─ audit.py                 # hash chain + verify
│  ├─ tagging.py               # keyword tagger (no ML)
│  └─ insights.py              # queries (a)-(e)
├─ frontend/                   # entry form, manager dashboard, audit-verify page
├─ docs/
│  ├─ synopsis/  er/  dfd/  report/
│  └─ weekly_progress/         # one short note + diagram per week
└─ tests/
```

---

## 11. Suggested 14-week plan [SUGGESTED]

Weekly progress must be shown (ER diagrams etc.), so each week ends with a visible artefact.

| Week | Work | Artefact to show |
|---|---|---|
| 1 | Finalise topic with faculty; get canteen management permission; design paper/Sheet log for daily entry | Signed-off topic, data sheet |
| 2 | Data requirement specification; **start real data collection (continues all semester)**; submit synopsis | Requirement spec, synopsis |
| 3–4 | ER diagram (Chen) and DFD levels 0–2 (GfG notation) | ER, DFDs |
| 5 | ER-to-relational mapping, schema draft | Relational schema |
| 6–7 | Normalization walkthrough 1NF -> 3NF (+ BCNF check) | FD list, decomposition |
| 8 | MySQL DDL, constraints, views; load collected data so far | `001_schema.sql`, views |
| 9 | MongoDB collections and indexes | Mongo schema, sample docs |
| 10 | Backend + staff entry form + manager dashboard | Working app |
| 11 | Security: auth, roles, DB users, parameterised queries | Security note + demo |
| 12 | Audit hash chain + verification; insight queries (a)–(e) | Tamper demo, reports |
| 13 | Testing, transactions/concurrency note (Unit IV link), documentation | Test log |
| 14 | Final report, viva prep, demo rehearsal (offline) | Report, demo script |

---

## 12. Documents already produced (status)

| Document | Status |
|---|---|
| Synopsis (template: RVCE "Mandi Price Cause Tracker" format) | Sections 1–3 drafted as text in chat; Section 4 Database Complexity and reference list need final update; final `.docx` not built (student formats it) |
| ER diagram (Chen, attributes as external ovals, PNG + SVG) | Done; **needs update for issue 1 (PURCHASE -> RAW_MATERIAL)** and optionally login attributes |
| DFD levels 0, 1, 2 | Content final; **drawn in Gane-Sarson and rejected; redraw in GfG notation** |
| Literature survey (10 IEEE papers, tables 2.1/2.2, positioning) | Text drafted; verify authors/DOIs for papers 3, 4, 9, 10 |
| Natural-language query interface | Proposed, undecided (section 3) |

---

## 13. Open decisions checklist

- [ ] Fix PURCHASE -> RAW_MATERIAL in ER and synopsis (issue 1).
- [ ] Where does `customer_count_est` live (issue 2)?
- [ ] Confirm weak-entity key mapping approach (issue 3).
- [ ] Add login attributes to STAFF in the ER (issue 4).
- [ ] FeedbackNotes: add `source` and allow student feedback (issue 5).
- [ ] Final stack choice (section 4).
- [ ] Include the natural-language query interface or not (section 3).
- [ ] Faculty approval of the topic and of the SQL + NoSQL split.
- [ ] Real data collection started and schedule agreed with canteen staff.
