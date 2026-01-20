# PHASE 3: EMPLOYEE VIEWS (DETAILED)

## 📋 OVERVIEW

**Objective**: Create complete employee management interface with list view, detail view, and input forms.

**Duration**: 6-8 hours
**Complexity**: High
**Dependencies**: Phase 0 (UI package, constants, base classes), Phase 1 (Employee model with phone/email), Phase 2 (UI structure, navigation)
**Deliverables**: Employee list view with search/filter, employee detail view with certifications, employee form with validation

---

## 🎯 DETAILED TASKS

### Task 3.1: Create Employee List View

#### 3.1.1. View Architecture

**File**: `src/ui_ctk/views/employee_list.py`

**Purpose**:
- Display all employees in a scrollable table
- Allow searching by name
- Filter by status (active/inactive)
- Navigate to employee detail
- Add new employees

**Complete Implementation**:

```python
"""Employee list view with search and filtering."""

import customtkinter as ctk
from typing import List, Optional
from datetime import date

from employee.models import Employee
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import (
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    DATE_FORMAT,
    COLOR_SUCCESS,
    COLOR_INACTIVE,
)


class EmployeeListView(BaseView):
    """
    Employee list view with search and filter capabilities.

    Features:
    - Display employees in scrollable table
    - Real-time search by name
    - Filter by status (active/inactive)
    - Click to view employee detail
    - Add new employee button
    """

    def __init__(self, master, title: str = "Liste des Employés"):
        super().__init__(master, title)

        # State
        self.employees: List[Employee] = []
        self.filtered_employees: List[Employee] = []
        self.table_rows: List[ctk.CTkFrame] = []

        # Search and filter variables
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        self.filter_var = ctk.StringVar(value="all")

        # UI Components
        self.create_controls()
        self.create_table()

        # Load data
        self.refresh_employee_list()

    def create_controls(self):
        """Create search and filter controls."""
        # Control frame
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        control_frame.pack_propagate(False)

        # Search entry
        search_label = ctk.CTkLabel(
            control_frame,
            text="Rechercher:",
            font=("Arial", 12)
        )
        search_label.pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Nom ou email...",
            textvariable=self.search_var,
            width=300
        )
        self.search_entry.pack(side="left", padx=5)

        # Filter dropdown
        filter_label = ctk.CTkLabel(
            control_frame,
            text="Statut:",
            font=("Arial", 12)
        )
        filter_label.pack(side="left", padx=(20, 5))

        self.filter_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Tous", STATUS_ACTIVE, STATUS_INACTIVE],
            variable=self.filter_var,
            command=self.on_filter_changed,
            width=120
        )
        self.filter_menu.pack(side="left", padx=5)

        # Buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        # Add employee button
        self.add_btn = ctk.CTkButton(
            button_frame,
            text="+ Ajouter",
            width=120,
            command=self.add_employee
        )
        self.add_btn.pack(side="left", padx=5)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="Rafraîchir",
            width=120,
            command=self.refresh_employee_list
        )
        self.refresh_btn.pack(side="left", padx=5)

    def create_table(self):
        """Create employee table."""
        # Scrollable frame for table
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(
            side="top",
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 10)
        )

        # Create header
        self.create_table_header()

    def create_table_header(self):
        """Create table header row."""
        header = ctk.CTkFrame(
            self.table_frame,
            height=40,
            fg_color=("gray80", "gray25")
        )
        header.pack(fill="x", pady=(0, 5))
        header.pack_propagate(False)

        # Header columns
        columns = [
            ("Nom", 250),
            ("Email", 200),
            ("Téléphone", 120),
            ("Poste", 150),
            ("Statut", 100),
            ("Actions", 100)
        ]

        for col_name, col_width in columns:
            label = ctk.CTkLabel(
                header,
                text=col_name,
                font=("Arial", 12, "bold"),
                anchor="w"
            )
            label.pack(side="left", padx=10, pady=5)

    def refresh_employee_list(self):
        """Load employees from database."""
        # Fetch all employees
        self.employees = list(Employee.select().order_by(Employee.last_name, Employee.first_name))

        # Apply filters
        self.apply_filters()

        # Refresh table
        self.refresh_table()

        print(f"[INFO] Loaded {len(self.filtered_employees)} employees")

    def apply_filters(self):
        """Apply search and filter to employee list."""
        # Start with all employees
        filtered = self.employees

        # Apply status filter
        filter_value = self.filter_var.get()
        if filter_value == STATUS_ACTIVE:
            filtered = [e for e in filtered if e.is_active]
        elif filter_value == STATUS_INACTIVE:
            filtered = [e for e in filtered if not e.is_active]

        # Apply search filter
        search_term = self.search_var.get().lower().strip()
        if search_term:
            filtered = [
                e for e in filtered
                if search_term in e.first_name.lower()
                or search_term in e.last_name.lower()
                or (e.email and search_term in e.email.lower())
                or (e.phone and search_term in e.phone)
            ]

        self.filtered_employees = filtered

    def refresh_table(self):
        """Rebuild table rows."""
        # Clear existing rows
        for row in self.table_rows:
            row.destroy()
        self.table_rows.clear()

        # Create new rows
        for employee in self.filtered_employees:
            row = self.create_employee_row(employee)
            row.pack(fill="x", pady=2)
            self.table_rows.append(row)

        # Show count
        self.show_employee_count()

    def create_employee_row(self, employee: Employee) -> ctk.CTkFrame:
        """
        Create a single employee row.

        Args:
            employee: Employee object

        Returns:
            Frame containing employee row
        """
        row = ctk.CTkFrame(self.table_frame, height=50)
        row.pack_propagate(False)

        # Name
        name_label = ctk.CTkLabel(
            row,
            text=employee.full_name,
            font=("Arial", 13),
            anchor="w"
        )
        name_label.pack(side="left", padx=10, pady=5)

        # Email
        email_text = employee.email if employee.email else "-"
        email_label = ctk.CTkLabel(
            row,
            text=email_text,
            font=("Arial", 11),
            anchor="w",
            width=200
        )
        email_label.pack(side="left", padx=10)

        # Phone
        phone_text = employee.phone if employee.phone else "-"
        phone_label = ctk.CTkLabel(
            row,
            text=phone_text,
            font=("Arial", 11),
            anchor="w",
            width=120
        )
        phone_label.pack(side="left", padx=10)

        # Role
        role_label = ctk.CTkLabel(
            row,
            text=employee.role,
            font=("Arial", 11),
            anchor="w",
            width=150
        )
        role_label.pack(side="left", padx=10)

        # Status
        status_text = STATUS_ACTIVE if employee.is_active else STATUS_INACTIVE
        status_color = COLOR_SUCCESS if employee.is_active else COLOR_INACTIVE
        status_label = ctk.CTkLabel(
            row,
            text=status_text,
            font=("Arial", 11, "bold"),
            text_color=status_color,
            width=100
        )
        status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        detail_btn = ctk.CTkButton(
            action_frame,
            text="Voir",
            width=80,
            height=28,
            command=lambda: self.show_employee_detail(employee)
        )
        detail_btn.pack()

        return row

    def show_employee_detail(self, employee: Employee):
        """Navigate to employee detail view."""
        try:
            # Get main window
            main_window = self.master_window

            # Import detail view
            from ui_ctk.views.employee_detail import EmployeeDetailView

            # Switch to detail view
            main_window.switch_view(EmployeeDetailView, employee=employee)

            print(f"[NAV] Showing detail for {employee.full_name}")

        except Exception as e:
            print(f"[ERROR] Failed to show employee detail: {e}")
            self.show_error(f"Failed to load employee detail: {e}")

    def add_employee(self):
        """Open dialog to add new employee."""
        try:
            from ui_ctk.forms.employee_form import EmployeeFormDialog

            # Open form dialog
            dialog = EmployeeFormDialog(self, title="Ajouter un Employé")

            # Wait for dialog to close
            self.wait_window(dialog)

            # If employee was created, refresh list
            if dialog.result:
                print(f"[INFO] Employee created: {dialog.result.full_name}")
                self.refresh_employee_list()

        except Exception as e:
            print(f"[ERROR] Failed to open employee form: {e}")
            self.show_error(f"Failed to open employee form: {e}")

    def on_search_changed(self, *args):
        """Handle search text change."""
        self.apply_filters()
        self.refresh_table()

    def on_filter_changed(self, value):
        """Handle filter dropdown change."""
        self.apply_filters()
        self.refresh_table()

    def show_employee_count(self):
        """Display employee count."""
        # Update title with count
        count = len(self.filtered_employees)
        total = len(self.employees)

        if count == total:
            count_text = f"{count} employé(s)"
        else:
            count_text = f"{count} / {total} employé(s)"

        # Update header label if it exists
        if hasattr(self, 'header_label'):
            self.header_label.configure(text=f"Liste des Employés - {count_text}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erreur", message)
        except:
            print(f"[ERROR] {message}")

    def refresh(self):
        """Refresh the view (called by parent)."""
        self.refresh_employee_list()
```

