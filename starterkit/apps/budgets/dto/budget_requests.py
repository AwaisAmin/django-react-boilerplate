from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class BudgetRequestInputDTO:
    """
    A client's request form, as parsed from the HTTP request.

    Values are raw strings; services validate and convert them (e.g. amount to Decimal).
    """

    title: str
    amount: str
    justification: str


@dataclass(frozen=True)
class ReviewInputDTO:
    """A manager's decision: "APPROVED" or "REJECTED", with an optional note."""

    decision: str
    note: str


@dataclass(frozen=True)
class BudgetRequestResultDTO:
    """
    Result of a mutation.

    On failure `errors` maps field names (or "non_field_errors") to messages, and
    `page_props` holds the props to re-render the form page with, when there is one.
    """

    success: bool
    request_id: int | None
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None = None
