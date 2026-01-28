"""UI views for the application."""

from .alerts_view import AlertsView
from .base_view import BaseView
from .contract_history_view import ContractHistoryView
from .employee_detail import EmployeeDetailView
from .employee_list import EmployeeListView
from .import_view import ImportView
from .placeholder import PlaceholderView

__all__ = [
    "BaseView",
    "EmployeeListView",
    "EmployeeDetailView",
    "ContractHistoryView",
    "AlertsView",
    "ImportView",
    "PlaceholderView",
]
