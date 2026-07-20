"""Pure transaction calculation helpers."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any


def matches_transaction(transaction: dict[str, Any], match_terms: list[str]) -> bool:
    """Return whether a transaction represents a matching merchant purchase."""
    if transaction.get("deleted") or transaction.get("transfer_account_id"):
        return False

    searchable = " ".join(
        str(transaction.get(field) or "")
        for field in ("payee_name", "memo")
    ).casefold()
    return any(term.casefold() in searchable for term in match_terms)


def calculate_spend(
    transactions: list[dict[str, Any]],
    match_terms: list[str],
    today: date,
    days: int,
) -> tuple[Decimal, int]:
    """Calculate net spend and matching transaction count for a rolling window."""
    first_date = today - timedelta(days=days - 1)
    amount_milliunits = 0
    count = 0

    for transaction in transactions:
        if not matches_transaction(transaction, match_terms):
            continue
        transaction_date = date.fromisoformat(transaction["date"])
        if first_date <= transaction_date <= today:
            # YNAB outflows are negative; refunds therefore reduce net spend.
            amount_milliunits -= int(transaction.get("amount", 0))
            count += 1

    return Decimal(amount_milliunits) / Decimal(1000), count