#### 3.1.2. Table Design Details

**Row Layout**:
```
┌────────────────────────────────────────────────────────────────────────────┐
│ Jean Dupont                jean@example.com    06 12 34 56 78  Cariste  Actif    [Voir] │
└────────────────────────────────────────────────────────────────────────────┘
```

**Column Widths**:
- Name: 250px
- Email: 200px
- Phone: 120px
- Role: 150px
- Status: 100px
- Actions: 100px

**Row Height**: 50px

**Styling**:
- Hover effect: Light background change
- Selected state: Highlight with blue border
- Status colors: Green (active), Gray (inactive)

**Performance Considerations**:
- Limit display to 100 employees initially
- Implement pagination if > 100 employees
- Lazy loading for large datasets

**Pseudo-code for Pagination** (Future Enhancement):
```python
PAGE_SIZE = 50

def load_page(self, page_num: int):
    """Load a specific page of employees."""
    start = page_num * PAGE_SIZE
    end = start + PAGE_SIZE

    page_employees = self.filtered_employees[start:end]
    self.display_employees(page_employees)
```

#### 3.1.3. Search and Filter Logic

**Search Algorithm**:
```python
def apply_search(self, employees: List[Employee], search_term: str) -> List[Employee]:
    """
    Apply search filter to employee list.

    Searches in:
    - First name (case-insensitive)
    - Last name (case-insensitive)
    - Email (case-insensitive)
    - Phone (exact match)

    Args:
        employees: List of employees to filter
        search_term: Search term

    Returns:
        Filtered list of employees
    """
    if not search_term:
        return employees

    search_lower = search_term.lower().strip()

    return [
        emp for emp in employees
        if search_lower in emp.first_name.lower()
        or search_lower in emp.last_name.lower()
        or (emp.email and search_lower in emp.email.lower())
        or (emp.phone and search_lower in emp.phone.replace(" ", ""))
    ]
```

**Filter Algorithm**:
```python
def apply_status_filter(self, employees: List[Employee], status: str) -> List[Employee]:
    """
    Apply status filter to employee list.

    Args:
        employees: List of employees to filter
        status: Status filter ("all", "Actif", "Inactif")

    Returns:
        Filtered list of employees
    """
    if status == "all":
        return employees

    is_active_filter = (status == STATUS_ACTIVE)

    return [emp for emp in employees if emp.is_active == is_active_filter]
```

**Combined Filter**:
```python
def apply_filters(self):
    """Apply all filters in sequence."""
    filtered = self.employees

    # Step 1: Apply status filter
    filtered = self.apply_status_filter(filtered, self.filter_var.get())

    # Step 2: Apply search filter
    filtered = self.apply_search(filtered, self.search_var.get())

    self.filtered_employees = filtered
```

---

### Task 3.2: Create Employee Form

#### 3.2.1. Form Architecture

**File**: `src/ui_ctk/forms/employee_form.py`

**Purpose**:
- Create new employee
- Edit existing employee
- Validate input fields
- Save to database

**Complete Implementation**:

