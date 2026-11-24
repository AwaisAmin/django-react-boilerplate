from collections.abc import Iterable

from django.contrib.auth import get_user_model

from apps.users.domain.models import UserProfile
from apps.users.domain.roles import Role, UserLike, effective_role

User = get_user_model()

# `role_for_user`, `roles_for_users` and `Role` are the entry points for other apps.
__all__ = ["Role", "role_for_user", "roles_for_users", "stored_role", "user_get"]


def user_get(user_id: int) -> User | None:
    return User.objects.filter(pk=user_id).first()


def stored_role(user: UserLike) -> str | None:
    if user.pk is None:  # Anonymous: skip the query.
        return None
    return UserProfile.objects.filter(user_id=user.pk).values_list("role", flat=True).first()


def role_for_user(user: UserLike) -> Role | None:
    return effective_role(user, stored_role(user))


def roles_for_users(users: Iterable[UserLike]) -> dict[int, Role | None]:
    """Current roles keyed by user id, with a single query."""
    users = list(users)
    stored = dict(
        UserProfile.objects.filter(user_id__in=[user.pk for user in users]).values_list("user_id", "role")
    )
    return {user.pk: effective_role(user, stored.get(user.pk)) for user in users}
