# BUSINESS REQUIREMENTS ANALYSIS

## 🎯 PROJECT PURPOSE

**Wareflow EMS** = Warehouse Employee Management System

**Goal:** Manage warehouse employees with their safety certifications (CACES) and medical compliance tracking.

---

## 👥 CORE ENTITY: EMPLOYEE

### What is an Employee?

A person working in the warehouse/Logistics company that needs to be tracked for safety compliance.

### Required Information

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| **first_name** | Text | ✅ YES | Prénom |
| **last_name** | Text | ✅ YES | Nom |
| **contract_type** | Dropdown | ✅ YES | Type de contrat |
| **entry_date** | Date | ✅ YES | Date d'arrivée |
| **departure_date** | Date | ❌ NO | Date de départ (optional) |
| **current_status** | Dropdown | ✅ YES | Statut actuel |

### Contract Types (Dropdown)

```
- CDI          = Contrat à Durée Indéterminée
- CDD          = Contrat à Durée Déterminée
- Interim      = Intérimaire
- Alternance  = Alternance
```

### Employee Status

```
- active    = Employé actif (travaille actuellement)
- inactive  = Employé inactif (a quitté, suspendu, etc.)
```

### Business Rules

1. **Employee must have at least:**
   - First name + Last name
   - Contract type
   - Entry date
   - Status (active/inactive)

2. **Departure date is optional:**
   - Only if employee has left
   - Can be added/updated later

3. **Status can change:**
   - active → inactive (when leaving)
   - inactive → active (when rehiring)

---

## 🏗️ TRACKING: CACES CERTIFICATIONS

### What is a CACES?

**CACES** = Certificat d'Aptitude à la Conduite En Sécurité

French mandatory certification for operating heavy machinery and equipment (forklifts, cranes, etc.)

### Required Information

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| **kind** | Dropdown | ✅ YES | Type R489 |
| **completion_date** | Date | ✅ YES | Date de début |
| **expiration_date** | Date | ✅ Auto | Date de fin (calculée) |
| **document_path** | File | ❌ NO | PDF du certificat |

### CACES Types (Dropdown)

Standard French R489 categories:

```
- R489-1A = Chariot élévateur en porte-à-faux
- R489-1B = Chariot élévateur à mât rétractable
- R489-3   = Chariot élévateur ≥ 6 tonnes
- R489-4   = Chariot à mât rétractable ≥ 6 tonnes
- R489-5   = Chariot latéral
```

### Validity Periods (Automatic Calculation)

| CACES Type | Validity |
|------------|----------|
| R489-1A | 5 years |
| R489-1B | 5 years |
| R489-3 | 5 years |
| R489-4 | 5 years |
| R489-5 | 10 years |

**Example:**
```
CACES R489-1A obtained: 2025-01-15
Expiration date: 2030-01-15 (auto-calculated)
```

### Business Rules

1. **One employee can have multiple CACES**
   - Employee can have R489-1A + R489-3
   - Each has its own dates

2. **Expiration is automatically calculated**
   - No need to manually calculate
   - Based on CACES type
   - Uses leap years correctly

3. **Document (PDF) is optional**
   - Can upload scanned certificate
   - File is stored in `documents/caces/`
   - Optional but recommended

---

## 🏥 TRACKING: MEDICAL VISITS

### What is a Medical Visit?

French labor law requires periodic occupational health examinations for warehouse workers.

### Required Information

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| **visit_type** | Dropdown | ✅ YES | Type de visite |
| **visit_date** | Date | ✅ YES | Date de la visite |
| **expiration_date** | Date | ✅ Auto | Date de fin de validité |
| **result** | Dropdown | ✅ YES | Résultat |
| **document_path** | File | ❌ NO | PDF du certificat |

### Visit Types (Dropdown)

```
- initial   = Visite d'embauche
- periodic  = Visite périodique (annuelle)
- recovery  = Visite de reprise (après arrêt maladie/blessure)
```

### Visit Results (Dropdown)

```
- fit                  = Aptte (apt au travail)
- unfit                = Inapte (pas apte au travail)
- fit_with_restrictions = Aptte avec restrictions (apte mais tâches limitées)
```

