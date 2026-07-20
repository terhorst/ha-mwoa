"""YNAB Amazon Spend integration."""

from __future__ import annotations

from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import YnabApiClient
from .const import (
    CONF_MATCH_TERMS,
    CONF_PLAN_ID,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_MATCH_TERMS,
    DEFAULT_PLAN_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import YnabAmazonSpendCoordinator

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_TOKEN): cv.string,
                vol.Optional(CONF_PLAN_ID, default=DEFAULT_PLAN_ID): cv.string,
                vol.Optional(CONF_MATCH_TERMS, default=DEFAULT_MATCH_TERMS): vol.All(
                    cv.ensure_list, [cv.string]
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Import YAML configuration into a config entry."""
    if yaml_config := config.get(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=dict(yaml_config)
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    data = {**entry.data, **entry.options}
    token = data.get(CONF_TOKEN) or data.get(CONF_ACCESS_TOKEN)
    client = YnabApiClient(
        async_get_clientsession(hass), token, data.get(CONF_PLAN_ID, DEFAULT_PLAN_ID)
    )
    coordinator = YnabAmazonSpendCoordinator(
        hass,
        client,
        list(data.get(CONF_MATCH_TERMS, DEFAULT_MATCH_TERMS)),
        timedelta(seconds=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
