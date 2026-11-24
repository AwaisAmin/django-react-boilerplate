# Django discovers models here; they are defined in the domain layer.
from apps.budgets.domain.models import BudgetRequest

__all__ = ["BudgetRequest"]