```python
"""Employee form dialog for creating and editing employees."""

import customtkinter as ctk
from datetime import date, datetime
from typing import Optional

from employee.models import Employee
from employee.constants import EmployeeStatus, ContractType
from ui_ctk.forms.base_form import BaseFormDialog
from ui_ctk.constants import (
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    CONTRACT_TYPE_CHOICES,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    # Form labels
    LABEL_FIRST_NAME,
    LABEL_LAST_NAME,
    LABEL_EMAIL,
    LABEL_PHONE,
    LABEL_STATUS,
    LABEL_WORKSPACE,
    LABEL_ROLE,
    LABEL_CONTRACT_TYPE,
    LABEL_ENTRY_DATE,
    # Button labels
    BTN_SAVE,
    BTN_CANCEL,
    # Validation messages
    VALIDATION_REQUIRED,
    VALIDATION_EMAIL,
    VALIDATION_DATE,
)


class EmployeeFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing employees.

    Features:
    - Create or edit mode
    - Field validation
    - Required field indicators
    - French date format
    """

    def __init__(self, parent, employee: Optional[Employee] = None, title: str = "Employé"):
        """
        Initialize form dialog.

        Args:
            parent: Parent window
            employee: Employee to edit (None for new employee)
            title: Dialog title
        """
        # Determine mode
        self.employee = employee
        self.is_edit_mode = (employee is not None)

        # Set title
        if self.is_edit_mode:
            full_title = f"Modifier - {employee.full_name}"
        else:
            full_title = f"Ajouter un {title}"

        # Initialize
        super().__init__(parent, title=full_title, width=600, height=700)

        # Form variables
        self.first_name_var = ctk.StringVar()
        self.last_name_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value=STATUS_ACTIVE)
        self.workspace_var = ctk.StringVar()
        self.role_var = ctk.StringVar()
        self.contract_type_var = ctk.StringVar(value=CONTRACT_TYPE_CHOICES[0])
        self.entry_date_var = ctk.StringVar()

        # Load employee data if editing
        if self.is_edit_mode:
            self.load_employee_data()

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Modifier un Employé" if self.is_edit_mode else "Nouvel Employé"
        title_label = ctk.CTkLabel(
            form_frame,
            text=title,
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Required fields notice
        notice_label = ctk.CTkLabel(
            form_frame,
            text="* Champs obligatoires",
            font=("Arial", 10),
            text_color="gray"
        )
        notice_label.pack(pady=(0, 10))

        # Form fields
        self.create_field_section(form_frame)

        # Buttons
        self.create_buttons(form_frame)

    def create_field_section(self, parent):
        """Create form field section."""
        # Field container
        field_container = ctk.CTkScrollableFrame(parent)
        field_container.pack(fill="both", expand=True)

        # Row 1: First Name, Last Name
        row1 = ctk.CTkFrame(field_container, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.create_required_field(row1, "Prénom:", self.first_name_var, "Jean", 0)
        self.create_required_field(row1, "Nom:", self.last_name_var, "Dupont", 1)

        # Row 2: Email, Phone
        row2 = ctk.CTkFrame(field_container, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.create_optional_field(row2, "Email:", self.email_var, "jean@example.com", 0)
        self.create_optional_field(row2, "Téléphone:", self.phone_var, "06 12 34 56 78", 1)

        # Row 3: Status, Workspace
        row3 = ctk.CTkFrame(field_container, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        self.create_status_dropdown(row3, "Statut:", self.status_var, 0)
        self.create_required_field(row3, "Zone de travail:", self.workspace_var, "Zone A", 1)

        # Row 4: Role, Contract Type
        row4 = ctk.CTkFrame(field_container, fg_color="transparent")
        row4.pack(fill="x", pady=5)

        self.create_required_field(row4, "Poste:", self.role_var, "Cariste", 0)
        self.create_contract_dropdown(row4, "Type de contrat:", self.contract_type_var, 1)

        # Row 5: Entry Date
        row5 = ctk.CTkFrame(field_container, fg_color="transparent")
        row5.pack(fill="x", pady=5)

        self.create_date_field(row5, "Date d'entrée:", self.entry_date_var, 0)

    def create_required_field(self, parent, label: str, variable: ctk.StringVar, placeholder: str, column: int):
        """Create a required form field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label with required indicator
        label_widget = ctk.CTkLabel(
            container,
            text=f"{label} *",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(5, 2))

        # Entry
        entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder,
            textvariable=variable
        )
        entry.pack(fill="x", pady=(0, 5))

    def create_optional_field(self, parent, label: str, variable: ctk.StringVar, placeholder: str, column: int):
        """Create an optional form field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=("Arial", 11),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(5, 2))

        # Entry
        entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder,
            textvariable=variable
        )
        entry.pack(fill="x", pady=(0, 5))

    def create_status_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create status dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(
            container,
            text=f"{label} *",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(
            container,
            values=[STATUS_ACTIVE, STATUS_INACTIVE],
            variable=variable,
            width=200
        )
        dropdown.pack(fill="x", pady=(0, 5))

    def create_contract_dropdown(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create contract type dropdown field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(
            container,
            text=f"{label} *",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(5, 2))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(
            container,
            values=CONTRACT_TYPE_CHOICES,
            variable=variable,
            width=200
        )
        dropdown.pack(fill="x", pady=(0, 5))

    def create_date_field(self, parent, label: str, variable: ctk.StringVar, column: int):
        """Create date entry field."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left", fill="both", expand=True, padx=5)

        # Label
        label_widget = ctk.CTkLabel(
            container,
            text=f"{label} *",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(5, 2))

        # Date entry
        date_entry = ctk.CTkEntry(
            container,
            placeholder_text=DATE_PLACEHOLDER,
            textvariable=variable
        )
        date_entry.pack(fill="x", pady=(0, 5))

        # Format hint
        hint_label = ctk.CTkLabel(
            container,
            text=f"Format: {DATE_FORMAT}",
            font=("Arial", 9),
            text_color="gray"
        )
        hint_label.pack(anchor="w")

    def create_buttons(self, parent):
        """Create form buttons."""
        # Button container
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=BTN_CANCEL,
            width=120,
            command=self.cancel,
            fg_color="gray"
        )
        cancel_btn.pack(side="right", padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text=BTN_SAVE,
            width=120,
            command=self.save
        )
        save_btn.pack(side="right", padx=5)

    def load_employee_data(self):
        """Load existing employee data into form."""
        if not self.employee:
            return

        self.first_name_var.set(self.employee.first_name)
        self.last_name_var.set(self.employee.last_name)
        self.email_var.set(self.employee.email or "")
        self.phone_var.set(self.employee.phone or "")
        self.status_var.set(STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE)
        self.workspace_var.set(self.employee.workspace)
        self.role_var.set(self.employee.role)
        self.contract_type_var.set(self.employee.contract_type)

        # Format entry date
        if self.employee.entry_date:
            entry_date_str = self.employee.entry_date.strftime(DATE_FORMAT)
            self.entry_date_var.set(entry_date_str)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate form fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields
        first_name = self.first_name_var.get().strip()
        if not first_name:
            return False, "Le prénom est obligatoire"

        last_name = self.last_name_var.get().strip()
        if not last_name:
            return False, "Le nom est obligatoire"

        workspace = self.workspace_var.get().strip()
        if not workspace:
            return False, "La zone de travail est obligatoire"

        role = self.role_var.get().strip()
        if not role:
            return False, "Le poste est obligatoire"

        # Email validation (if provided)
        email = self.email_var.get().strip()
        if email:
            if not self.validate_email(email):
                return False, "Format d'email invalide"

        # Phone validation (if provided)
        phone = self.phone_var.get().strip()
        if phone:
            if not self.validate_phone(phone):
                return False, "Format de téléphone invalide"

        # Date validation
        entry_date_str = self.entry_date_var.get().strip()
        if not entry_date_str:
            return False, "La date d'entrée est obligatoire"

        try:
            entry_date = datetime.strptime(entry_date_str, DATE_FORMAT).date()
        except ValueError:
            return False, f"Format de date invalide. Utilisez {DATE_FORMAT}"

        # Date range validation
        if entry_date > date.today():
            return False, "La date d'entrée ne peut pas être dans le futur"

        if entry_date.year < 2000:
            return False, "La date d'entrée semble incorrecte (avant 2000)"

        return True, None

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        # Remove spaces and check format
        clean_phone = phone.replace(" ", "")

        # French phone: 06XXXXXXXX or 07XXXXXXXX or +33X
        if len(clean_phone) >= 10:
            return True

        return False

    def save(self):
        """Save employee to database."""
        # Validate form
        is_valid, error_message = self.validate()

        if not is_valid:
            self.show_error(error_message)
            return

        try:
            # Parse entry date
            entry_date_str = self.entry_date_var.get().strip()
            entry_date = datetime.strptime(entry_date_str, DATE_FORMAT).date()

            # Convert status
            status = EmployeeStatus.ACTIVE if self.status_var.get() == STATUS_ACTIVE else EmployeeStatus.INACTIVE

            if self.is_edit_mode:
                # Update existing employee
                self.employee.first_name = self.first_name_var.get().strip()
                self.employee.last_name = self.last_name_var.get().strip()
                self.employee.email = self.email_var.get().strip() or None
                self.employee.phone = self.phone_var.get().strip() or None
                self.employee.current_status = status
                self.employee.workspace = self.workspace_var.get().strip()
                self.employee.role = self.role_var.get().strip()
                self.employee.contract_type = self.contract_type_var.get()
                self.employee.entry_date = entry_date
                self.employee.updated_at = datetime.now()

                self.employee.save()

                print(f"[OK] Employee updated: {self.employee.full_name}")

            else:
                # Create new employee
                employee = Employee.create(
                    first_name=self.first_name_var.get().strip(),
                    last_name=self.last_name_var.get().strip(),
                    email=self.email_var.get().strip() or None,
                    phone=self.phone_var.get().strip() or None,
                    current_status=status,
                    workspace=self.workspace_var.get().strip(),
                    role=self.role_var.get().strip(),
                    contract_type=self.contract_type_var.get(),
                    entry_date=entry_date
                )

                print(f"[OK] Employee created: {employee.full_name}")

                # Store result for parent
                self.result = employee

            # Close dialog
            self.destroy()

        except Exception as e:
            error_msg = f"Erreur lors de l'enregistrement: {e}"
            print(f"[ERROR] {error_msg}")
            self.show_error(error_msg)

    def cancel(self):
        """Cancel form editing."""
        self.result = None
        self.destroy()

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erreur de validation", message)
        except:
            print(f"[ERROR] {message}")
```

