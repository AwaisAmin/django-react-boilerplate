from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.http import Http404

from apps.users.domain import policies
from apps.users.domain.models import UserProfile
from apps.users.domain.roles import Role
from apps.users.dto.roles import AssignRoleInputDTO, AssignRoleResultDTO
from apps.users.selectors import roles as role_selectors

INVALID_ROLE_ERROR = "Select a valid role."
FIXED_ROLE_ERROR = "Superusers are always admins; their role cannot be changed."


def assign_role(*, actor: AbstractBaseUser, data: AssignRoleInputDTO) -> AssignRoleResultDTO:
    if not policies.can_assign_roles(actor):
        raise PermissionDenied
    user = role_selectors.user_get(data.user_id)
    if user is None:
        raise Http404("User not found.")

    if policies.has_fixed_role(user):
        return _failure(FIXED_ROLE_ERROR)
    if data.role not in Role.values:
        return _failure(INVALID_ROLE_ERROR)

    UserProfile.objects.update_or_create(user=user, defaults={"role": data.role})
    return AssignRoleResultDTO(
        success=True,
        message=f'"{user.get_username()}" now has the {Role(data.role).label} role.',
        errors={},
    )


def _failure(error: str) -> AssignRoleResultDTO:
    return AssignRoleResultDTO(success=False, message="", errors={"role": [error]})
