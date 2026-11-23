# Django discovers models here; they are defined in the domain layer.
from apps.users.domain.models import UserProfile

__all__ = ["UserProfile"]
