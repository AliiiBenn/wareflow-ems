# ISSUE-062: Equipment Operation Authorization System

## Description

The system currently tracks certifications but doesn't enforce whether an employee is authorized to operate specific equipment (chariots/forklifts). Users need to define and enforce rules that prevent equipment operation if all required conditions are not met.

## Current State

- Certifications are tracked (CACES, medical visits, training)
- No link between certifications and equipment authorization
- No validation of authorization before equipment operation
- No visual indicator of who can operate what equipment
- No reporting on unauthorized operation attempts

## Expected Behavior

### Equipment Model

**Add to: `src/employee/models.py`**

```python
class Equipment(BaseModel):
    """Represent equipment that requires authorization."""

    id = AutoField()
    name = CharField(max_length=100)  # e.g., "Chariot Élévateur 1"
    type = CharField(max_length=50)  # e.g., "Forklift", "Crane", "Platform"
    serial_number = CharField(max_length=100, null=True)
    location = CharField(max_length=100, null=True)
    status = CharField(max_length=20, default="active")  # active, maintenance, retired
    notes = TextField(null=True)

    def can_be_operated_by(self, employee: Employee) -> tuple[bool, list[str]]:
        """
        Check if employee is authorized to operate this equipment.

        Returns:
            Tuple of (is_authorized, list_of_reasons)
        """
        requirements = EquipmentRequirement.select().where(EquipmentRequirement.equipment == self)
        reasons = []

        for requirement in requirements:
            if not requirement.is_satisfied_by(employee):
                reasons.append(requirement.get_failure_message())

        return len(reasons) == 0, reasons


class EquipmentRequirement(BaseModel):
    """Requirements for operating equipment."""

    id = AutoField()
    equipment = ForeignKeyField(Equipment, backref="requirements")
    requirement_type = CharField(max_length=50)  # caces, medical, training, contract
    caces_type = CharField(max_length=50, null=True)  # Required if type=caces
    training_name = CharField(max_length=100, null=True)  # Required if type=training
    min_days_valid = IntegerField(default=30)  # Certificate must be valid this many more days
    required = BooleanField(default=True)  # If True, must have this certification

    def is_satisfied_by(self, employee: Employee) -> bool:
        """Check if employee satisfies this requirement."""
        if self.requirement_type == "caces":
            return self._check_caces(employee)
        elif self.requirement_type == "medical":
            return self._check_medical(employee)
        elif self.requirement_type == "training":
            return self._check_training(employee)
        elif self.requirement_type == "contract":
            return self._check_contract(employee)
        return False

    def _check_caces(self, employee: Employee) -> bool:
        """Check if employee has valid CACES certification."""
        caces = CACES.select().where(
            (CACES.employee == employee) &
            (CACES.caces_type == self.caces_type)
        ).first()

        if not caces:
            return not self.required

        # Check if still valid
        if caces.expiration_date:
            days_until = (caces.expiration_date - date.today()).days
            return days_until >= self.min_days_valid

        return True

    def _check_medical(self, employee: Employee) -> bool:
        """Check if employee has valid medical visit."""
        visit = MedicalVisit.select().where(
            MedicalVisit.employee == employee
        ).order_by(MedicalVisit.visit_date.desc()).first()

        if not visit:
            return not self.required

        # Check next due date
        if visit.next_due_date:
            days_until = (visit.next_due_date - date.today()).days
            return days_until >= self.min_days_valid

        return True

    def _check_training(self, employee: Employee) -> bool:
        """Check if employee has required training."""
        training = Training.select().where(
            (Training.employee == employee) &
            (Training.training_name == self.training_name)
        ).first()

        if not training:
            return not self.required

        # Check if expired
        if training.expiration_date:
            days_until = (training.expiration_date - date.today()).days
            return days_until >= self.min_days_valid

        return True

    def _check_contract(self, employee: Employee) -> bool:
        """Check if employee has valid contract."""
        if not employee.current_contract:
            return not self.required

        # Check if contract is active
        if employee.current_contract.end_date:
            days_until = (employee.current_contract.end_date - date.today()).days
            return days_until >= self.min_days_valid

        return True

    def get_failure_message(self) -> str:
        """Get human-readable failure message."""
        if self.requirement_type == "caces":
            return f"Requires valid {self.caces_type} certification (min {self.min_days_valid} days valid)"
        elif self.requirement_type == "medical":
            return f"Requires valid medical visit (min {self.min_days_valid} days valid)"
        elif self.requirement_type == "training":
            return f"Requires {self.training_name} training (min {self.min_days_valid} days valid)"
        elif self.requirement_type == "contract":
            return f"Requires valid employment contract (min {self.min_days_valid} days valid)"
        return "Authorization requirement not met"


class EquipmentOperationLog(BaseModel):
    """Log equipment operation attempts."""

    id = AutoField()
    equipment = ForeignKeyField(Equipment, backref="operation_logs")
    employee = ForeignKeyField(Employee, backref="operation_logs")
    timestamp = DateTimeField(default=datetime.now)
    authorized = BooleanField()
    reasons = TextField(null=True)  # JSON array of reasons if not authorized
    operation_type = CharField(max_length=50)  # start, stop, check
```