### Validity Periods (Automatic Calculation)

| Visit Type | Validity |
|------------|----------|
| initial | 2 years |
| periodic | 2 years |
| recovery | 1 year |

**Example:**
```
Initial visit: 2025-01-15
Expiration date: 2027-01-15 (auto-calculated)
```

### Business Rules

1. **Visit type determines validity period**
   - Initial/periodic = 2 years
   - Recovery = 1 year

2. **Result affects employee fitness**
   - fit = Can work normally
   - unfit = CANNOT work (safety risk)
   - fit_with_restrictions = Can work with limitations

3. **Recovery visits MUST have restrictions**
   - Business rule: someone returning from medical leave has restrictions
   - System enforces: recovery → fit_with_restrictions only

4. **Multiple visits over time**
   - Employee has history of visits
   - Track each visit separately
   - Only LATEST visit determines current fitness

---

## 📊 SECONDARY TRACKING: ONLINE TRAININGS

*(Less critical, but included in system)*

### Required Information

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| **title** | Text | ✅ YES | Titre de la formation |
| **completion_date** | Date | ✅ YES | Date de fin |
| **validity_months** | Number | ❌ NO | Durée de validité (mois) |
| **expiration_date** | Date | Auto | Date d'expiration (si applicable) |
| **certificate_path** | File | ❌ NO | PDF du certificat |

### Business Rules

1. **Some trainings expire, others are permanent**
   - If `validity_months` is set → training expires
   - If `validity_months` is NULL → training is permanent

2. **Examples:**
   - "Safety Training" = 12 months validity → expires
   - "Company Policy" = NULL validity → permanent

---

## 🎯 KEY REQUIREMENT: EXPIRATION TRACKING

### The Core Problem

**Safety certifications EXPIRE.** The system must track:
- When certifications expire
- Who has expiring certifications
- Alert before expiration

### Status Indicators

For each certification (CACES, Medical, Training):

| Status | Meaning | Color Code |
|--------|---------|-------------|
| **valid** | More than 60 days left | 🟢 Green |
| **warning** | Expires in 30-60 days | 🟡 Yellow |
| **critical** | Expires in less than 30 days | 🟠 Orange |
| **expired** | Already expired | 🔴 Red |

### Alert Thresholds (Configurable)

Default thresholds:
- **30 days** = Critical (expires soon)
- **60 days** = Warning (plan renewal)
- **90 days** = Information (upcoming)

### Example Timeline

```
Today: 2025-01-20
CACES R489-1A expires: 2025-02-15

Days until expiration: 26 days
Status: CRITICAL (less than 30 days)
Action needed: Schedule renewal ASAP
```

---

## 🔗 RELATIONSHIPS

### Employee → Certifications (One-to-Many)

```
Employee (1) ←→ (N) CACES
Employee (1) ←→ (N) Medical Visits
Employee (1) ←→ (N) Online Trainings
```

**What this means:**
- One employee can have multiple CACES
- One employee can have multiple medical visits (over time)
- One employee can have multiple trainings
- When employee is deleted, ALL their certifications are deleted (CASCADE)

---

## 📱 USER WORKFLOWS

### Workflow 1: Add New Employee

```
1. Click "Add Employee" button
2. Fill form:
   - First name: "Jean"
   - Last name: "Dupont"
   - Contract type: CDI
   - Entry date: 2025-01-15
   - Status: active
3. Click "Save"
4. Employee appears in list
```

### Workflow 2: Add CACES to Employee

```
1. Open employee detail view
2. Click "Add CACES" button
3. Fill form:
   - Type: R489-1A (dropdown)
   - Start date: 2025-01-15
4. System auto-calculates expiration: 2030-01-15
5. Optional: Upload PDF certificate
6. Click "Save"
7. CACES appears in employee's certifications list
```

### Workflow 3: Check Expiring Certifications

```
1. Open "Alerts" view
2. System shows:
   - All certifications expiring within 30/60/90 days
   - Grouped by employee
   - Color-coded by urgency
3. Take action: Schedule renewal, notify employee, etc.
```

### Workflow 4: Record Medical Visit

