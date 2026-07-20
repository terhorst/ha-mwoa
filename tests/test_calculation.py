"""Tests for transaction calculations."""

from datetime import date
from decimal import Decimal

from custom_components.ynab_amazon_spend.calculation import calculate_spend


def test_calculates_net_spend_and_matching_count() -> None:
    transactions = [
        {"date": "2026-07-20", "payee_name": "Amazon", "amount": -25990},
        {"date": "2026-07-19", "payee_name": "AMZN Mktp", "amount": -10000},
        {"date": "2026-07-18", "memo": "Amazon refund", "amount": 5000},
        {"date": "2026-07-20", "payee_name": "Grocery", "amount": -9000},
    ]

    amount, count = calculate_spend(
        transactions, ["amazon", "amzn"], date(2026, 7, 20), 7
    )

    assert amount == Decimal("30.99")
    assert count == 3


def test_window_and_exclusions() -> None:
    transactions = [
        {"date": "2026-07-13", "payee_name": "Amazon", "amount": -1000},
        {
            "date": "2026-07-20",
            "payee_name": "Amazon",
            "amount": -2000,
            "deleted": True,
        },
        {
            "date": "2026-07-20",
            "payee_name": "Amazon",
            "amount": -3000,
            "transfer_account_id": "account-id",
        },
    ]

    amount, count = calculate_spend(
        transactions, ["amazon"], date(2026, 7, 20), 7
    )

    assert amount == Decimal("0")
    assert count == 0
