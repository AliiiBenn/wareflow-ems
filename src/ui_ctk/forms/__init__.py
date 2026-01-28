"""UI form dialogs for employee data."""

from ui_ctk.forms.base_form import BaseFormDialog
from ui_ctk.forms.caces_form import CacesFormDialog
from ui_ctk.forms.contract_amendment_form import ContractAmendmentFormDialog
from ui_ctk.forms.contract_form import ContractFormDialog
from ui_ctk.forms.employee_form import EmployeeFormDialog
from ui_ctk.forms.medical_form import MedicalVisitFormDialog

__all__ = [
    "BaseFormDialog",
    "CacesFormDialog",
    "ContractAmendmentFormDialog",
    "ContractFormDialog",
    "EmployeeFormDialog",
    "MedicalVisitFormDialog",
]
