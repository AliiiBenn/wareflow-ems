# ISSUE-065: Contract History and Evolution Tracking

## Description

The current Employee model only tracks the current contract (start date). The system needs to maintain a complete history of contracts with start dates, end dates, contract types, and evolution (promotions, status changes) to properly track employee career progression.

## Current State

**Employee model has:**
```python
class Employee(BaseModel):
    # ...
    entry_date = DateField()  # Hire date
    contract_type = CharField(null=True)  # Single value
    # No contract history
```

**Missing:**
- Contract history
- Start and end dates for each contract
- Contract type evolution (CDI, CDD, interim, etc.)
- Salary evolution
- Position changes
- Status changes
- Trial periods

## Expected Behavior

### Contract History Model

**Add to: `src/employee/models.py`**

```python
class Contract(BaseModel):
    """Represent an employment contract."""

    id = AutoField()
    employee = ForeignKeyField(Employee, backref="contracts")

    # Contract details
    contract_type = CharField(max_length=50)  # CDI, CDD, Interim, Apprentissage, Stage
    start_date = DateField()
    end_date = DateField(null=True)  # Null for CDI (permanent)
    trial_period_end = DateField(null=True)
    weekly_hours = DecimalField(max_digits=4, decimal_places=2, default=35.0)
    gross_salary = DecimalField(max_digits=10, decimal_places=2, null=True)

    # Position and department
    position = CharField(max_length=100)
    department = CharField(max_length=100)
    manager = CharField(max_length=100, null=True)

    # Status
    status = CharField(max_length=20, default="active")  # active, ended, cancelled
    end_reason = CharField(max_length=100, null=True)  # resignation, termination, completion, etc.

    # Documents
    contract_document_path = CharField(max_length=500, null=True)
    amendments = TextField(null=True)  # JSON array of amendments

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    created_by = CharField(max_length=100, null=True)
    notes = TextField(null=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.contract_type} ({self.start_date})"

    @property
    def is_current(self) -> bool:
        """Check if this is the current active contract."""
        if self.status != "active":
            return False

        today = date.today()

        # Hasn't started yet
        if self.start_date > today:
            return False

        # Has end date and has passed
        if self.end_date and self.end_date < today:
            return False

        return True

    @property
    def duration_days(self) -> Optional[int]:
        """Calculate contract duration in days."""
        if not self.end_date:
            return None  # Ongoing (CDI)
        return (self.end_date - self.start_date).days

    @property
    def is_trial_period(self) -> bool:
        """Check if currently in trial period."""
        if not self.trial_period_end:
            return False
        return date.today() <= self.trial_period_end

    class Meta:
        indexes = (
            (("employee", "start_date"), False),  # Chronological order
            ("employee", False),
            ("end_date", False),  # Expiring contracts
        )


class ContractAmendment(BaseModel):
    """Represent changes to a contract."""

    id = AutoField()
    contract = ForeignKeyField(Contract, backref="amendments")

    # Amendment details
    amendment_date = DateField()
    amendment_type = CharField(max_length=50)  # salary_change, position_change, hours_change, other
    description = TextField()

    # Old values (before change)
    old_field_name = CharField(max_length=50)
    old_value = CharField(max_length=500, null=True)

    # New values (after change)
    new_value = CharField(max_length=500, null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    created_by = CharField(max_length=100, null=True)
    document_path = CharField(max_length=500, null=True)  # Amendment document

    def __str__(self):
        return f"{self.contract} - {self.amendment_type} ({self.amendment_date})"
```

### Update Employee Model

```python
class Employee(BaseModel):
    """Employee model (updated)."""

    # ... existing fields ...

    # Remove or deprecate these:
    # contract_type = CharField(null=True)  # Use Contract.history instead

    @property
    def current_contract(self) -> Optional[Contract]:
        """Get current active contract."""
        try:
            return Contract.select().where(
                (Contract.employee == self) &
                (Contract.status == "active")
            ).order_by(Contract.start_date.desc()).first()
        except Contract.DoesNotExist:
            return None

    @property
    def contract_history(self) -> list[Contract]:
        """Get all contracts in chronological order."""
        return list(
            Contract.select()
            .where(Contract.employee == self)
            .order_by(Contract.start_date.desc())
        )

    @property
    def tenure_days(self) -> int:
        """Calculate total tenure (days since first hire)."""
        first_contract = Contract.select().where(
            Contract.employee == self
        ).order_by(Contract.start_date).first()

        if not first_contract:
            return 0

        return (date.today() - first_contract.start_date).days

    @property
    def experience_years(self) -> float:
        """Calculate total experience in years."""
        return self.tenure_days / 365.25

    @property
    def position_history(self) -> list[dict]:
        """Get position changes over time."""
        contracts = self.contract_history
        positions = []

        for contract in contracts:
            positions.append({
                "position": contract.position,
                "department": contract.department,
                "start_date": contract.start_date,
                "end_date": contract.end_date,
                "contract_type": contract.contract_type
            })

        return positions
```

