"""Contract amendment form dialog for tracking contract changes."""

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from employee.constants import CONTRACT_AMENDMENT_TYPES
from employee.models import Contract, ContractAmendment
from ui_ctk.constants import (
    BTN_CANCEL,
    BTN_SAVE,
    DATE_FORMAT,
    DATE_PLACEHOLDER,
    VALIDATION_DATE_REQUIRED,
)
from ui_ctk.forms.base_form import BaseFormDialog


class ContractAmendmentFormDialog(BaseFormDialog):
    """
    Dialog for creating/editing contract amendments.

    Features:
    - Track changes to salary, position, department, hours
    - Automatic field tracking
    - Document upload support
    - Create and edit modes
    """

    # Field mappings for amendment types
    FIELD_OPTIONS = {
        "gross_salary": "Salary (€)",
        "position": "Position",
        "department": "Department",
        "weekly_hours": "Weekly Hours",
        "trial_period_end": "Trial Period End",
    }

    def __init__(self, parent, contract: Contract, amendment: Optional[ContractAmendment] = None):
        """
        Initialize contract amendment form dialog.

        Args:
            parent: Parent window
            contract: Contract object (required)
            amendment: ContractAmendment object to edit (None for new amendment)
        """
        self.contract = contract
        self.amendment = amendment
        self.is_edit_mode = amendment is not None

        # Form variables
        self.amendment_type_var = ctk.StringVar()
        self.amendment_date_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.old_field_name_var = ctk.StringVar()
        self.old_value_var = ctk.StringVar()
        self.new_value_var = ctk.StringVar()
        self.document_path_var = ctk.StringVar()

        # Determine title
        if self.is_edit_mode:
            title = f"Edit Amendment - {amendment.amendment_type}"
        else:
            title = "Add Contract Amendment"

        # Initialize parent
        super().__init__(parent, title=title, width=500, height=600)

        # Track these variables for unsaved changes detection
        self.state_manager.track_variable("amendment_type", self.amendment_type_var)
        self.state_manager.track_variable("amendment_date", self.amendment_date_var)
        self.state_manager.track_variable("description", self.description_var)
        self.state_manager.track_variable("old_field_name", self.old_field_name_var)
        self.state_manager.track_variable("old_value", self.old_value_var)
        self.state_manager.track_variable("new_value", self.new_value_var)
        self.state_manager.track_variable("document_path", self.document_path_var)

        # Load amendment data if editing
        if self.is_edit_mode:
            self.load_amendment_data()

        # Bind amendment type change to update field options
        self.amendment_type_var.trace_add('write', self.on_amendment_type_changed)

    def create_form(self):
        """Create form widgets."""
        # Main form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Form title
        title = "Edit Contract Amendment" if self.is_edit_mode else "New Contract Amendment"
        title_label = ctk.CTkLabel(form_frame, text=title, font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))

        # Required fields notice
        notice_label = ctk.CTkLabel(form_frame, text="* Required fields", font=("Arial", 10), text_color="gray")
        notice_label.pack(pady=(0, 10))

        # Contract info
        info_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        info_row.pack(fill="x", pady=5)
        info_text = f"Contract: {self.contract.contract_type} - {self.contract.position}"
        info_label = ctk.CTkLabel(info_row, text=info_text, font=("Arial", 11, "bold"), text_color="gray")
        info_label.pack(side="left", padx=10)

        # Form fields
        self.create_field_section(form_frame)

        # Buttons
        self.create_buttons(form_frame)

    def create_field_section(self, parent):
        """Create form field section."""
        # Field container
        field_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        field_container.pack(fill="both", expand=True)

        # Amendment Type (required)
        type_row = ctk.CTkFrame(field_container, fg_color="transparent")
        type_row.pack(fill="x", pady=5)
        self.create_required_field_label(type_row, "Amendment Type")
        self.type_dropdown = ctk.CTkOptionMenu(
            type_row,
            values=list(CONTRACT_AMENDMENT_TYPES.keys()),
            variable=self.amendment_type_var,
            command=self.on_amendment_type_changed,
            width=300
        )
        self.type_dropdown.pack(side="right", padx=10)

        # Amendment Date (required)
        date_row = ctk.CTkFrame(field_container, fg_color="transparent")
        date_row.pack(fill="x", pady=5)
        self.create_required_field_label(date_row, "Amendment Date")
        self.date_entry = ctk.CTkEntry(
            date_row, placeholder_text=DATE_PLACEHOLDER, textvariable=self.amendment_date_var, width=300
        )
        self.date_entry.pack(side="right", padx=10)

        # Field Name (required)
        field_row = ctk.CTkFrame(field_container, fg_color="transparent")
        field_row.pack(fill="x", pady=5)
        self.create_required_field_label(field_row, "Field Being Changed")
        self.field_dropdown = ctk.CTkOptionMenu(
            field_row,
            values=list(self.FIELD_OPTIONS.keys()),
            variable=self.old_field_name_var,
            command=self.on_field_changed,
            width=300
        )
        self.field_dropdown.pack(side="right", padx=10)

        # Display mapped names
        field_display_row = ctk.CTkFrame(field_container, fg_color="transparent")
        field_display_row.pack(fill="x", pady=0)
        self.field_display_label = ctk.CTkLabel(
            field_display_row,
            text="",
            font=("Arial", 10),
            text_color="gray"
        )
        self.field_display_label.pack(side="right", padx=10)

        # Old Value
        old_row = ctk.CTkFrame(field_container, fg_color="transparent")
        old_row.pack(fill="x", pady=5)
        self.create_required_field_label(old_row, "Old Value")
        self.old_value_entry = ctk.CTkEntry(
            old_row, placeholder_text="Previous value", textvariable=self.old_value_var, width=300
        )
        self.old_value_entry.pack(side="right", padx=10)

        # Auto-fill old value button
        auto_btn = ctk.CTkButton(old_row, text="Auto", width=60, command=self.auto_fill_old_value)
        auto_btn.pack(side="right", padx=5)

        # New Value
        new_row = ctk.CTkFrame(field_container, fg_color="transparent")
        new_row.pack(fill="x", pady=5)
        self.create_required_field_label(new_row, "New Value")
        self.new_value_entry = ctk.CTkEntry(
            new_row, placeholder_text="New value", textvariable=self.new_value_var, width=300
        )
        self.new_value_entry.pack(side="right", padx=10)

        # Description (required)
        desc_row = ctk.CTkFrame(field_container, fg_color="transparent")
        desc_row.pack(fill="x", pady=5)
        self.create_required_field_label(desc_row, "Description")
        self.desc_entry = ctk.CTkEntry(
            desc_row, placeholder_text="Reason for change", textvariable=self.description_var, width=300
        )
        self.desc_entry.pack(side="right", padx=10)

        # Document Path (optional)
        doc_row = ctk.CTkFrame(field_container, fg_color="transparent")
        doc_row.pack(fill="x", pady=5)
        self.create_optional_field_label(doc_row, "Supporting Document")
        doc_frame = ctk.CTkFrame(doc_row, fg_color="transparent")
        doc_frame.pack(side="right", padx=10)

        self.doc_entry = ctk.CTkEntry(
            doc_frame,
            placeholder_text="Optional - Path to document PDF",
            textvariable=self.document_path_var,
            width=200,
        )
        self.doc_entry.pack(side="left")

        browse_btn = ctk.CTkButton(doc_frame, text="Browse...", width=80, command=self.browse_document)
        browse_btn.pack(side="left", padx=5)

    def create_required_field_label(self, parent, text: str):
        """Create a required field label with asterisk."""
        label = ctk.CTkLabel(parent, text=f"{text}: *", font=("Arial", 11), width=180, anchor="w")
        label.pack(side="left", padx=10)

    def create_optional_field_label(self, parent, text: str):
        """Create an optional field label."""
        label = ctk.CTkLabel(parent, text=f"{text}:", font=("Arial", 11), width=180, anchor="w")
        label.pack(side="left", padx=10)

    def create_buttons(self, parent):
        """Create form action buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(button_frame, text=BTN_CANCEL, width=120, command=self.on_cancel)
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(button_frame, text=BTN_SAVE, width=120, command=self.on_save)
        save_btn.pack(side="right", padx=5)

    def on_amendment_type_changed(self, *args):
        """Handle amendment type change."""
        amendment_type = self.amendment_type_var.get()

        # Pre-fill description based on type
        type_descriptions = {
            "salary_change": "Salary adjustment",
            "position_change": "Position change",
            "department_change": "Department transfer",
            "hours_change": "Working hours adjustment",
            "extension": "Contract extension",
            "other": "Other amendment",
        }

        if amendment_type and not self.is_edit_mode:
            # Only pre-fill if not already filled
            if not self.description_var.get():
                self.description_var.set(type_descriptions.get(amendment_type, ""))

    def on_field_changed(self, *args):
        """Handle field selection change."""
        field_name = self.old_field_name_var.get()
        display_name = self.FIELD_OPTIONS.get(field_name, field_name)
        self.field_display_label.configure(text=f"({display_name})")

    def auto_fill_old_value(self):
        """Auto-fill old value from current contract."""
        field_name = self.old_field_name_var.get()

        if not field_name:
            return

        # Get current value from contract
        if hasattr(self.contract, field_name):
            value = getattr(self.contract, field_name)

            if value is None:
                self.old_value_var.set("")
            elif isinstance(value, date):
                self.old_value_var.set(value.strftime(DATE_FORMAT))
            elif isinstance(value, datetime):
                self.old_value_var.set(value.strftime(DATE_FORMAT))
            else:
                self.old_value_var.set(str(value))

    def browse_document(self):
        """Open file browser to select supporting document."""
        try:
            from tkinter import filedialog
            import tkinter.messagebox as messagebox

            file_path = filedialog.askopenfilename(
                title="Select Supporting Document PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

            if not file_path:
                return  # User cancelled

            # Validate and copy to secure storage
            from utils.file_validation import validate_and_copy_document

            success, error, secure_path = validate_and_copy_document(
                file_path,
                allowed_extensions={".pdf"},
                max_size_mb=10
            )

            if not success:
                messagebox.showerror("File Validation Error", error)
                print(f"[SECURITY] File upload rejected: {error}")
                return

            # Store secure path in form
            self.document_path_var.set(secure_path)
            print(f"[OK] File validated and copied to secure storage: {secure_path}")

        except Exception as e:
            print(f"[ERROR] Failed to browse file: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Failed to select file: {e}")

    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date from French format."""
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            return None

    def load_amendment_data(self):
        """Load existing amendment data for editing."""
        if self.amendment:
            self.amendment_type_var.set(self.amendment.amendment_type)
            self.amendment_date_var.set(self.amendment.amendment_date.strftime(DATE_FORMAT))
            self.description_var.set(self.amendment.description)
            self.old_field_name_var.set(self.amendment.old_field_name)
            self.old_value_var.set(self.amendment.old_value or "")
            self.new_value_var.set(self.amendment.new_value or "")

            if self.amendment.document_path:
                self.document_path_var.set(self.amendment.document_path)

            # Update field display
            self.on_field_changed()

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate form data."""
        amendment_type = self.amendment_type_var.get().strip()
        date_str = self.amendment_date_var.get().strip()
        field_name = self.old_field_name_var.get().strip()
        old_value = self.old_value_var.get().strip()
        new_value = self.new_value_var.get().strip()
        description = self.description_var.get().strip()

        # Validate amendment type
        if not amendment_type:
            return False, "Amendment type is required"

        if amendment_type not in CONTRACT_AMENDMENT_TYPES:
            return False, f"Invalid amendment type: {amendment_type}"

        # Validate date
        if not date_str:
            return False, f"Amendment date: {VALIDATION_DATE_REQUIRED}"

        amendment_date = self.parse_date(date_str)
        if not amendment_date:
            return False, "Amendment date is invalid"

        # Validate field name
        if not field_name:
            return False, "Field name is required"

        if field_name not in self.FIELD_OPTIONS:
            return False, f"Invalid field name: {field_name}"

        # Validate values
        if not old_value:
            return False, "Old value is required"

        if not new_value:
            return False, "New value is required"

        # Validate description
        if not description:
            return False, "Description is required"

        if len(description) < 10:
            return False, "Description must be at least 10 characters"

        return True, None

    def save(self):
        """Save form data to database."""
        amendment_type = self.amendment_type_var.get().strip()
        date_str = self.amendment_date_var.get().strip()
        field_name = self.old_field_name_var.get().strip()
        old_value = self.old_value_var.get().strip()
        new_value = self.new_value_var.get().strip()
        description = self.description_var.get().strip()
        document_path = self.document_path_var.get().strip() or None

        try:
            # Parse date
            amendment_date = self.parse_date(date_str)

            if self.is_edit_mode:
                # Update existing amendment
                self.amendment.amendment_type = amendment_type
                self.amendment.amendment_date = amendment_date
                self.amendment.description = description
                self.amendment.old_field_name = field_name
                self.amendment.old_value = old_value if old_value else None
                self.amendment.new_value = new_value if new_value else None
                self.amendment.document_path = document_path
                self.amendment.save()
                print(f"[OK] Contract amendment updated: {amendment_type}")
            else:
                # Create new amendment
                self.amendment = ContractAmendment.create(
                    contract=self.contract,
                    amendment_type=amendment_type,
                    amendment_date=amendment_date,
                    description=description,
                    old_field_name=field_name,
                    old_value=old_value if old_value else None,
                    new_value=new_value if new_value else None,
                    document_path=document_path,
                )
                print(f"[OK] Contract amendment created: {amendment_type}")

        except Exception as e:
            error_msg = f"Error saving amendment: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.show_error(error_msg)
            raise
