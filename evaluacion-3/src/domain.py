from datetime import date
import math
from typing import Any


class DomainError(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_submission(proposal: dict[str, Any]) -> None:
    missing = [
        name
        for name in ("title", "sponsor", "abstract", "requested_amount", "deadline")
        if proposal.get(name) is None
        or (isinstance(proposal.get(name), str) and not proposal[name].strip())
    ]
    if missing:
        raise DomainError(
            "incomplete_proposal",
            f"Missing required fields: {', '.join(missing)}",
            422,
        )

    amount = proposal["requested_amount"]
    if not math.isfinite(amount) or amount <= 0:
        raise DomainError(
            "invalid_requested_amount",
            "requested_amount must be a finite value greater than zero",
            422,
        )

    if date.fromisoformat(proposal["deadline"]) <= date.today():
        raise DomainError(
            "expired_deadline",
            "deadline must be a future date",
            422,
        )