### Contract Management UI

**Create: `src/ui_ctk/views/contract_history_view.py`**

```python
class ContractHistoryView(ctk.CTkFrame):
    """View for managing employee contract history."""

    def __init__(self, parent, employee, **kwargs):
        super().__init__(parent, **kwargs)
        self.employee = employee
        self.create_widgets()
        self.load_contracts()

    def create_widgets(self):
        """Create widgets."""
        # Employee info header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text=f"Contract History: {self.employee.full_name}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text=f"Tenure: {self.employee.experience_years:.1f} years"
        ).pack(side="left", padx=10)

        # Contract list
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Table header
        header_row = ctk.CTkFrame(list_frame)
        header_row.pack(fill="x")

        headers = ["Type", "Period", "Position", "Department", "Status"]
        for i, header_text in enumerate(headers):
            ctk.CTkLabel(
                header_row,
                text=header_text,
                font=("Arial", 12, "bold"),
                width=150
            ).pack(side="left", padx=5, pady=5)

        # Contract rows
        self.contracts_frame = ctk.CTkScrollableFrame(list_frame)
        self.contracts_frame.pack(fill="both", expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Add New Contract",
            command=self.add_contract,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Edit Contract",
            command=self.edit_contract
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="View Amendments",
            command=self.view_amendments
        ).pack(side="left", padx=5)

    def load_contracts(self):
        """Load and display contracts."""
        # Clear existing
        for widget in self.contracts_frame.winfo_children():
            widget.destroy()

        # Load contracts
        for contract in self.employee.contract_history:
            row = self.create_contract_row(contract)
            row.pack(fill="x", padx=5, pady=2)

    def create_contract_row(self, contract: Contract):
        """Create a row displaying contract info."""
        row = ctk.CTkFrame(self.contracts_frame)

        # Contract type
        type_label = ctk.CTkLabel(row, text=contract.contract_type, width=150)
        type_label.pack(side="left", padx=5)

        # Period
        if contract.end_date:
            period = f"{contract.start_date} → {contract.end_date}"
        else:
            period = f"{contract.start_date} → Present"
        period_label = ctk.CTkLabel(row, text=period, width=150)
        period_label.pack(side="left", padx=5)

        # Position
        pos_label = ctk.CTkLabel(row, text=contract.position, width=150)
        pos_label.pack(side="left", padx=5)

        # Department
        dept_label = ctk.CTkLabel(row, text=contract.department, width=150)
        dept_label.pack(side="left", padx=5)

        # Status
        status_color = "green" if contract.is_current else "gray"
        status_text = "Current" if contract.is_current else contract.status.title()
        status_label = ctk.CTkLabel(
            row,
            text=status_text,
            text_color=status_color,
            width=150
        )
        status_label.pack(side="left", padx=5)

        return row


class ContractForm(ctk.CTkToplevel):
    """Dialog for adding/editing contracts."""

    def __init__(self, parent, employee, contract=None):
        super().__init__(parent)
        self.employee = employee
        self.contract = contract

        self.title("Contract Details")
        self.geometry("600x700")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if contract:
            self.load_contract_data(contract)

    def create_widgets(self):
        """Create form widgets."""
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Contract type
        self.contract_type = self.create_labeled_input(
            main,
            "Contract Type:",
            ctk.CTkComboBox,
            values=["CDI", "CDD", "Interim", "Apprentissage", "Stage", "Freelance"]
        )

        # Dates
        self.start_date = self.create_labeled_input(
            main,
            "Start Date:",
            ctk.CTkEntry
        )

        self.end_date = self.create_labeled_input(
            main,
            "End Date (optional for CDI):",
            ctk.CTkEntry
        )

        self.trial_period_end = self.create_labeled_input(
            main,
            "Trial Period End (optional):",
            ctk.CTkEntry
        )

        # Position and department
        self.position = self.create_labeled_input(
            main,
            "Position:",
            ctk.CTkComboBox,
            values=["Operateur", "Magasinier", "Cariste", "Chef d'équipe"]
        )

        self.department = self.create_labeled_input(
            main,
            "Department:",
            ctk.CTkComboBox,
            values=["Logistique", "Production", "Maintenance", "Administration"]
        )

        # Salary and hours
        self.gross_salary = self.create_labeled_input(
            main,
            "Gross Salary (€):",
            ctk.CTkEntry
        )

        self.weekly_hours = self.create_labeled_input(
            main,
            "Weekly Hours:",
            ctk.CTkEntry,
            default="35.0"
        )

        # Status
        self.status = self.create_labeled_input(
            main,
            "Status:",
            ctk.CTkComboBox,
            values=["active", "ended", "cancelled"]
        )

        # Document upload
        doc_frame = ctk.CTkFrame(main)
        doc_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(doc_frame, text="Contract Document:").pack(side="left", padx=5)

        self.document_path = ctk.CTkLabel(doc_frame, text="No file selected")
        self.document_path.pack(side="left", padx=5)

        ctk.CTkButton(
            doc_frame,
            text="Browse",
            command=self.browse_document,
            width=100
        ).pack(side="left", padx=5)

        # Buttons
        button_frame = ctk.CTkFrame(main)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_contract,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="left", padx=5)

    def save_contract(self):
        """Save contract to database."""
        from employee.models import Contract
        from utils.file_storage import DocumentStorageManager

        # Validate inputs
        # ... validation code ...

        # Prepare data
        data = {
            "employee": self.employee,
            "contract_type": self.contract_type.get(),
            "start_date": self.parse_date(self.start_date.get()),
            "end_date": self.parse_date(self.end_date.get()) if self.end_date.get() else None,
            "trial_period_end": self.parse_date(self.trial_period_end.get()) if self.trial_period_end.get() else None,
            "position": self.position.get(),
            "department": self.department.get(),
            "gross_salary": Decimal(self.gross_salary.get()) if self.gross_salary.get() else None,
            "weekly_hours": Decimal(self.weekly_hours.get()),
            "status": self.status.get(),
        }

        if self.contract:
            # Update existing
            for key, value in data.items():
                setattr(self.contract, key, value)
            self.contract.updated_at = datetime.now()
            self.contract.save()
        else:
            # Create new
            self.contract = Contract.create(**data)

        # Handle document upload
        if hasattr(self, 'uploaded_document_path'):
            storage = DocumentStorageManager()
            stored_path = storage.store_document(
                doc_type="contracts",
                matricule=self.employee.matricule,
                file_path=Path(self.uploaded_document_path),
                metadata={
                    "file_name": Path(self.uploaded_document_path).name,
                    "document_type": "contract",
                    "contract_id": self.contract.id,
                    "version": 1
                }
            )
            self.contract.contract_document_path = str(stored_path)
            self.contract.save()

        self.destroy()
```

