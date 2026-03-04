"""Sensor platform for Elisa Kotiakku integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElisaKotiakkuDataCoordinator


@dataclass(frozen=True, kw_only=True)
class ElisaKotiakkuSensorEntityDescription(SensorEntityDescription):
    """Describes Elisa Kotiakku sensor entity."""

    emoji: str


SENSOR_DESCRIPTIONS: tuple[ElisaKotiakkuSensorEntityDescription, ...] = (
    ElisaKotiakkuSensorEntityDescription(
        key="battery_power_kw",
        name="Battery Power 🔋",
        emoji="🔋",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-high",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="state_of_charge_percent",
        name="Battery State Of Charge 🔋",
        emoji="🔋",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-heart-variant",
        suggested_display_precision=1,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="solar_power_kw",
        name="Solar Power ☀️",
        emoji="☀️",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="grid_power_kw",
        name="Grid Power ⚡",
        emoji="⚡",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="house_power_kw",
        name="House Power 🏠",
        emoji="🏠",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="solar_to_house_kw",
        name="Solar To House ☀️🏠",
        emoji="☀️",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-import-outline",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="solar_to_battery_kw",
        name="Solar To Battery ☀️🔋",
        emoji="☀️",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-up",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="solar_to_grid_kw",
        name="Solar To Grid ☀️⚡",
        emoji="☀️",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="grid_to_house_kw",
        name="Grid To House ⚡🏠",
        emoji="⚡",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-import-outline",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="grid_to_battery_kw",
        name="Grid To Battery ⚡🔋",
        emoji="⚡",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="battery_to_house_kw",
        name="Battery To House 🔋🏠",
        emoji="🔋",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-export-outline",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="battery_to_grid_kw",
        name="Battery To Grid 🔋⚡",
        emoji="🔋",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="spot_price_cents_per_kwh",
        name="Spot Price 💶",
        emoji="💶",
        native_unit_of_measurement="c/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-eur",
        suggested_display_precision=3,
    ),
    ElisaKotiakkuSensorEntityDescription(
        key="battery_temperature_celsius",
        name="Battery Temperature 🌡️",
        emoji="🌡️",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        suggested_display_precision=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elisa Kotiakku sensors from config entry."""
    coordinator: ElisaKotiakkuDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ElisaKotiakkuSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ElisaKotiakkuSensor(CoordinatorEntity[ElisaKotiakkuDataCoordinator], SensorEntity):
    """Representation of an Elisa Kotiakku sensor."""

    entity_description: ElisaKotiakkuSensorEntityDescription

    def __init__(
        self,
        coordinator: ElisaKotiakkuDataCoordinator,
        entry_id: str,
        description: ElisaKotiakkuSensorEntityDescription,
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.native_value is not None

    @property
    def native_value(self) -> Any:
        """Return current state value."""
        latest = self.coordinator.latest_row
        return latest.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose period timing metadata from latest row."""
        latest = self.coordinator.latest_row
        attributes: dict[str, Any] = {}
        if "period_start" in latest:
            attributes["period_start"] = latest["period_start"]
        if "period_end" in latest:
            attributes["period_end"] = latest["period_end"]
        if self.entity_description.emoji:
            attributes["emoji"] = self.entity_description.emoji
        return attributes
