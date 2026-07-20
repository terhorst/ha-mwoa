"""Config flow for YNAB Amazon Spend."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import YnabApiClient, YnabApiError, YnabAuthenticationError
from .const import (
    CONF_MATCH_TERMS,
    CONF_PLAN_ID,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_MATCH_TERMS,
    DEFAULT_PLAN_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class YnabAmazonSpendConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure YNAB Amazon Spend."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle UI setup."""
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input[CONF_ACCESS_TOKEN]
            plan_id = user_input[CONF_PLAN_ID]
            client = YnabApiClient(async_get_clientsession(self.hass), token, plan_id)
            try:
                plan_name = await client.validate()
            except YnabAuthenticationError:
                errors["base"] = "invalid_auth"
            except YnabApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(plan_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Amazon spend ({plan_name})",
                    data={
                        CONF_TOKEN: token,
                        CONF_PLAN_ID: plan_id,
                        CONF_MATCH_TERMS: [
                            term.strip()
                            for term in user_input[CONF_MATCH_TERMS].split(",")
                            if term.strip()
                        ],
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_TOKEN): str,
                vol.Required(CONF_PLAN_ID, default=DEFAULT_PLAN_ID): str,
                vol.Required(
                    CONF_MATCH_TERMS, default=", ".join(DEFAULT_MATCH_TERMS)
                ): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_data: dict[str, Any]):
        """Import configuration from configuration.yaml."""
        import_data = dict(import_data)
        scan_interval = import_data.get(CONF_SCAN_INTERVAL)
        if hasattr(scan_interval, "total_seconds"):
            import_data[CONF_SCAN_INTERVAL] = int(scan_interval.total_seconds())
        plan_id = import_data.get(CONF_PLAN_ID, DEFAULT_PLAN_ID)
        await self.async_set_unique_id(plan_id)
        self._abort_if_unique_id_configured(updates=import_data)
        client = YnabApiClient(
            async_get_clientsession(self.hass), import_data[CONF_TOKEN], plan_id
        )
        try:
            plan_name = await client.validate()
        except YnabApiError:
            return self.async_abort(reason="cannot_connect")
        return self.async_create_entry(
            title=f"Amazon spend ({plan_name})", data=import_data
        )