### Contract Evolution Tracking

```python
# src/reports/contract_evolution_report.py
def generate_evolution_report(employee: Employee) -> dict:
    """Generate contract evolution report for an employee."""
    contracts = employee.contract_history

    report = {
        "employee": employee,
        "total_contracts": len(contracts),
        "total_tenure_days": employee.tenure_days,
        "position_changes": [],
        "salary_evolution": [],
        "department_changes": [],
        "contract_type_changes": [],
        "gaps": []  # Periods without contract
    }

    previous_contract = None

    for contract in contracts:
        # Track position changes
        if previous_contract and previous_contract.position != contract.position:
            report["position_changes"].append({
                "from": previous_contract.position,
                "to": contract.position,
                "date": contract.start_date
            })

        # Track salary changes
        if contract.gross_salary:
            report["salary_evolution"].append({
                "salary": float(contract.gross_salary),
                "date": contract.start_date,
                "position": contract.position
            })

        # Track department changes
        if previous_contract and previous_contract.department != contract.department:
            report["department_changes"].append({
                "from": previous_contract.department,
                "to": contract.department,
                "date": contract.start_date
            })

        # Check for gaps between contracts
        if previous_contract:
            if previous_contract.end_date and contract.start_date:
                gap = (contract.start_date - previous_contract.end_date).days
                if gap > 0:
                    report["gaps"].append({
                        "start": previous_contract.end_date,
                        "end": contract.start_date,
                        "days": gap
                    })

        previous_contract = contract

    return report
```

