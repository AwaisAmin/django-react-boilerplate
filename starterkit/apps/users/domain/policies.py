"""Permission rules for application roles."""

from apps.users.domain.roles import Role, UserLike


def can_access_workspace(role: Role | None) -> bool:
    """Every active user has a role; anonymous and inactive users have none."""
    return role is not None


def can_assign_roles(actor: UserLike) -> bool:
    """Roles grant privileges, so only superusers may change them."""
    return bool(actor.is_authenticated and actor.is_active and actor.is_superuser)


def has_fixed_role(target: UserLike) -> bool:
    """Superusers are always admins; a stored role would have no effect."""
    return bool(target.is_superuser)
