"""Contract history view for managing employee contracts."""

from datetime import date
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from employee.models import Contract, Employee
from reports.contract_evolution import generate_contract_evolution_report
from ui_ctk.constants import (
    BTN_ADD,
    BTN_BACK,
    BTN_DELETE,
    BTN_EDIT,
    COLOR_CRITICAL,
    COLOR_INACTIVE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    CONFIRM_DELETE_WARNING,
    DATE_FORMAT,
    EXPIRATION_STATUS_EXPIRED,
    EXPIRATION_STATUS_SOON,
    EXPIRATION_STATUS_URGENT,
    EXPIRATION_STATUS_VALID,
)
from ui_ctk.views.base_view import BaseView


class ContractHistoryView(BaseView):
    """
    Dedicated view for managing employee contract history.

    Features:
    - Display complete contract timeline
    - Add/edit/delete contracts
    - Show evolution statistics
    - Visual status indicators
    - Document links
    """

    def __init__(self, master, employee: Employee):
        """
        Initialize contract history view.

        Args:
            master: Parent window
            employee: Employee object to display contracts for
        """
        # Don't call parent with title to avoid creating default header
        super().__init__(master, title="")

        self.employee = employee

        # Create UI (header with buttons + content)
        self.create_header()
        self.create_content()

    def create_header(self):
        """Create view header with back button."""
        # Header frame
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)

        # Back button
        back_btn = ctk.CTkButton(header_frame, text=f"← {BTN_BACK}", width=100, command=self.go_back)
        back_btn.pack(side="left", padx=10)

        # Employee name and title
        name_label = ctk.CTkLabel(header_frame, text=self.employee.full_name, font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=20)

        title_label = ctk.CTkLabel(header_frame, text="- Contract History", font=("Arial", 16))
        title_label.pack(side="left", padx=5)

        # Evolution statistics
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=10)

        # Generate evolution report for stats
        report = generate_contract_evolution_report(self.employee)

        tenure_text = f"{report.total_experience_years:.1f} years"
        tenure_label = ctk.CTkLabel(stats_frame, text=f"Tenure: {tenure_text}", font=("Arial", 11))
        tenure_label.pack(side="left", padx=10)

        contracts_text = f"{report.total_contracts} contract(s)"
        contracts_label = ctk.CTkLabel(stats_frame, text=contracts_text, font=("Arial", 11))
        contracts_label.pack(side="left", padx=10)

    def create_content(self):
        """Create content sections."""
        # Scrollable content
        content = ctk.CTkScrollableFrame(self)
        content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Contract list section
        self.create_contracts_section(content)

        # Amendments section
        self.create_amendments_section(content)

        # Evolution summary section
        self.create_evolution_section(content)

    def create_contracts_section(self, parent):
        """Create contracts list section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with add button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text="📄 Contracts", font=("Arial", 14, "bold"))
        header.pack(side="left")

        add_btn = ctk.CTkButton(header_frame, text=f"+ {BTN_ADD}", width=100, command=self.add_contract)
        add_btn.pack(side="right")

        # Load contracts
        contracts = list(
            Contract.select()
            .where(Contract.employee == self.employee)
            .order_by(Contract.start_date.desc())
        )

        if contracts:
            # Display contracts
            for contract in contracts:
                self.create_contract_item(section, contract)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(section, text="No contracts found", text_color="gray")
            empty_label.pack(padx=10, pady=(0, 10))

    def create_contract_item(self, parent, contract: Contract):
        """Create a single contract item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Left side: Contract info
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Row 1: Type and status
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x")

        type_label = ctk.CTkLabel(row1, text=f"{contract.contract_type}", font=("Arial", 12, "bold"), anchor="w")
        type_label.pack(side="left")

        # Status badge
        if contract.is_current:
            status_text = "Current"
            status_color = COLOR_SUCCESS
            status_label = ctk.CTkLabel(row1, text=status_text, font=("Arial", 10, "bold"), text_color=status_color)
            status_label.pack(side="left", padx=10)
        elif contract.end_date:
            days_until = (contract.end_date - date.today()).days
            if days_until < 0:
                status_text = EXPIRATION_STATUS_EXPIRED
                status_color = COLOR_CRITICAL
            elif days_until < 30:
                status_text = f"{EXPIRATION_STATUS_URGENT} ({days_until}d)"
                status_color = COLOR_CRITICAL
            elif days_until < 90:
                status_text = f"{EXPIRATION_STATUS_SOON} ({days_until}d)"
                status_color = COLOR_WARNING
            else:
                status_text = EXPIRATION_STATUS_VALID
                status_color = COLOR_SUCCESS

            status_label = ctk.CTkLabel(row1, text=status_text, font=("Arial", 10, "bold"), text_color=status_color)
            status_label.pack(side="left", padx=10)
        else:
            status_text = contract.status.title()
            status_color = COLOR_INACTIVE
            status_label = ctk.CTkLabel(row1, text=status_text, font=("Arial", 10), text_color=status_color)
            status_label.pack(side="left", padx=10)

        # Row 2: Position and department
        row2 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row2.pack(fill="x")

        pos_dept_text = f"{contract.position} in {contract.department}"
        pos_dept_label = ctk.CTkLabel(row2, text=pos_dept_text, font=("Arial", 11), anchor="w")
        pos_dept_label.pack(side="left")

        # Row 3: Dates
        row3 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row3.pack(fill="x")

        start_text = f"From {contract.start_date.strftime(DATE_FORMAT)}"
        start_label = ctk.CTkLabel(row3, text=start_text, font=("Arial", 10), anchor="w")
        start_label.pack(side="left")

        if contract.end_date:
            end_text = f" to {contract.end_date.strftime(DATE_FORMAT)}"
            end_label = ctk.CTkLabel(row3, text=end_text, font=("Arial", 10))
            end_label.pack(side="left", padx=5)

            # Duration
            if contract.duration_days:
                duration_text = f"({contract.duration_days} days)"
                duration_label = ctk.CTkLabel(row3, text=duration_text, font=("Arial", 10), text_color="gray")
                duration_label.pack(side="left", padx=5)

        # Row 4: Salary and trial period (if exists)
        if contract.gross_salary or contract.trial_period_end:
            row4 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row4.pack(fill="x")

            if contract.gross_salary:
                salary_text = f"Salary: €{float(contract.gross_salary):.2f}"
                salary_label = ctk.CTkLabel(row4, text=salary_text, font=("Arial", 10), anchor="w")
                salary_label.pack(side="left")

            if contract.trial_period_end:
                trial_text = f"Trial: {contract.trial_period_end.strftime(DATE_FORMAT)}"
                trial_label = ctk.CTkLabel(row4, text=trial_text, font=("Arial", 10))
                trial_label.pack(side="left", padx=10)

        # Row 5: Document (if exists)
        if contract.contract_document_path:
            row5 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row5.pack(fill="x")

            doc_label = ctk.CTkLabel(row5, text="📎 Document attached", font=("Arial", 9), text_color="gray")
            doc_label.pack(side="left")

        # Right side: Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(action_frame, text=f"✏️ {BTN_EDIT}", width=100, command=lambda c=contract: self.edit_contract(c))
        edit_btn.pack(pady=2)

        delete_btn = ctk.CTkButton(
            action_frame, text=f"🗑️ {BTN_DELETE}", width=100, command=lambda c=contract: self.delete_contract(c), fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(pady=2)

    def create_amendments_section(self, parent):
        """Create contract amendments section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header with info
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text="📝 Contract Amendments", font=("Arial", 14, "bold"))
        header.pack(side="left")

        info_label = ctk.CTkLabel(header_frame, text="Modifications to contracts (salary, position, etc.)", font=("Arial", 10), text_color="gray")
        info_label.pack(side="left", padx=10)

        add_btn = ctk.CTkButton(header_frame, text=f"+ {BTN_ADD}", width=100, command=self.add_amendment)
        add_btn.pack(side="right")

        # Load all amendments for employee's contracts
        from employee.models import ContractAmendment

        amendments = list(
            ContractAmendment.select()
            .join(Contract)
            .where(Contract.employee == self.employee)
            .order_by(ContractAmendment.amendment_date.desc())
        )

        if amendments:
            # Display amendments
            for amendment in amendments:
                self.create_amendment_item(section, amendment)
        else:
            # Empty message
            empty_label = ctk.CTkLabel(section, text="No amendments found", text_color="gray")
            empty_label.pack(padx=10, pady=(0, 10))

    def create_amendment_item(self, parent, amendment):
        """Create a single amendment item."""
        # Item frame
        item = ctk.CTkFrame(parent, fg_color=("gray95", "gray25"))
        item.pack(fill="x", padx=10, pady=5)

        # Left side: Amendment info
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Row 1: Type and date
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x")

        type_label = ctk.CTkLabel(row1, text=f"{amendment.amendment_type}", font=("Arial", 11, "bold"), anchor="w")
        type_label.pack(side="left")

        date_text = f"On {amendment.amendment_date.strftime(DATE_FORMAT)}"
        date_label = ctk.CTkLabel(row1, text=date_text, font=("Arial", 10), text_color="gray")
        date_label.pack(side="left", padx=10)

        # Row 2: Field change
        row2 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row2.pack(fill="x")

        # Map field name to display name
        field_display_names = {
            "gross_salary": "Salary",
            "position": "Position",
            "department": "Department",
            "weekly_hours": "Weekly Hours",
            "trial_period_end": "Trial Period",
        }

        field_name = field_display_names.get(amendment.old_field_name, amendment.old_field_name)
        field_text = f"{field_name}: {amendment.old_value or 'None'} → {amendment.new_value or 'None'}"
        field_label = ctk.CTkLabel(row2, text=field_text, font=("Arial", 10), anchor="w")
        field_label.pack(side="left")

        # Row 3: Description
        if amendment.description:
            row3 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row3.pack(fill="x")

            desc_label = ctk.CTkLabel(row3, text=f"📄 {amendment.description}", font=("Arial", 10), anchor="w")
            desc_label.pack(side="left")

        # Row 4: Document (if exists)
        if amendment.document_path:
            row4 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row4.pack(fill="x")

            doc_label = ctk.CTkLabel(row4, text="📎 Supporting document attached", font=("Arial", 9), text_color="gray")
            doc_label.pack(side="left")

        # Right side: Actions
        action_frame = ctk.CTkFrame(item, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(
            action_frame,
            text=f"✏️ {BTN_EDIT}",
            width=100,
            command=lambda a=amendment: self.edit_amendment(a)
        )
        edit_btn.pack(pady=2)

        delete_btn = ctk.CTkButton(
            action_frame,
            text=f"🗑️ {BTN_DELETE}",
            width=100,
            command=lambda a=amendment: self.delete_amendment(a),
            fg_color=COLOR_CRITICAL
        )
        delete_btn.pack(pady=2)

    def create_evolution_section(self, parent):
        """Create contract evolution summary section."""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=5)

        # Section header
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(header_frame, text="📊 Career Evolution", font=("Arial", 14, "bold"))
        header.pack(side="left")

        # Generate evolution report
        report = generate_contract_evolution_report(self.employee)

        # Evolution grid
        grid_frame = ctk.CTkFrame(section, fg_color=("gray90", "gray20"))
        grid_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Statistics rows
        self.create_stat_row(grid_frame, "Total Contracts:", str(report.total_contracts))
        self.create_stat_row(grid_frame, "Total Tenure:", f"{report.total_tenure_days} days ({report.total_experience_years:.1f} years)")
        self.create_stat_row(grid_frame, "Position Changes:", str(report.position_count))
        self.create_stat_row(grid_frame, "Department Changes:", str(report.department_count))

        if report.starting_salary and report.current_salary:
            self.create_stat_row(grid_frame, "Salary Progression:", f"€{report.starting_salary:.2f} → €{report.current_salary:.2f}")
            if report.total_salary_increase > 0:
                increase_text = f"+€{report.total_salary_increase:.2f}"
                self.create_stat_row(grid_frame, "Total Increase:", increase_text)

        if report.has_gaps:
            self.create_stat_row(grid_frame, "Employment Gaps:", f"{len(report.employment_gaps)} gap(s) - {report.total_gap_days} days")

        # Position history
        if report.position_changes:
            pos_section = ctk.CTkFrame(section, fg_color="transparent")
            pos_section.pack(fill="x", padx=10, pady=(10, 5))

            pos_header = ctk.CTkLabel(pos_section, text="Position History:", font=("Arial", 12, "bold"))
            pos_header.pack(anchor="w")

            for change in report.position_changes:
                change_row = ctk.CTkFrame(pos_section, fg_color="transparent")
                change_row.pack(fill="x", padx=10, pady=2)

                change_text = f"{change.from_position} → {change.to_position} ({change.change_date.strftime(DATE_FORMAT)})"
                change_label = ctk.CTkLabel(change_row, text=change_text, font=("Arial", 10))
                change_label.pack(anchor="w")

    def create_stat_row(self, parent, label: str, value: str):
        """Create a statistics row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=2)

        label_widget = ctk.CTkLabel(row, text=label, font=("Arial", 11), anchor="w", width=180)
        label_widget.pack(side="left", padx=10)

        value_widget = ctk.CTkLabel(row, text=value, font=("Arial", 11, "bold"), anchor="w")
        value_widget.pack(side="left", padx=10)

    def add_contract(self):
        """Add new contract."""
        try:
            from ui_ctk.forms.contract_form import ContractFormDialog

            dialog = ContractFormDialog(self, employee=self.employee)
            self.wait_window(dialog)

            if dialog.result:
                # Reload view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to add contract: {e}")
            self.show_error(f"Failed to add contract: {e}")

    def edit_contract(self, contract: Contract):
        """Edit existing contract."""
        try:
            from ui_ctk.forms.contract_form import ContractFormDialog

            dialog = ContractFormDialog(self, employee=self.employee, contract=contract)
            self.wait_window(dialog)

            if dialog.result:
                # Reload view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to edit contract: {e}")
            self.show_error(f"Failed to edit contract: {e}")

    def delete_contract(self, contract: Contract):
        """Delete contract."""
        try:
            import tkinter.messagebox as messagebox

            # Get contract details
            contract_details = f"{contract.contract_type} - {contract.position}\n"
            contract_details += f"From {contract.start_date.strftime(DATE_FORMAT)}"
            if contract.end_date:
                contract_details += f" to {contract.end_date.strftime(DATE_FORMAT)}"

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Delete Contract",
                f"Delete this contract?\n\n"
                f"{contract_details}\n\n"
                f"Employee: {self.employee.full_name}\n\n"
                f"Warning: This will permanently delete the contract history.",
                icon="warning"
            )

            if confirm:
                # Delete contract (CASCADE will delete amendments)
                contract.delete_instance()

                print(f"[OK] Contract deleted: {contract.contract_type}")

                # Refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to delete contract: {e}")
            self.show_error(f"Failed to delete contract: {e}")

    def add_amendment(self):
        """Add new contract amendment."""
        try:
            from ui_ctk.forms.contract_amendment_form import ContractAmendmentFormDialog

            # Need to select a contract first if there are multiple
            contracts = list(
                Contract.select()
                .where(Contract.employee == self.employee)
                .order_by(Contract.start_date.desc())
            )

            if not contracts:
                self.show_error("Cannot add amendment: No contracts found")
                return

            # For now, use the most recent contract
            # In future, could show dialog to select contract
            contract = contracts[0]

            dialog = ContractAmendmentFormDialog(self, contract=contract)
            self.wait_window(dialog)

            if dialog.result:
                # Reload view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to add amendment: {e}")
            self.show_error(f"Failed to add amendment: {e}")

    def edit_amendment(self, amendment):
        """Edit existing contract amendment."""
        try:
            from ui_ctk.forms.contract_amendment_form import ContractAmendmentFormDialog

            dialog = ContractAmendmentFormDialog(self, contract=amendment.contract, amendment=amendment)
            self.wait_window(dialog)

            if dialog.result:
                # Reload view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to edit amendment: {e}")
            self.show_error(f"Failed to edit amendment: {e}")

    def delete_amendment(self, amendment):
        """Delete contract amendment."""
        try:
            import tkinter.messagebox as messagebox

            # Get amendment details
            amendment_details = f"{amendment.amendment_type}\n"
            amendment_details += f"Field: {amendment.old_field_name}\n"
            amendment_details += f"Date: {amendment.amendment_date.strftime(DATE_FORMAT)}"

            # Confirm deletion
            confirm = messagebox.askyesno(
                "Delete Amendment",
                f"Delete this contract amendment?\n\n"
                f"{amendment_details}\n\n"
                f"This action cannot be undone.",
                icon="warning"
            )

            if confirm:
                # Delete amendment
                amendment.delete_instance()

                print(f"[OK] Contract amendment deleted: {amendment.amendment_type}")

                # Refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to delete amendment: {e}")
            self.show_error(f"Failed to delete amendment: {e}")

    def refresh_view(self):
        """Reload employee data and recreate the view."""
        try:
            # Reload employee data
            self.employee = Employee.get_by_id(self.employee.id)

            # Recreate view
            for widget in self.winfo_children():
                widget.destroy()

            self.create_header()
            self.create_content()

        except Exception as e:
            print(f"[ERROR] Failed to refresh view: {e}")

    def go_back(self):
        """Go back to employee detail view."""
        try:
            from ui_ctk.views.employee_detail import EmployeeDetailView

            if self.master_window:
                self.master_window.switch_view(EmployeeDetailView, employee=self.employee)
            else:
                self.destroy()
        except Exception as e:
            print(f"[ERROR] Failed to go back: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Error", message)
        except (ImportError, RuntimeError, AttributeError):
            print(f"[ERROR] {message}")
