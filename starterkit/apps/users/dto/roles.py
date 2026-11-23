from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class AssignRoleInputDTO:
    user_id: int
    role: str


@dataclass(frozen=True)
class AssignRoleResultDTO:
    success: bool
    message: str
    errors: Mapping[str, Sequence[str]]
