"""Sensors for YNAB Amazon Spend."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WINDOWS
from .coordinator import YnabAmazonSpendCoordinator


@dataclass(frozen=True, kw_only=True)
class YnabSpendSensorDescription(SensorEntityDescription):
    """Describe a spend sensor."""

    window: str


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up spend sensors."""
    coordinator: YnabAmazonSpendCoordinator = entry.runtime_data
    async_add_entities(
        YnabAmazonSpendSensor(
            coordinator,
            entry,
            YnabSpendSensorDescription(
                key=window,
                window=window,
                name=f"Amazon spend past {window}",
                device_class=SensorDeviceClass.MONETARY,
                state_class=SensorStateClass.TOTAL,
            ),
        )
        for window in WINDOWS
    )


class YnabAmazonSpendSensor(CoordinatorEntity[YnabAmazonSpendCoordinator], SensorEntity):
    """A rolling Amazon spend sensor."""

    entity_description: YnabSpendSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.window}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "YNAB Amazon Spend",
            "manufacturer": "YNAB",
            "configuration_url": "https://app.ynab.com/",
        }

    @property
    def native_value(self) -> Decimal:
        """Return net spend."""
        return self.coordinator.data[self.entity_description.window]["amount"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the plan currency."""
        return self.coordinator.data["currency"]

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return useful calculation details."""
        data = self.coordinator.data[self.entity_description.window]
        return {
            "transaction_count": data["count"],
            "window_days": WINDOWS[self.entity_description.window],
            "match_terms": self.coordinator.match_terms,
            "plan_name": self.coordinator.data["plan_name"],
        }
