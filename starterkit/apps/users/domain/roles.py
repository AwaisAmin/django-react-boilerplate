from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import models

UserLike = AbstractBaseUser | AnonymousUser


class Role(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    MANAGER = "MANAGER", "Manager"
    ADMIN = "ADMIN", "Admin"


# Least privilege: accounts without a profile are treated as clients.
DEFAULT_ROLE = Role.CLIENT


def effective_role(user: UserLike, stored_role: str | None) -> Role | None:
    """
    The role a user acts with, given the role stored on their profile.

    Anonymous and inactive users have no role. Superusers are always admins, so
    an account made with `createsuperuser` works without further setup.
    """

    if not user.is_authenticated or not user.is_active:
        return None
    if user.is_superuser:
        return Role.ADMIN
    return DEFAULT_ROLE if stored_role is None else Role(stored_role)