```
1. Open employee detail view
2. Click "Add Medical Visit" button
3. Fill form:
   - Type: periodic (dropdown)
   - Date: 2025-01-15
   - Result: fit (dropdown)
4. System auto-calculates expiration: 2027-01-15
5. Optional: Upload medical certificate
6. Click "Save"
```

---

## 🚨 CRITICAL BUSINESS REQUIREMENTS

### 1. Compliance Tracking

**Why this exists:**
- French law mandates valid CACES for machinery operators
- French law mandates valid medical clearance for warehouse workers
- Company must PROVE compliance at any time (audits, inspections)

**What the system must do:**
- Track expiration dates automatically
- Alert before certifications expire
- Provide proof of compliance (show valid certificates)
- Identify non-compliant employees (expired certifications)

### 2. Safety

**Why this matters:**
- Employee with expired CACES = Illegal to operate machinery
- Employee with "unfit" medical status = Safety risk
- Company can be fined for non-compliance

**What the system must do:**
- Show current status clearly (valid/expired)
- Highlight expired certifications in red
- Identify unfit employees
- Prevent scheduling of non-compliant employees

### 3. Documentation

**Why important:**
- Proof of certification for audits
- Legal requirement to keep records
- Need to produce certificates on demand

**What the system must do:**
- Store PDF certificates safely
- Organize by type (caces/, medical/, training/)
- Allow viewing/downloading certificates
- Standardized file naming

---

## 📊 DATA MODEL SUMMARY

### Tables (Entities)

```
employees
├── id (UUID)
├── first_name
├── last_name
├── contract_type (CDI/CDD/Interim/Alternance)
├── entry_date
├── departure_date (optional)
└── current_status (active/inactive)

caces (linked to employee)
├── id (UUID)
├── employee_id (foreign key)
├── kind (R489-1A, R489-1B, etc.)
├── completion_date
├── expiration_date (auto-calculated)
└── document_path (optional)

medical_visits (linked to employee)
├── id (UUID)
├── employee_id (foreign key)
├── visit_type (initial/periodic/recovery)
├── visit_date
├── expiration_date (auto-calculated)
├── result (fit/unfit/fit_with_restrictions)
└── document_path (optional)

online_trainings (linked to employee)
├── id (UUID)
├── employee_id (foreign key)
├── title
├── completion_date
├── validity_months (optional, NULL = permanent)
├── expiration_date (auto-calculated if applicable)
└── certificate_path (optional)
```

---

## ✅ CURRENT IMPLEMENTATION STATUS

### ✅ FULLY IMPLEMENTED

**Employee Model (`src/employee/models.py`)**
- ✅ All fields present
- ✅ Auto-calculations (full_name, seniority)
- ✅ Relationships to certifications
- ✅ Validation hooks
- ✅ CASCADE delete configured

**CACES Model**
- ✅ All fields present
- ✅ Auto-calculation of expiration_date
- ✅ Computed properties (is_expired, days_until_expiration, status)
- ✅ Class methods (expiring_soon, expired, by_kind)
- ✅ Validation (kind must be valid R489 type)
- ✅ Validity periods correctly configured

**MedicalVisit Model**
- ✅ All fields present
- ✅ Auto-calculation of expiration_date
- ✅ Computed properties (is_expired, is_fit, has_restrictions)
- ✅ Class methods (expiring_soon, unfit_employees)
- ✅ Validation (visit type + result consistency)
- ✅ Validity periods correctly configured

**OnlineTraining Model**
- ✅ All fields present
- ✅ Auto-calculation of expiration_date
- ✅ Handles both expiring and permanent trainings
- ✅ Computed properties (expires, is_expired, status)

### ✅ CONTROLLERS IMPLEMENTED

**DashboardController** (`src/controllers/dashboard_controller.py`)
- ✅ get_statistics() → Dashboard counts
- ✅ get_alerts() → Expiring certifications grouped by employee
- ✅ get_compliance_percentage() → Overall compliance score

**EmployeeController** (`src/controllers/employee_controller.py`)
- ✅ get_employee_by_id() → Get one employee
- ✅ get_employee_details() → Get complete employee data with certifications
- ✅ get_all_employees() → List all employees
- ✅ get_active_employees() → List active employees only