### Equipment Management UI

**Create: `src/ui_ctk/views/equipment_view.py`**

```python
class EquipmentView(ctk.CTkFrame):
    """View for managing equipment and authorizations."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.selected_equipment = None
        self.create_widgets()
        self.load_equipment()

    def create_widgets(self):
        """Create widgets."""
        # Equipment list
        self.equipment_list = self.create_equipment_list()
        self.equipment_list.pack(side="left", fill="both", expand=True)

        # Equipment details
        self.details_panel = self.create_details_panel()
        self.details_panel.pack(side="right", fill="both", expand=True)

    def create_details_panel(self):
        """Create equipment details panel."""
        panel = ctk.CTkFrame(self)

        # Equipment info
        info_frame = ctk.CTkFrame(panel)
        info_frame.pack(fill="x", padx=10, pady=10)

        # Authorization status
        auth_frame = ctk.CTkFrame(panel)
        auth_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            auth_frame,
            text="Authorization Requirements",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Requirements list
        self.requirements_list = ctk.CTkScrollableFrame(auth_frame)
        self.requirements_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(panel)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Add Requirement",
            command=self.add_requirement
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Check Authorization",
            command=self.check_authorization
        ).pack(side="left", padx=5)

        # Employee selector
        employee_frame = ctk.CTkFrame(panel)
        employee_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            employee_frame,
            text="Check Employee Authorization:"
        ).pack(side="left", padx=5)

        self.employee_selector = ctk.CTkComboBox(
            employee_frame,
            values=[e.full_name for e in Employee.select()]
        )
        self.employee_selector.pack(side="left", padx=5)

        return panel

    def check_authorization(self):
        """Check if selected employee can operate equipment."""
        if not self.selected_equipment:
            return

        employee_name = self.employee_selector.get()
        employee = Employee.select().where(Employee.full_name == employee_name).first()

        if not employee:
            return

        is_authorized, reasons = self.selected_equipment.can_be_operated_by(employee)

        # Show result dialog
        AuthorizationResultDialog(self, employee, self.selected_equipment, is_authorized, reasons)


class AuthorizationResultDialog(ctk.CTkToplevel):
    """Dialog showing authorization check result."""

    def __init__(self, parent, employee, equipment, is_authorized, reasons):
        super().__init__(parent)

        self.title("Authorization Check Result")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        self.create_widgets(employee, equipment, is_authorized, reasons)

    def create_widgets(self, employee, equipment, is_authorized, reasons):
        """Create dialog widgets."""
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Result
        if is_authorized:
            result_label = ctk.CTkLabel(
                main,
                text=f"✓ AUTHORIZED",
                font=("Arial", 24, "bold"),
                text_color="green"
            )
            result_label.pack(pady=20)

            info = ctk.CTkLabel(
                main,
                text=f"{employee.full_name} is authorized to operate {equipment.name}",
                font=("Arial", 14)
            )
            info.pack(pady=10)
        else:
            result_label = ctk.CTkLabel(
                main,
                text=f"✗ NOT AUTHORIZED",
                font=("Arial", 24, "bold"),
                text_color="red"
            )
            result_label.pack(pady=20)

            info = ctk.CTkLabel(
                main,
                text=f"{employee.full_name} is NOT authorized to operate {equipment.name}",
                font=("Arial", 14)
            )
            info.pack(pady=10)

            # Reasons
            if reasons:
                reasons_frame = ctk.CTkFrame(main)
                reasons_frame.pack(fill="both", expand=True, pady=20)

                ctk.CTkLabel(
                    reasons_frame,
                    text="Reasons:",
                    font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=10, pady=10)

                for reason in reasons:
                    reason_label = ctk.CTkLabel(
                        reasons_frame,
                        text=f"• {reason}",
                        text_color="red"
                    )
                    reason_label.pack(anchor="w", padx=20, pady=5)

        # Log the check
        EquipmentOperationLog.create(
            equipment=equipment,
            employee=employee,
            authorized=is_authorized,
            reasons=json.dumps(reasons) if reasons else None,
            operation_type="check"
        )

        # Close button
        ctk.CTkButton(
            main,
            text="Close",
            command=self.destroy
        ).pack(pady=20)
```