## Affected Files

- `src/employee/models.py` - Add Contract and ContractAmendment models
- `src/ui_ctk/views/contract_history_view.py` - New contract history view
- `src/ui_ctk/forms/contract_form.py` - New contract form
- `src/reports/contract_evolution_report.py` - New evolution report
- Database migration for new tables
- Employee detail view - Add contract history tab

## Implementation Plan

### Phase 1: Data Model (1 day)
1. Create Contract model
2. Create ContractAmendment model
3. Update Employee model with properties
4. Create database migration
5. Add indexes for performance

### Phase 2: Contract Management UI (2 days)
1. Create contract history view
2. Create contract form (add/edit)
3. Integrate with employee detail view
4. Add document upload support

### Phase 3: Evolution Tracking (1 day)
1. Implement evolution report generator
2. Track position/salary/department changes
3. Detect gaps in employment
4. Create timeline visualization

### Phase 4: Migration from Old System (1 day)
1. Migrate existing entry_date to first contract
2. Migrate contract_type if exists
3. Validate data integrity
4. Test migration

### Phase 5: Integration and Testing (1 day)
1. Update alerts view to check contract expiration
2. Add contract alerts to configurable alerts
3. Test contract workflows
4. Performance testing

## Dependencies

- ISSUE-060: Hierarchical Document Storage (contract documents)
- ISSUE-061: Configurable Alert System (contract expiration alerts)

## Related Issues

- ISSUE-060: Hierarchical Document Storage
- ISSUE-061: Configurable Alert System
- ISSUE-064: Contract History Tracking

## Acceptance Criteria

- [ ] Contract model implemented
- [ ] ContractAmendment model implemented
- [ ] Employee.current_contract property works
- [ ] Employee.contract_history property works
- [ ] Contract history view functional
- [ ] Can add/edit/delete contracts
- [ ] Document upload works for contracts
- [ ] Evolution report generated
- [ ] Position changes tracked
- [ ] Salary evolution tracked
- [ ] Gaps in employment detected
- [ ] Contract expiration alerts work
- [ ] Migration from old system successful
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Data model: 1 day
- Contract management UI: 2 days
- Evolution tracking: 1 day
- Migration: 1 day
- Integration and testing: 1 day

## Notes

This is a critical HR feature. Proper contract tracking ensures legal compliance and provides a complete employment history. The evolution tracking helps identify career progression and patterns in employee movements.

## Example Use Cases

### Use Case 1: Contract Renewal

1. **Initial Contract:** CDD from 2024-01-01 to 2024-12-31
2. **Alert:** System warns at D-90 (October 2024)
3. **Renewal:** Create new CDI contract from 2025-01-01
4. **History:** Both contracts visible in timeline
5. **Evolution:** Shows transition from CDD to CDI

### Use Case 2: Promotion

1. **Initial Contract:** CDI as Magasinier (2023-01-01)
2. **Promotion:** Amendment to Chef d'Équipe (2024-06-01)
3. **Salary Update:** Amendment with new salary (2024-06-01)
4. **History:** Shows evolution with salary progression
5. **Report:** Career path visualization

### Use Case 3: Re-hiring

1. **First Contract:** CDD (2022-01-01 to 2022-12-31)
2. **Gap:** No contract (2023-01-01 to 2023-06-30) - 6 months
3. **Re-hiring:** New CDD (2023-07-01 to 2023-12-31)
4. **Gap Detection:** Report shows 6-month gap
5. **Tenure:** Total tenure calculated from first hire

## Future Enhancements

- Contract templates (pre-filled standard contracts)
- Automatic contract generation from templates
- Contract renewal workflow (approval process)
- Integration with payroll software
- Contract expiration notifications
- Trial period alerts
- Multi-contract tracking (multiple simultaneous contracts)
- Export contract history to PDF