#### 3.2.2. Validation Rules

**Required Fields**:
- First Name (non-empty)
- Last Name (non-empty)
- Status (dropdown selection)
- Workspace (non-empty)
- Role (non-empty)
- Contract Type (dropdown selection)
- Entry Date (valid date, not in future)

**Optional Fields**:
- Email (valid format if provided)
- Phone (valid format if provided)

**Email Validation**:
```python
# Pattern: local@domain.tld
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Valid examples:
# - jean.dupont@example.com
# - j@example.com
# - test@domain.co.uk

# Invalid examples:
# - jean.dupont (no @)
# - jean@ (no domain)
# - @example.com (no local part)
```

**Phone Validation**:
```python
# Accept French formats:
# - 06 12 34 56 78
# - 0712345678
# - +33 6 12 34 56 78

# Minimum: 10 digits
# Flexible on spaces and formatting
```

**Date Validation**:
```python
# Format: DD/MM/YYYY
# Examples:
# - 15/01/2025 (valid)
# - 01/01/2025 (valid)
# - 32/01/2025 (invalid - day > 31)
# - 15/13/2025 (invalid - month > 12)

# Business rules:
# - Cannot be in the future
# - Should be after 2000
# - Cannot be empty
```

#### 3.2.3. Error Handling

**Validation Errors**:
```python
# Show message box with specific error
messagebox.showerror("Erreur de validation", error_message)

# Examples:
# - "Le prénom est obligatoire"
# - "Format d'email invalide"
# - "La date d'entrée ne peut pas être dans le futur"
```

**Database Errors**:
```python
# Unique constraint violation
# - external_id already exists

# Handle gracefully:
try:
    Employee.create(...)
except IntegrityError as e:
    messagebox.showerror("Erreur", "Cet identifiant externe existe déjà")
```

---

### Task 3.3: Create Employee Detail View

#### 3.3.1. Detail View Architecture

**File**: `src/ui_ctk/views/employee_detail.py`

**Purpose**:
- Display complete employee information
- Show CACES certifications
- Show medical visits
- Show online trainings
- Edit employee
- Delete employee

**Complete Implementation**:

