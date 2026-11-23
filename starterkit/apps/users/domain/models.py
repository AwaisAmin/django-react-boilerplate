from django.conf import settings
from django.db import models

from apps.users.domain.roles import DEFAULT_ROLE, Role


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=DEFAULT_ROLE)

    class Meta:
        constraints = [
            # `choices` is only checked by forms and full_clean(); enforce it in the database too.
            models.CheckConstraint(
                condition=models.Q(role__in=Role.values), name="users_profile_role_valid"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} ({self.get_role_display()})"