**AlertsController** (`src/controllers/alerts_controller.py`)
- ✅ Filter by alert type, days
- ✅ Export functionality

---

## 🎯 PRIORITY REQUIREMENTS FOR UI

### Must Have (MVP)

1. **Employee List**
   - Show all employees in a table
   - Display: Name, Role, Status, Compliance Score
   - Filter by status (active/inactive)
   - Search by name

2. **Employee Detail**
   - Show employee information
   - List all CACES with expiration status
   - List all medical visits with expiration status
   - Color-code status (green/orange/red)

3. **Add Employee Form**
   - First name, last name (required)
   - Contract type (dropdown)
   - Entry date (required)
   - Status (dropdown)

4. **Add CACES Form**
   - Type (dropdown: R489-1A, R489-1B, etc.)
   - Completion date
   - Optional: Upload PDF

5. **Add Medical Visit Form**
   - Type (dropdown: initial, periodic, recovery)
   - Date
   - Result (dropdown: fit, unfit, fit_with_restrictions)
   - Optional: Upload PDF

6. **Alerts View**
   - Show all certifications expiring soon
   - Group by employee
   - Show days until expiration
   - Color-code urgency

### Nice to Have (V2)

7. **Dashboard**
   - Statistics cards (total employees, expiring count, etc.)
   - Compliance percentage
   - Recent alerts list

8. **Online Training Tracking**
   - Add trainings
   - Track expiration

9. **Excel Export**
   - Export employee list with certifications
   - Export alerts list

---

## 🚨 WHAT'S MISSING FOR UI

### Nothing in Core Business Logic!

The database models, controllers, and business logic are **COMPLETE**.

What's needed:
1. **CustomTkinter UI** to display and interact with data
2. **Bootstrapper** (optional - can create instances manually for now)
3. **Build system** (PyInstaller to create .exe)

---

## 📋 SIMPLIFIED TECHNICAL STACK

### What You Have (Business Logic)

✅ Python 3.14+
✅ SQLite database with Peewee ORM
✅ Employee models (Employee, Caces, MedicalVisit, OnlineTraining)
✅ Business logic (calculations, validations)
✅ Controllers (Dashboard, Employee, Alerts)
✅ Lock manager (multi-user safety)
✅ CLI (fully functional)

### What You Need (UI Only)

❌ Desktop UI in CustomTkinter

That's it!

---

## 🎯 NEXT STEPS FOR UI

### Option 1: Simple & Fast (RECOMMENDED)

Create CustomTkinter app with:

1. **Employee List View**
   - Table with all employees
   - Add button → form dialog
   - Double-click row → detail view

2. **Employee Detail View**
   - Employee info card
   - List of CACES (with status badges)
   - List of medical visits (with status badges)
   - Add buttons for each type

3. **Simple Forms**
   - Employee form (add/edit)
   - CACES form (add)
   - Medical visit form (add)

4. **Alerts View**
   - List of expiring items
   - Grouped by employee
   - Filter by type (CACES/medical)

**That's the MVP.** Simple, functional, does what you need.

---

## 💡 KEY INSIGHT

**The business logic is SOLID.** The models, validations, calculations, and controllers are all implemented and tested.

**What you need is just the USER INTERFACE** to interact with this data.

The UI doesn't need to be fancy. It just needs to:
- Display employees
- Display certifications
- Add/edit employees
- Add certifications
- Show alerts

**CustomTkinter is perfect for this.**

---

## 📊 SUMMARY

### Core Entities
1. **Employee** - People working in the warehouse
2. **CACES** - Safety certifications for machinery
3. **Medical Visits** - Health compliance tracking
4. **Online Trainings** - Additional certifications

### Most Important Feature
**TRACKING EXPIRATION DATES**
- Auto-calculate from start date
- Alert before expiration
- Show status (valid/warning/critical/expired)
- Group by employee for easy viewing

### Current State
✅ Business logic 100% complete
❌ UI removed (was Flet, now needs CustomTkinter)

### What's Needed
Just a simple, functional CustomTkinter desktop application.

**No bootstrapper complexity needed initially.** Just the UI app.