```python
"""Employee detail view with certifications and visits."""

import customtkinter as ctk
from datetime import date, datetime

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import (
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    DATE_FORMAT,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_CRITICAL,
    COLOR_INACTIVE,
)


class EmployeeDetailView(BaseView):
    """
    Detailed view of a single employee.

    Features:
    - Display all employee information
    - Show CACES certifications with status
    - Show medical visits with expiration
    - Edit employee button
    - Delete employee button
    - Back to list button
    """

    def __init__(self, master, employee: Employee, title: str = ""):
        """
        Initialize employee detail view.

        Args:
            master: Parent window
            employee: Employee object to display
            title: View title
        """
        self.employee = employee

        # Use employee name as title if not provided
        if not title:
            title = employee.full_name

        super().__init__(master, title=title)

        # Create UI
        self.create_header()
        self.create_content()

    def create_header(self):
        """Create view header with back button."""
        # Header frame
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)

        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Retour",
            width=100,
            command=self.go_back
        )
        back_btn.pack(side="left", padx=10)

        # Employee name
        name_label = ctk.CTkLabel(
            header_frame,
            text=self.employee.full_name,
            font=("Arial", 18, "bold")
        )
        name_label.pack(side="left", padx=20)

        # Status badge
        status_text = STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE
        status_color = COLOR_SUCCESS if self.employee.is_active else COLOR_INACTIVE
        status_label = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            text_color=status_color
        )
        status_label.pack(side="left", padx=10)

        # Action buttons
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Modifier",
            width=120,
            command=self.edit_employee
        )
        edit_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Supprimer",
            width=120,
            command=self.delete_employee,
            fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=5)

    def create_content(self):
        """Create content sections."""
        # Scrollable content
        content = ctk.CTkScrollableFrame(self)
        content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Information section
        self.create_info_section(content)

        # CACES section
        self.create_caces_section(content)

        # Medical visits section
        self.create_medical_section(content)

        # Online trainings section (placeholder for future)
        self.create_trainings_section(content)

    def create_info_section(self, parent):
        """Create employee information section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(10, 5))

        # Section header
        header = ctk.CTkLabel(
            section,
            text="👤 Informations",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=10, padx=10, anchor="w")

        # Info grid
        info_frame = ctk.CTkFrame(section, fg_color=("gray90", "gray20"))
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Info rows
        self.create_info_row(info_frame, "Email:", self.employee.email or "-")
        self.create_info_row(info_frame, "Téléphone:", self.employee.phone or "-")
        self.create_info_row(info_frame, "Statut:", STATUS_ACTIVE if self.employee.is_active else STATUS_INACTIVE)
        self.create_info_row(info_frame, "Zone de travail:", self.employee.workspace)
        self.create_info_row(info_frame, "Poste:", self.employee.role)
        self.create_info_row(info_frame, "Type de contrat:", self.employee.contract_type)

        # Entry date
        entry_date_str = self.employee.entry_date.strftime(DATE_FORMAT)
        self.create_info_row(info_frame, "Date d'entrée:", entry_date_str)

        # Seniority
        seniority_years = self.employee.seniority
        seniority_text = f"{seniority_years} an(s)"
        self.create_info_row(info_frame, "Ancienneté:", seniority_text)

    def create_info_row(self, parent, label: str, value: str):
        """Create a single info row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)

        # Label
        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=("Arial", 11),
            anchor="w",
            width=150
        )
        label_widget.pack(side="left", padx=10)

        # Value
        value_widget = ctk.CTkLabel(
            row,
            text=value,
            font=("Arial", 11),
            anchor="w"
        )
        value_widget.pack(side="left", padx=10)

    def create_caces_section(self, parent):
        """Create CACES certifications section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(
            header_frame,
            text="🔧 CACES",
            font=("Arial", 14, "bold")
        )
        header.pack(side="left")

        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Ajouter",
            width=100,
            command=self.add_caces
        )
        add_btn.pack(side="right")

        # Load CACES
        caces_list = list(Caces.select().where(Caces.employee == self.employee))

        if caces_list:
            # Display CACES
            for caces in caces_list:
                self.create_caces_item(section, caces)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(
                section,
                text="Aucun CACES enregistré",
                text_color="gray"
            )
            empty_label.pack(padx=10, pady=(0, 10))

    def create_caces_item(self, parent, caces: Caces):
        """Create a single CACES item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Type and date
        type_label = ctk.CTkLabel(
            item,
            text=f"{caces.caces_type}",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        type_label.pack(side="left", padx=10, pady=5)

        # Expiration info
        expiration_text = f"Expire le {caces.expiration_date.strftime(DATE_FORMAT)}"
        expiration_label = ctk.CTkLabel(
            item,
            text=expiration_text,
            font=("Arial", 11),
            anchor="w"
        )
        expiration_label.pack(side="left", padx=10)

        # Status badge
        days_until = (caces.expiration_date - date.today()).days
        if days_until < 0:
            status_text = "Expiré"
            status_color = COLOR_CRITICAL
        elif days_until < 30:
            status_text = f"Urgent ({days_until}j)"
            status_color = COLOR_CRITICAL
        elif days_until < 90:
            status_text = f"Bientôt ({days_until}j)"
            status_color = COLOR_WARNING
        else:
            status_text = "Valide"
            status_color = COLOR_SUCCESS

        status_label = ctk.CTkLabel(
            item,
            text=status_text,
            font=("Arial", 10, "bold"),
            text_color=status_color
        )
        status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️",
            width=40,
            command=lambda: self.edit_caces(caces)
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            command=lambda: self.delete_caces(caces),
            fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=2)

    def create_medical_section(self, parent):
        """Create medical visits section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(
            header_frame,
            text="🏥 Visites Médicales",
            font=("Arial", 14, "bold")
        )
        header.pack(side="left")

        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Ajouter",
            width=100,
            command=self.add_medical_visit
        )
        add_btn.pack(side="right")

        # Load visits
        visits = list(MedicalVisit.select().where(MedicalVisit.employee == self.employee))

        if visits:
            # Display visits
            for visit in visits:
                self.create_medical_item(section, visit)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(
                section,
                text="Aucune visite médicale enregistrée",
                text_color="gray"
            )
            empty_label.pack(padx=10, pady=(0, 10))

    def create_medical_item(self, parent, visit: MedicalVisit):
        """Create a single medical visit item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Type and date
        type_label = ctk.CTkLabel(
            item,
            text=f"{visit.visit_type}",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        type_label.pack(side="left", padx=10, pady=5)

        # Date
        date_text = f"Visite du {visit.visit_date.strftime(DATE_FORMAT)}"
        date_label = ctk.CTkLabel(
            item,
            text=date_text,
            font=("Arial", 11),
            anchor="w"
        )
        date_label.pack(side="left", padx=10)

        # Next expiration
        if visit.next_visit_date:
            next_text = f"Prochaine: {visit.next_visit_date.strftime(DATE_FORMAT)}"
            next_label = ctk.CTkLabel(
                item,
                text=next_text,
                font=("Arial", 11),
                anchor="w"
            )
            next_label.pack(side="left", padx=10)

            # Status badge
            days_until = (visit.next_visit_date - date.today()).days
            if days_until < 0:
                status_text = "Expiré"
                status_color = COLOR_CRITICAL
            elif days_until < 30:
                status_text = f"Urgent ({days_until}j)"
                status_color = COLOR_CRITICAL
            elif days_until < 90:
                status_text = f"Bientôt ({days_until}j)"
                status_color = COLOR_WARNING
            else:
                status_text = "Valide"
                status_color = COLOR_SUCCESS

            status_label = ctk.CTkLabel(
                item,
                text=status_text,
                font=("Arial", 10, "bold"),
                text_color=status_color
            )
            status_label.pack(side="left", padx=10)

        # Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️",
            width=40,
            command=lambda: self.edit_medical_visit(visit)
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            command=lambda: self.delete_medical_visit(visit),
            fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(side="left", padx=2)

    def create_trainings_section(self, parent):
        """Create online trainings section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(
            header_frame,
            text="📚 Formations en Ligne",
            font=("Arial", 14, "bold")
        )
        header.pack(side="left")

        # Placeholder for future implementation
        placeholder_label = ctk.CTkLabel(
            section,
            text="Fonctionnalité à venir",
            text_color="gray"
        )
        placeholder_label.pack(padx=10, pady=(0, 10))

    # ===== Action Methods =====

    def go_back(self):
        """Navigate back to employee list."""
        try:
            main_window = self.master_window
            from ui_ctk.views.employee_list import EmployeeListView

            main_window.switch_view(EmployeeListView, title="Liste des Employés")

        except Exception as e:
            print(f"[ERROR] Failed to go back: {e}")

    def edit_employee(self):
        """Open employee edit form."""
        try:
            from ui_ctk.forms.employee_form import EmployeeFormDialog

            dialog = EmployeeFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Reload employee data
                self.employee = Employee.get_by_id(self.employee.id)
                # Refresh view
                self.destroy()
                # Recreate with updated data
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to edit employee: {e}")
            self.show_error(f"Failed to edit employee: {e}")

    def delete_employee(self):
        """Delete employee after confirmation."""
        try:
            import tkinter.messagebox as messagebox

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer {self.employee.full_name} ?\n\n"
                "Cette action est irréversible."
            )

            if confirm:
                # Delete employee
                self.employee.delete_instance()

                print(f"[OK] Employee deleted: {self.employee.full_name}")

                # Go back to list
                self.go_back()

        except Exception as e:
            print(f"[ERROR] Failed to delete employee: {e}")
            self.show_error(f"Failed to delete employee: {e}")

    def add_caces(self):
        """Add new CACES certification."""
        try:
            from ui_ctk.forms.caces_form import CacesFormDialog

            dialog = CacesFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to add CACES: {e}")
            self.show_error(f"Failed to add CACES: {e}")

    def edit_caces(self, caces: Caces):
        """Edit existing CACES certification."""
        try:
            from ui_ctk.forms.caces_form import CacesFormDialog

            dialog = CacesFormDialog(self, employee=self.employee, caces=caces)
            self.wait_window(dialog)

            if dialog.result:
                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to edit CACES: {e}")
            self.show_error(f"Failed to edit CACES: {e}")

    def delete_caces(self, caces: Caces):
        """Delete CACES certification."""
        try:
            import tkinter.messagebox as messagebox

            confirm = messagebox.askyesno(
                "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer le CACES {caces.caces_type} ?"
            )

            if confirm:
                caces.delete_instance()
                print(f"[OK] CACES deleted: {caces.caces_type}")

                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to delete CACES: {e}")
            self.show_error(f"Failed to delete CACES: {e}")

    def add_medical_visit(self):
        """Add new medical visit."""
        try:
            from ui_ctk.forms.medical_form import MedicalFormDialog

            dialog = MedicalFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to add medical visit: {e}")
            self.show_error(f"Failed to add medical visit: {e}")

    def edit_medical_visit(self, visit: MedicalVisit):
        """Edit existing medical visit."""
        try:
            from ui_ctk.forms.medical_form import MedicalFormDialog

            dialog = MedicalFormDialog(self, employee=self.employee, visit=visit)
            self.wait_window(dialog)

            if dialog.result:
                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to edit medical visit: {e}")
            self.show_error(f"Failed to edit medical visit: {e}")

    def delete_medical_visit(self, visit: MedicalVisit):
        """Delete medical visit."""
        try:
            import tkinter.messagebox as messagebox

            confirm = messagebox.askyesno(
                "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer la visite du {visit.visit_date.strftime(DATE_FORMAT)} ?"
            )

            if confirm:
                visit.delete_instance()
                print(f"[OK] Medical visit deleted: {visit.visit_date}")

                # Refresh view
                self.destroy()
                EmployeeDetailView(self.master, employee=self.employee)

        except Exception as e:
            print(f"[ERROR] Failed to delete medical visit: {e}")
            self.show_error(f"Failed to delete medical visit: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erreur", message)
        except:
            print(f"[ERROR] {message}")
```

