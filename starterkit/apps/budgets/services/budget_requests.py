"""
Budget request workflow: every state change goes through here.

Each mutation resolves the actor's role, checks a policy and then changes state.
Changes to an existing request run in a transaction with the row locked, so two
people acting at once (e.g. two managers reviewing the same request) cannot both
succeed: the second one sees the new status and gets a clear error.

Failures are reported in two ways:
- PermissionDenied (403) / Http404: the actor may not do this at all.
- A result with errors: the action is allowed in principle but the input is
  invalid or the request has moved on (e.g. it was already reviewed).
"""

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.http import Http404
from django.utils import timezone

from apps.budgets.domain import policies
from apps.budgets.domain.models import BudgetRequest, Status
from apps.budgets.dto.budget_requests import (
    BudgetRequestInputDTO,
    BudgetRequestResultDTO,
    ReviewInputDTO,
)
from apps.budgets.selectors import budget_requests as selectors
from apps.budgets.services.validation import clean_request_input, clean_review_input
from apps.users.selectors.roles import role_for_user
from shared.services import ensure_allowed

ALREADY_REVIEWED_ERROR = "This request has already been reviewed and can no longer be changed."
NOT_PENDING_ERROR = "This request is no longer pending."


def create_request(*, actor: AbstractBaseUser, data: BudgetRequestInputDTO) -> BudgetRequestResultDTO:
    ensure_allowed(policies.can_create(role_for_user(actor)))

    clean, errors = clean_request_input(data)
    if errors:
        return _failure(errors)

    request = BudgetRequest.objects.create(
        requester=actor, title=clean.title, amount=clean.amount, justification=clean.justification
    )
    return _success(request, f'Request "{request.title}" was submitted.')


def update_request(
    *, actor: AbstractBaseUser, request_id: int, data: BudgetRequestInputDTO
) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    clean, errors = clean_request_input(data)

    with transaction.atomic():
        request = _get_visible_for_update(actor, role, request_id)
        _ensure_owner_may_change(actor, role, request)
        if not request.is_pending:
            return _failure({"non_field_errors": [ALREADY_REVIEWED_ERROR]}, request_id)
        if errors:
            return _failure(errors, request_id)

        request.title = clean.title
        request.amount = clean.amount
        request.justification = clean.justification
        request.save(update_fields=["title", "amount", "justification", "updated_at"])
    return _success(request, f'Request "{request.title}" was updated.')


def withdraw_request(*, actor: AbstractBaseUser, request_id: int) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    with transaction.atomic():
        request = _get_visible_for_update(actor, role, request_id)
        _ensure_owner_may_change(actor, role, request)
        if not request.is_pending:
            return _failure({"non_field_errors": [ALREADY_REVIEWED_ERROR]}, request_id)

        request.status = Status.WITHDRAWN
        request.save(update_fields=["status", "updated_at"])
    return _success(request, f'Request "{request.title}" was withdrawn.')


def review_request(
    *, actor: AbstractBaseUser, request_id: int, data: ReviewInputDTO
) -> BudgetRequestResultDTO:
    role = role_for_user(actor)
    # Checked before loading the request, so non-managers learn nothing about it.
    ensure_allowed(policies.can_view_review_queue(role))
    clean, errors = clean_review_input(data)

    with transaction.atomic():
        request = _get_for_update_or_404(request_id)
        if not policies.can_review(role, request):
            # The actor is a manager, so the only reason is that it was already decided.
            return _failure({"non_field_errors": [NOT_PENDING_ERROR]}, request_id)
        if errors:
            return _failure(errors, request_id)

        request.status = clean.status
        request.review_note = clean.note
        request.reviewer = actor
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "review_note", "reviewer", "reviewed_at", "updated_at"])
    return _success(request, f'Request "{request.title}" was {request.get_status_display().lower()}.')


def delete_request(*, actor: AbstractBaseUser, request_id: int) -> BudgetRequestResultDTO:
    ensure_allowed(policies.can_delete(role_for_user(actor)))
    with transaction.atomic():
        request = _get_for_update_or_404(request_id)
        title = request.title
        request.delete()
    return _success(None, f'Request "{title}" was permanently deleted.')


# Helpers


def _get_for_update_or_404(request_id: int) -> BudgetRequest:
    request = selectors.budget_request_get_for_update(request_id)
    if request is None:
        raise Http404("Budget request not found.")
    return request


def _get_visible_for_update(actor, role, request_id: int) -> BudgetRequest:
    """
    Requests the actor may not see are reported as missing (404), so a client
    cannot discover which request ids belong to other people.
    """
    request = _get_for_update_or_404(request_id)
    if not policies.can_view(actor, role, request):
        raise Http404("Budget request not found.")
    return request


def _ensure_owner_may_change(actor, role, request: BudgetRequest) -> None:
    """
    Only the owning client may change a request. Whether it is still pending is
    checked separately, so the owner gets a helpful message instead of a 403.
    """
    is_owning_client = policies.can_view_own_requests(role) and request.requester_id == actor.pk
    ensure_allowed(is_owning_client)


def _success(request: BudgetRequest | None, message: str) -> BudgetRequestResultDTO:
    return BudgetRequestResultDTO(
        success=True, request_id=request.pk if request else None, message=message, errors={}
    )


def _failure(errors: dict, request_id: int | None = None) -> BudgetRequestResultDTO:
    return BudgetRequestResultDTO(success=False, request_id=request_id, message="", errors=errors)