### Equipment Authorization Report

**Add report showing:**

1. Equipment and authorized operators
2. Operators near expiration (won't be authorized soon)
3. Unauthorized operation attempts
4. Equipment with no authorized operators

```python
# src/reports/equipment_authorization_report.py
def generate_authorization_report():
    """Generate equipment authorization report."""
    report = {
        "equipment": [],
        "unauthorized_attempts": [],
        "expiring_soon": []
    }

    for equipment in Equipment.select():
        authorized_operators = []
        all_operators = []

        for employee in Employee.select():
            is_authorized, reasons = equipment.can_be_operated_by(employee)
            operator_info = {
                "employee": employee,
                "authorized": is_authorized,
                "reasons": reasons
            }
            all_operators.append(operator_info)
            if is_authorized:
                authorized_operators.append(employee)

        report["equipment"].append({
            "equipment": equipment,
            "authorized_count": len(authorized_operators),
            "authorized_operators": authorized_operators,
            "all_operators": all_operators
        })

    return report
```

## Affected Files

- `src/employee/models.py` - Add Equipment, EquipmentRequirement, EquipmentOperationLog models
- `src/ui_ctk/views/equipment_view.py` - New equipment management view
- `src/ui_ctk/dialogs/authorization_result_dialog.py` - New authorization result dialog
- `src/reports/equipment_authorization_report.py` - New authorization report
- Database migration for new tables

## Implementation Plan

### Phase 1: Data Model (1 day)
1. Create Equipment model
2. Create EquipmentRequirement model
3. Create EquipmentOperationLog model
4. Create database migration
5. Add authorization check methods

### Phase 2: Equipment Management UI (2 days)
1. Create equipment view with list
2. Add equipment creation/editing
3. Add requirement management
4. Add authorization check dialog
5. Integrate with main window

### Phase 3: Authorization Logic (1 day)
1. Implement authorization check algorithm
2. Add validation for requirements
3. Handle edge cases (expired, missing certifications)
4. Add operation logging

### Phase 4: Reporting (1 day)
1. Create authorization report
2. Add equipment authorization summary
3. Export to Excel
4. Add scheduling for regular reports

## Dependencies

- None (new functionality)

## Related Issues

- ISSUE-060: Hierarchical Document Storage (certification tracking)
- ISSUE-061: Configurable Alert System (uses same validation logic)
- ISSUE-064: Contract History Tracking (contract validation)

## Acceptance Criteria

- [ ] Equipment model implemented
- [ ] EquipmentRequirement model implemented
- [ ] Authorization check logic works correctly
- [ ] Can define requirements per equipment
- [ ] Multiple requirement types supported (CACES, medical, training, contract)
- [ ] Configurable minimum validity period
- [ ] Authorization check dialog shows clear results
- [ ] Operation attempts logged
- [ ] Authorization report generated
- [ ] Excel export of authorization report
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Data model: 1 day
- Equipment management UI: 2 days
- Authorization logic: 1 day
- Reporting: 1 day
- Testing and integration: 0.5-1 day

## Notes

This is a critical safety feature. Ensuring only properly certified employees can operate equipment prevents accidents and ensures compliance with safety regulations.

## Example Use Cases

### Example 1: Forklift Authorization

Equipment: "Chariot Élévateur 1"
Requirements:
- CACES 1A or 1B (min 30 days valid)
- Valid medical visit (min 30 days valid)
- Active contract

Result: Only employees meeting ALL requirements are authorized.

### Example 2: Crane Authorization

Equipment: "Pont Roulant 5T"
Requirements:
- CACES 3 (min 60 days valid)
- Specific training "Pont Roulant" (min 30 days valid)
- Valid medical visit (min 60 days valid)

Result: More stringent requirements for heavy equipment.

## Future Enhancements

- Equipment authorization schedule (who is authorized when)
- Temporary authorization (with supervisor approval)
- Authorization expiration warnings
- Equipment operation time tracking
- Integration with access control systems
- Mobile authorization verification (QR codes)