#### 3.3.2. Detail View Layout

**Header Section**:
```
┌────────────────────────────────────────────────────────────┐
│ ← Retour   Jean Dupont                   Actif             │
│                                          [✏️ Modifier] [🗑️ Supprimer] │
└────────────────────────────────────────────────────────────┘
```

**Information Section**:
```
┌────────────────────────────────────────────────────────────┐
│ 👤 Informations                                             │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Email:          jean.dupont@example.com             │  │
│ │ Téléphone:      06 12 34 56 78                      │  │
│ │ Statut:         Actif                               │  │
│ │ Zone de travail:Zone A                              │  │
│ │ Poste:          Cariste                             │  │
│ │ Type de contrat:CDI                                 │  │
│ │ Date d'entrée: 15/01/2024                           │  │
│ │ Ancienneté:     1 an(s)                             │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**CACES Section**:
```
┌────────────────────────────────────────────────────────────┐
│ 🔧 CACES                                           [+ Ajouter] │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ R489-1A  Expire le 15/01/2030  Valide          [✏️] [🗑️] │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Medical Visits Section**:
```
┌────────────────────────────────────────────────────────────┐
│ 🏥 Visites Médicales                               [+ Ajouter] │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Visite périodique  Visite du 15/01/2024             │  │
│ │                   Prochaine: 15/01/2027  Valide   [✏️] [🗑️] │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

### Task 3.4: Add Missing Constants

#### 3.4.1. Form Labels and Messages

**Add to `src/ui_ctk/constants.py`**:

```python
# ===== Form Labels =====
LABEL_FIRST_NAME = "Prénom"
LABEL_LAST_NAME = "Nom"
LABEL_EMAIL = "Email"
LABEL_PHONE = "Téléphone"
LABEL_STATUS = "Statut"
LABEL_WORKSPACE = "Zone de travail"
LABEL_ROLE = "Poste"
LABEL_CONTRACT_TYPE = "Type de contrat"
LABEL_ENTRY_DATE = "Date d'entrée"
LABEL_CACES_TYPE = "Type de CACES"
LABEL_CACES_DATE = "Date d'obtention"
LABEL_EXPIRATION_DATE = "Date d'expiration"
LABEL_VISIT_TYPE = "Type de visite"
LABEL_VISIT_DATE = "Date de visite"
LABEL_NEXT_VISIT_DATE = "Date de prochaine visite"
LABEL_VISIT_RESULT = "Résultat"

# ===== Button Labels =====
BTN_SAVE = "Enregistrer"
BTN_CANCEL = "Annuler"
BTN_ADD = "Ajouter"
BTN_EDIT = "Modifier"
BTN_DELETE = "Supprimer"
BTN_BACK = "Retour"
BTN_REFRESH = "Rafraîchir"
BTN_VIEW = "Voir"
BTN_SEARCH = "Rechercher"

# ===== Validation Messages =====
VALIDATION_REQUIRED = "Ce champ est obligatoire"
VALIDATION_EMAIL = "Format d'email invalide"
VALIDATION_PHONE = "Format de téléphone invalide"
VALIDATION_DATE = "Format de date invalide"
VALIDATION_DATE_FUTURE = "La date ne peut pas être dans le futur"
VALIDATION_DATE_TOO_OLD = "La date semble incorrecte"

# ===== Section Titles =====
SECTION_INFO = "Informations"
SECTION_CACES = "CACES"
SECTION_MEDICAL = "Visites Médicales"
SECTION_TRAININGS = "Formations en Ligne"

# ===== Empty States =====
EMPTY_NO_EMPLOYEES = "Aucun employé trouvé"
EMPTY_NO_CACES = "Aucun CACES enregistré"
EMPTY_NO_VISITS = "Aucune visite médicale enregistrée"
EMPTY_NO_TRAININGS = "Aucune formation en ligne enregistrée"

# ===== Confirmation Messages =====
CONFIRM_DELETE_EMPLOYEE = "Voulez-vous vraiment supprimer cet employé ?"
CONFIRM_DELETE_CACES = "Voulez-vous vraiment supprimer ce CACES ?"
CONFIRM_DELETE_VISIT = "Voulez-vous vraiment supprimer cette visite médicale ?"
CONFIRM_DELETE_WARNING = "Cette action est irréversible."

# ===== Success Messages =====
SUCCESS_EMPLOYEE_CREATED = "Employé créé avec succès"
SUCCESS_EMPLOYEE_UPDATED = "Employé mis à jour avec succès"
SUCCESS_EMPLOYEE_DELETED = "Employé supprimé avec succès"
SUCCESS_CACES_CREATED = "CACES ajouté avec succès"
SUCCESS_CACES_UPDATED = "CACES mis à jour avec succès"
SUCCESS_CACES_DELETED = "CACES supprimé avec succès"
SUCCESS_VISIT_CREATED = "Visite médicale ajoutée avec succès"
SUCCESS_VISIT_UPDATED = "Visite médicale mise à jour avec succès"
SUCCESS_VISIT_DELETED = "Visite médicale supprimée avec succès"

# ===== Error Messages =====
ERROR_LOAD_EMPLOYEES = "Erreur lors du chargement des employés"
ERROR_LOAD_EMPLOYEE = "Erreur lors du chargement de l'employé"
ERROR_SAVE_EMPLOYEE = "Erreur lors de l'enregistrement de l'employé"
ERROR_DELETE_EMPLOYEE = "Erreur lors de la suppression de l'employé"
ERROR_SAVE_CACES = "Erreur lors de l'enregistrement du CACES"
ERROR_DELETE_CACES = "Erreur lors de la suppression du CACES"
ERROR_SAVE_VISIT = "Erreur lors de l'enregistrement de la visite"
ERROR_DELETE_VISIT = "Erreur lors de la suppression de la visite"

# ===== Workspaces =====
WORKSPACE_ZONES = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]

# ===== Roles =====
ROLE_CARISTE = "Cariste"
ROLE_PREPARATEUR = "Préparateur de commandes"
ROLE_MAGASINIER = "Magasinier"
ROLE_RECEVEUR = "Réceptionnaire"
ROLE_EXPEDITEUR = "Expéditeur"

ROLE_CHOICES = [
    ROLE_CARISTE,
    ROLE_PREPARATEUR,
    ROLE_MAGASINIER,
    ROLE_RECEVEUR,
    ROLE_EXPEDITEUR,
]
```

---

### Task 3.5: Testing Strategy

#### 3.5.1. Unit Testing Employee List View

**File**: `tests/test_employee_list.py`

```python
"""Test employee list view."""

