"""
Who may do what with budget requests.

Policies are pure functions of the actor's role (resolved by the users app)
and, where it matters, the request itself. Services call them and raise
PermissionDenied; React only receives the resulting `can` flags.

    Client   creates requests; sees, edits and withdraws only their own, only while pending
    Manager  sees every request; approves or rejects pending ones
    Admin    sees every request and the totals; the only role that may delete
"""

from django.contrib.auth.models import AbstractBaseUser

from apps.budgets.domain.models import BudgetRequest
from apps.users.selectors.roles import Role

# Listing


def can_create(role: Role | None) -> bool:
    return role == Role.CLIENT


def can_view_own_requests(role: Role | None) -> bool:
    return role == Role.CLIENT


def can_view_review_queue(role: Role | None) -> bool:
    return role == Role.MANAGER


def can_view_all_requests(role: Role | None) -> bool:
    """Organization-wide list with totals (admin overview)."""
    return role == Role.ADMIN


# A single request


def _is_owner(actor: AbstractBaseUser, request: BudgetRequest) -> bool:
    return request.requester_id == actor.pk


def can_view(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    if role in (Role.MANAGER, Role.ADMIN):
        return True
    return role == Role.CLIENT and _is_owner(actor, request)


def can_edit(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    """Clients may change their own request until someone acts on it."""
    return role == Role.CLIENT and _is_owner(actor, request) and request.is_pending


def can_withdraw(actor: AbstractBaseUser, role: Role | None, request: BudgetRequest) -> bool:
    return can_edit(actor, role, request)


def can_review(role: Role | None, request: BudgetRequest) -> bool:
    """Decisions are final: only pending requests can be approved or rejected."""
    return role == Role.MANAGER and request.is_pending


def can_delete(role: Role | None) -> bool:
    return role == Role.ADMIN
