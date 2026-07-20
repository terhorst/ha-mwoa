"""Data coordinator for YNAB Amazon Spend."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import YnabApiClient, YnabApiError
from .calculation import calculate_spend
from .const import DOMAIN, WINDOWS

_LOGGER = logging.getLogger(__name__)


class YnabAmazonSpendCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch YNAB transactions and calculate all rolling totals."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: YnabApiClient,
        match_terms: list[str],
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client
        self.match_terms = match_terms

    async def _async_update_data(self) -> dict[str, Any]:
        today = dt_util.now().date()
        since = today - timedelta(days=max(WINDOWS.values()) - 1)
        try:
            plan = await self.client.get_plan()
            transactions = await self.client.get_transactions(since.isoformat())
        except YnabApiError as err:
            raise UpdateFailed(str(err)) from err

        currency = plan.get("currency_format", {}).get("iso_code", "USD")
        results: dict[str, Any] = {"currency": currency, "plan_name": plan["name"]}
        for window, days in WINDOWS.items():
            amount, count = calculate_spend(transactions, self.match_terms, today, days)
            results[window] = {"amount": amount, "count": count}
        return results