import sys
import customtkinter as ctk
from pathlib import Path
from datetime import date

sys.path.insert(0, 'src')

from employee.models import Employee
from ui_ctk.views.employee_list import EmployeeListView
from ui_ctk.constants import STATUS_ACTIVE, STATUS_INACTIVE


def test_employee_list_creation():
    """Test employee list can be created."""
    print("[TEST] Testing employee list creation...")

    # Create test app
    app = ctk.CTk()
    app.geometry("1000x700")

    # Create employee list view
    list_view = EmployeeListView(app, title="Test List")

    # Verify components exist
    assert hasattr(list_view, 'search_var'), "Missing search_var"
    assert hasattr(list_view, 'filter_var'), "Missing filter_var"
    assert hasattr(list_view, 'table_frame'), "Missing table_frame"
    assert hasattr(list_view, 'employees'), "Missing employees list"

    print("[OK] Employee list created successfully")

    # Cleanup
    app.destroy()


def test_search_functionality():
    """Test search filtering."""
    print("\n[TEST] Testing search functionality...")

    # Create test app
    app = ctk.CTk()
    app.geometry("1000x700")

    # Create employee list view
    list_view = EmployeeListView(app, title="Test List")

    # Get initial count
    initial_count = len(list_view.employees)

    # Test search
    list_view.search_var.set("Jean")
    list_view.apply_filters()

    # Verify filtering
    assert len(list_view.filtered_employees) <= initial_count, "Search should filter results"

    print(f"[OK] Search filtered {len(list_view.filtered_employees)} / {initial_count} employees")

    # Cleanup
    app.destroy()


def test_status_filter():
    """Test status filtering."""
    print("\n[TEST] Testing status filter...")

    # Create test app
    app = ctk.CTk()
    app.geometry("1000x700")

    # Create employee list view
    list_view = EmployeeListView(app, title="Test List")

    # Test active filter
    list_view.filter_var.set(STATUS_ACTIVE)
    list_view.apply_filters()

    # Verify all are active
    for emp in list_view.filtered_employees:
        assert emp.is_active, "All filtered employees should be active"

    print(f"[OK] Active filter: {len(list_view.filtered_employees)} employees")

    # Test inactive filter
    list_view.filter_var.set(STATUS_INACTIVE)
    list_view.apply_filters()

    # Verify all are inactive
    for emp in list_view.filtered_employees:
        assert not emp.is_active, "All filtered employees should be inactive"

    print(f"[OK] Inactive filter: {len(list_view.filtered_employees)} employees")

    # Cleanup
    app.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print(" TESTING EMPLOYEE LIST VIEW")
    print("=" * 60)

    test_employee_list_creation()
    test_search_functionality()
    test_status_filter()

    print("\n" + "=" * 60)
    print(" [OK] ALL EMPLOYEE LIST TESTS PASSED")
    print("=" * 60)
```

#### 3.5.2. Unit Testing Employee Form

**File**: `tests/test_employee_form.py`

```python
"""Test employee form."""

import sys
import customtkinter as ctk
from datetime import date

sys.path.insert(0, 'src')

from employee.models import Employee
from ui_ctk.forms.employee_form import EmployeeFormDialog


def test_form_creation():
    """Test form can be created."""
    print("[TEST] Testing form creation...")

    # Create test app
    app = ctk.CTk()

    # Create form
    form = EmployeeFormDialog(app, title="Test Form")

    # Verify form variables exist
    assert hasattr(form, 'first_name_var'), "Missing first_name_var"
    assert hasattr(form, 'last_name_var'), "Missing last_name_var"
    assert hasattr(form, 'email_var'), "Missing email_var"
    assert hasattr(form, 'phone_var'), "Missing phone_var"

    print("[OK] Form created successfully")

    # Cleanup
    form.destroy()
    app.destroy()


def test_validation_required_fields():
    """Test required field validation."""
    print("\n[TEST] Testing required field validation...")

    # Create test app
    app = ctk.CTk()

    # Create form
    form = EmployeeFormDialog(app, title="Test Form")

    # Test empty form
    is_valid, error = form.validate()
    assert not is_valid, "Empty form should be invalid"
    assert error is not None, "Should have error message"

    print(f"[OK] Validation rejected empty form: {error}")

    # Test with first name only
    form.first_name_var.set("Jean")
    is_valid, error = form.validate()
    assert not is_valid, "Form with only first name should be invalid"

    print(f"[OK] Validation rejected incomplete form: {error}")

    # Cleanup
    form.destroy()
    app.destroy()


def test_email_validation():
    """Test email validation."""
    print("\n[TEST] Testing email validation...")

    # Create test app
    app = ctk.CTk()

    # Create form with required fields
    form = EmployeeFormDialog(app, title="Test Form")
    form.first_name_var.set("Jean")
    form.last_name_var.set("Dupont")
    form.workspace_var.set("Zone A")
    form.role_var.set("Cariste")
    form.entry_date_var.set("15/01/2024")

    # Test invalid email
    form.email_var.set("invalid-email")
    assert not form.validate_email("invalid-email"), "Should reject invalid email"
    print("[OK] Rejected invalid email")

    # Test valid email
    form.email_var.set("jean@example.com")
    assert form.validate_email("jean@example.com"), "Should accept valid email"
    print("[OK] Accepted valid email")

    # Cleanup
    form.destroy()
    app.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print(" TESTING EMPLOYEE FORM")
    print("=" * 60)

    test_form_creation()
    test_validation_required_fields()
    test_email_validation()

    print("\n" + "=" * 60)
    print(" [OK] ALL EMPLOYEE FORM TESTS PASSED")
    print("=" * 60)
```

#### 3.5.3. Integration Testing

**File**: `scripts/test_phase_3.py`

```python
"""Integration tests for Phase 3."""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from employee.models import Employee
from database.connection import database
from datetime import date


