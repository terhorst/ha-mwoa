"""Small asynchronous client for the YNAB API."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import API_BASE


class YnabApiError(Exception):
    """Base YNAB API error."""


class YnabAuthenticationError(YnabApiError):
    """The YNAB token was rejected."""


class YnabApiClient:
    """Read-only client for the endpoints used by this integration."""

    def __init__(self, session: ClientSession, token: str, plan_id: str) -> None:
        self._session = session
        self._headers = {"Authorization": f"Bearer {token}"}
        self.plan_id = plan_id

    async def _get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            response = await self._session.get(
                f"{API_BASE}{path}", headers=self._headers, params=params
            )
            if response.status in (401, 403):
                raise YnabAuthenticationError("YNAB rejected the personal access token")
            response.raise_for_status()
            payload = await response.json()
        except YnabAuthenticationError:
            raise
        except (ClientError, ClientResponseError, ValueError) as err:
            raise YnabApiError(f"Unable to read data from YNAB: {err}") from err
        return payload["data"]

    async def validate(self) -> str:
        """Validate the token and plan, returning the plan name."""
        data = await self._get(f"/plans/{self.plan_id}")
        return str(data["plan"]["name"])

    async def get_plan(self) -> dict[str, Any]:
        """Return plan metadata."""
        return (await self._get(f"/plans/{self.plan_id}"))["plan"]

    async def get_transactions(self, since_date: str) -> list[dict[str, Any]]:
        """Return transactions since an explicit date."""
        data = await self._get(
            f"/plans/{self.plan_id}/transactions", {"since_date": since_date}
        )
        return data["transactions"]
