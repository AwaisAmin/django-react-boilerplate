from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AssignRoleInputDTO:
    user_id: int
    role: str


@dataclass(frozen=True)
class AssignRoleResultDTO:
    """
    Result of changing a user's role.

    On failure `page_props` holds the props to re-render the role page with.
    """

    success: bool
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None