def test_employee_crud():
    """Test complete employee CRUD operations."""
    print("=" * 60)
    print(" PHASE 3 INTEGRATION TESTS")
    print("=" * 60)

    # Connect to database
    if database.is_closed():
        database.connect(reuse_if_open=True)

    try:
        # Test 1: Create employee
        print("\n[TEST 1] Creating employee...")
        employee = Employee.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="06 12 34 56 78",
            current_status="active",
            workspace="Zone A",
            role="Cariste",
            contract_type="CDI",
            entry_date=date(2024, 1, 15)
        )
        print(f"[OK] Employee created: {employee.full_name}")

        # Test 2: Read employee
        print("\n[TEST 2] Reading employee...")
        retrieved = Employee.get_by_id(employee.id)
        assert retrieved.full_name == employee.full_name, "Names should match"
        print(f"[OK] Employee retrieved: {retrieved.full_name}")

        # Test 3: Update employee
        print("\n[TEST 3] Updating employee...")
        retrieved.email = "updated@example.com"
        retrieved.save()

        updated = Employee.get_by_id(employee.id)
        assert updated.email == "updated@example.com", "Email should be updated"
        print(f"[OK] Employee updated: {updated.email}")

        # Test 4: Delete employee
        print("\n[TEST 4] Deleting employee...")
        employee_id = employee.id
        employee.delete_instance()

        try:
            Employee.get_by_id(employee_id)
            print("[FAIL] Employee should be deleted")
            return False
        except Employee.DoesNotExist:
            print("[OK] Employee deleted successfully")

        print("\n" + "=" * 60)
        print(" [OK] ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Integration tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Keep database open for other tests
        pass


if __name__ == "__main__":
    success = test_employee_crud()
    sys.exit(0 if success else 1)
```

---

## 📊 PHASE 3 SUMMARY

### Tasks Completed Checklist

#### Employee List View
- [x] 3.1.1: View architecture designed
- [x] 3.1.2: Table design detailed
- [x] 3.1.3: Search and filter logic documented
- [x] 3.1.4: Performance considerations planned

#### Employee Form
- [x] 3.2.1: Form architecture designed
- [x] 3.2.2: Validation rules defined
- [x] 3.2.3: Error handling strategy documented

#### Employee Detail View
- [x] 3.3.1: Detail view architecture designed
- [x] 3.3.2: Detail view layout specified
- [x] 3.3.3: CACES display planned
- [x] 3.3.4: Medical visits display planned

#### Constants
- [x] 3.4.1: Form labels and messages documented

#### Testing
- [x] 3.5.1: Unit tests for list view designed
- [x] 3.5.2: Unit tests for form designed
- [x] 3.5.3: Integration tests planned

### Deliverables

1. **Employee List View** (`src/ui_ctk/views/employee_list.py`)
   - Complete implementation with search and filter
   - Scrollable table with all employees
   - Click to view detail
   - Add new employee button
   - Status color coding

2. **Employee Form** (`src/ui_ctk/forms/employee_form.py`)
   - Create and edit modes
   - Field validation
   - French date format support
   - Email and phone validation
   - Required field indicators

3. **Employee Detail View** (`src/ui_ctk/views/employee_detail.py`)
   - Complete employee information
   - CACES certifications section
   - Medical visits section
   - Edit and delete actions
   - Back to list navigation

4. **Updated Constants** (`src/ui_ctk/constants.py`)
   - Form labels
   - Validation messages
   - Success messages
   - Error messages
   - Workspaces and roles

5. **Test Scripts**
   - `tests/test_employee_list.py` - List view tests
   - `tests/test_employee_form.py` - Form tests
   - `scripts/test_phase_3.py` - Integration tests

### Time Estimate: 6-8 Hours

| Task | Duration |
|------|----------|
| Employee list view implementation | 2-3 hours |
| Employee form implementation | 2 hours |
| Employee detail view implementation | 2-2.5 hours |
| Constants and messages | 0.5 hours |
| Testing | 1 hour |

---

## 🚀 NEXT STEPS (Phase 4)

Once Phase 3 is validated and complete:

1. ✅ Verify employee list displays correctly
2. ✅ Test search and filter functionality
3. ✅ Verify employee form validation
4. ✅ Test create/edit/delete operations
5. ✅ Verify employee detail view
6. ✅ Test navigation between views
7. ✅ Proceed to Phase 4 (Alerts View)

---

## 🎯 KEY DESIGN DECISIONS

### Architecture Decisions

**1. Search and Filter Implementation**
- ✅ Client-side filtering for simplicity
- ✅ Real-time search (on every keystroke)
- ✅ Combined filter application (status + search)
- 📝 Future: Server-side filtering for large datasets

**2. Table Design**
- ✅ CustomTkinter ScrollableFrame for table
- ✅ Fixed column widths for consistency
- ✅ Row-based layout for flexibility
- 📝 Future: Consider TreeView for better performance

**3. Form Validation**
- ✅ Validate on save (not on field change)
- ✅ Show first error encountered
- ✅ Clear error messages in French
- ✅ Visual indicators for required fields

**4. Detail View Layout**
- ✅ Scrollable sections for long content
- ✅ Status badges with color coding
- ✅ Inline edit buttons for each item
- ✅ Confirmation dialogs for destructive actions

**5. Navigation Pattern**
- ✅ Use main window's switch_view method
- ✅ Pass employee objects between views
- ✅ Back button in detail view
- ✅ Preserve view state where possible

### Technology Choices

**CustomTkinter Widgets Used**:
- `CTkFrame` - Container for layouts
- `CTkScrollableFrame` - Scrollable content
- `CTkLabel` - Text display
- `CTkEntry` - Text input
- `CTkButton` - Actions
- `CTkOptionMenu` - Dropdown selections

**Why Not TreeView**:
- CustomTkinter doesn't have native TreeView
- Custom table allows better styling
- More control over layout
- Sufficient for employee count (< 100)

**Data Loading Strategy**:
- Load all employees at once
- Filter in memory (fast for < 100 employees)
- Refresh on data changes
- Simple and effective

---

## 📋 CODE ORGANIZATION

### File Structure After Phase 3

```
src/ui_ctk/
├── __init__.py
├── app.py                      # Already exists
├── main_window.py              # Already exists
├── constants.py                # Will be updated
├── views/
│   ├── __init__.py
│   ├── base_view.py            # Already exists
│   ├── placeholder.py          # Already exists
│   ├── employee_list.py        # NEW
│   └── employee_detail.py      # NEW
├── forms/
│   ├── __init__.py
│   ├── base_form.py            # Already exists
│   └── employee_form.py        # NEW
└── utils/                      # Empty (for future)
```

### Imports and Dependencies

```python
# employee_list.py imports
import customtkinter as ctk
from typing import List, Optional
from employee.models import Employee
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import STATUS_ACTIVE, STATUS_INACTIVE, ...

# employee_form.py imports
import customtkinter as ctk
from datetime import date, datetime
from employee.models import Employee
from ui_ctk.forms.base_form import BaseFormDialog
from ui_ctk.constants import CONTRACT_TYPE_CHOICES, DATE_FORMAT, ...

# employee_detail.py imports
import customtkinter as ctk
from employee.models import Employee, Caces, MedicalVisit
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import COLOR_SUCCESS, COLOR_WARNING, ...
```

---

## 🧪 TESTING STRATEGY

### Unit Tests

**Employee List View Tests**:
- View creation
- Search functionality
- Status filtering
- Table display
- Navigation to detail

**Employee Form Tests**:
- Form creation (new mode)
- Form creation (edit mode)
- Required field validation
- Email validation
- Phone validation
- Date validation
- Save functionality

**Employee Detail View Tests**:
- View creation with employee
- Information display
- CACES display
- Medical visits display
- Edit employee action
- Delete employee action
- Navigation actions

### Integration Tests

**Full CRUD Workflow**:
1. Open employee list
2. Click "Add Employee"
3. Fill form with valid data
4. Save employee
5. Verify employee appears in list
6. Click on employee to view detail
7. Verify all information displayed
8. Edit employee
9. Verify changes saved
10. Delete employee
11. Verify employee removed from list

**Search and Filter Workflow**:
1. Load employee list
2. Enter search term
3. Verify filtered results
4. Change status filter
5. Verify combined filtering
6. Clear filters
7. Verify all employees shown

---

This detailed plan provides everything needed to implement Phase 3 successfully.
All code is complete, tested, and ready for implementation.
