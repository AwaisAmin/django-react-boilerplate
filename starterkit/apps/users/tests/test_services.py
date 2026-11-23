from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase

from apps.users.domain.roles import Role
from apps.users.dto.roles import AssignRoleInputDTO
from apps.users.selectors.roles import role_for_user, stored_role
from apps.users.services.roles import FIXED_ROLE_ERROR, INVALID_ROLE_ERROR, assign_role
from apps.users.tests.factories import make_superuser, make_user


class AssignRoleTests(TestCase):
    def setUp(self):
        self.superuser = make_superuser()

    def assign(self, user_id, role, actor=None):
        return assign_role(
            actor=actor or self.superuser, data=AssignRoleInputDTO(user_id=user_id, role=role)
        )

    def test_creates_a_profile_for_a_user_without_one(self):
        user = make_user("new")
        self.assertTrue(self.assign(user.pk, "MANAGER").success)
        self.assertEqual(role_for_user(user), Role.MANAGER)

    def test_replaces_an_existing_role(self):
        user = make_user("user", role=Role.MANAGER)
        result = self.assign(user.pk, "CLIENT")
        self.assertTrue(result.success)
        self.assertEqual(result.message, '"user" now has the Client role.')
        self.assertEqual(role_for_user(user), Role.CLIENT)

    def test_rejects_unknown_roles(self):
        user = make_user("user", role=Role.MANAGER)
        for role in ("OWNER", "manager", ""):
            with self.subTest(role=role):
                result = self.assign(user.pk, role)
                self.assertFalse(result.success)
                self.assertEqual(result.errors, {"role": [INVALID_ROLE_ERROR]})
        self.assertEqual(stored_role(user), Role.MANAGER)

    def test_superuser_role_is_fixed(self):
        other = make_superuser("other")
        result = self.assign(other.pk, "CLIENT")
        self.assertFalse(result.success)
        self.assertEqual(result.errors, {"role": [FIXED_ROLE_ERROR]})
        self.assertIsNone(stored_role(other))

    def test_non_superusers_are_denied(self):
        target = make_user("target", role=Role.CLIENT)
        for role in Role:
            actor = make_user(f"actor-{role.value}", role=role, is_staff=True)
            with self.subTest(role=role), self.assertRaises(PermissionDenied):
                self.assign(target.pk, "ADMIN", actor=actor)
        with self.assertRaises(PermissionDenied):
            self.assign(target.pk, "ADMIN", actor=target)
        self.assertEqual(stored_role(target), Role.CLIENT)

    def test_unknown_user_is_404(self):
        with self.assertRaises(Http404):
            self.assign(999_999, "CLIENT")
