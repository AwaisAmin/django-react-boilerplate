from django.contrib.auth import get_user_model

from apps.users.domain.models import UserProfile
from apps.users.domain.roles import Role, UserLike, effective_role

User = get_user_model()


def user_get(user_id: int) -> User | None:
    return User.objects.filter(pk=user_id).first()


def stored_role(user: UserLike) -> str | None:
    return UserProfile.objects.filter(user_id=user.pk).values_list("role", flat=True).first()


def role_for_user(user: UserLike) -> Role | None:
    """The user's current role. This is the entry point for other apps."""
    return effective_role(user, stored_role(user))
