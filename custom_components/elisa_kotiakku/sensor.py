"""Sensor platform for Elisa Kotiakku integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import EXPECTED_MEASUREMENT_KEYS, ElisaKotiakkuDataCoordinator


@dataclass(frozen=True, kw_only=True)
class ElisaKotiakkuSensorEntityDescription(SensorEntityDescription):
    """Describes Elisa Kotiakku sensor entity."""

    emoji: str


@dataclass(frozen=True, kw_only=True)
class ElisaKotiakkuEnergySensorEntityDescription(SensorEntityDescription):
    """Describes Elisa Kotiakku cumulative energy sensor entity."""

    value_fn: Callable[[dict[str, Any]], float]


@dataclass(frozen=True, kw_only=True)
class ElisaKotiakkuDerivedPowerSensorEntityDescription(SensorEntityDescription):
    """Describes Elisa Kotiakku derived live power sensor entity."""

    value_fn: Callable[[dict[str, Any]], float | None]


@dataclass(frozen=True, kw_only=True)
class ElisaKotiakkuDiagnosticSensorEntityDescription(SensorEntityDescription):
    """Describes Elisa Kotiakku diagnostic sensor entity."""

    value_fn: Callable[[ElisaKotiakkuDataCoordinator], Any]


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


def _as_float(value: Any) -> float:
    """Convert numeric value to float, or return 0.0."""
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _flow_or_fallback(
    row: dict[str, Any],
    primary_keys: tuple[str, ...],
    fallback: float,
) -> float:
    """Use flow keys when present, otherwise use fallback value."""
    values = [_as_float(row.get(key)) for key in primary_keys if row.get(key) is not None]
    if values:
        return max(sum(values), 0.0)
    return max(fallback, 0.0)


def _sum_available(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    """Sum available keys; return None only if all source values are null/missing."""
    values: list[float] = []
    for key in keys:
        value = row.get(key)
        if value is not None:
            values.append(_as_float(value))

    if not values:
        return None

    return sum(values)


def _has_measurement_data(row: dict[str, Any]) -> bool:
    """Return True when latest row contains any non-null measurement value."""
    if not row:
        return False
    present = [key for key in EXPECTED_MEASUREMENT_KEYS if key in row]
    if not present:
        return False
    return any(row.get(key) is not None for key in present)


ENERGY_SENSOR_DESCRIPTIONS: tuple[ElisaKotiakkuEnergySensorEntityDescription, ...] = (
    ElisaKotiakkuEnergySensorEntityDescription(
        key="solar_energy_total",
        name="Solar Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power-variant",
        value_fn=lambda row: max(_as_float(row.get("solar_power_kw")), 0.0),
    ),
    ElisaKotiakkuEnergySensorEntityDescription(
        key="house_consumption_energy_total",
        name="House Consumption Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:home-lightning-bolt-outline",
        value_fn=lambda row: max(-_as_float(row.get("house_power_kw")), 0.0),
    ),
    ElisaKotiakkuEnergySensorEntityDescription(
        key="grid_import_energy_total",
        name="Grid Import Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
        value_fn=lambda row: _flow_or_fallback(
            row,
            ("grid_to_house_kw", "grid_to_battery_kw"),
            _as_float(row.get("grid_power_kw")),
        ),
    ),
    ElisaKotiakkuEnergySensorEntityDescription(
        key="grid_export_energy_total",
        name="Grid Export Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
        value_fn=lambda row: _flow_or_fallback(
            row,
            ("solar_to_grid_kw", "battery_to_grid_kw"),
            -_as_float(row.get("grid_power_kw")),
        ),
    ),
    ElisaKotiakkuEnergySensorEntityDescription(
        key="battery_charge_energy_total",
        name="Battery Charge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-arrow-up-outline",
        value_fn=lambda row: _flow_or_fallback(
            row,
            ("solar_to_battery_kw", "grid_to_battery_kw"),
            -_as_float(row.get("battery_power_kw")),
        ),
    ),
    ElisaKotiakkuEnergySensorEntityDescription(
        key="battery_discharge_energy_total",
        name="Battery Discharge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-arrow-down-outline",
        value_fn=lambda row: _flow_or_fallback(
            row,
            ("battery_to_house_kw", "battery_to_grid_kw"),
            _as_float(row.get("battery_power_kw")),
        ),
    ),
)


DERIVED_POWER_SENSOR_DESCRIPTIONS: tuple[
    ElisaKotiakkuDerivedPowerSensorEntityDescription, ...
] = (
    ElisaKotiakkuDerivedPowerSensorEntityDescription(
        key="grid_consumption_kw",
        name="Grid Consumption",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        value_fn=lambda row: _sum_available(row, ("grid_to_house_kw", "grid_to_battery_kw")),
    ),
    ElisaKotiakkuDerivedPowerSensorEntityDescription(
        key="grid_production_kw",
        name="Grid Production",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        value_fn=lambda row: _sum_available(row, ("solar_to_grid_kw", "battery_to_grid_kw")),
    ),
    ElisaKotiakkuDerivedPowerSensorEntityDescription(
        key="battery_consumption_kw",
        name="Battery Consumption",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-up",
        value_fn=lambda row: _sum_available(row, ("grid_to_battery_kw", "solar_to_battery_kw")),
    ),
    ElisaKotiakkuDerivedPowerSensorEntityDescription(
        key="battery_production_kw",
        name="Battery Production",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-down",
        value_fn=lambda row: _sum_available(row, ("battery_to_grid_kw", "battery_to_house_kw")),
    ),
)


DIAGNOSTIC_SENSOR_DESCRIPTIONS: tuple[
    ElisaKotiakkuDiagnosticSensorEntityDescription, ...
] = (
    ElisaKotiakkuDiagnosticSensorEntityDescription(
        key="sensor_data_available",
        name="Sensor Data Available",
        icon="mdi:database-check-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _has_measurement_data(coordinator.latest_row),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elisa Kotiakku sensors from config entry."""
    coordinator: ElisaKotiakkuDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        ElisaKotiakkuSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    entities.extend(
        ElisaKotiakkuEnergySensor(coordinator, entry.entry_id, description)
        for description in ENERGY_SENSOR_DESCRIPTIONS
    )
    entities.extend(
        ElisaKotiakkuDerivedPowerSensor(coordinator, entry.entry_id, description)
        for description in DERIVED_POWER_SENSOR_DESCRIPTIONS
    )
    entities.extend(
        ElisaKotiakkuDiagnosticSensor(coordinator, entry.entry_id, description)
        for description in DIAGNOSTIC_SENSOR_DESCRIPTIONS
    )
    async_add_entities(entities)


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


class ElisaKotiakkuEnergySensor(
    CoordinatorEntity[ElisaKotiakkuDataCoordinator], SensorEntity, RestoreEntity
):
    """Cumulative energy sensor derived from time-series power values."""

    entity_description: ElisaKotiakkuEnergySensorEntityDescription

    def __init__(
        self,
        coordinator: ElisaKotiakkuDataCoordinator,
        entry_id: str,
        description: ElisaKotiakkuEnergySensorEntityDescription,
    ) -> None:
        """Initialize cumulative energy sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._native_value = 0.0
        self._last_period_end: datetime | None = None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is None:
            return

        try:
            self._native_value = float(last_state.state)
        except (ValueError, TypeError):
            self._native_value = 0.0

        restored_end = last_state.attributes.get("last_period_end")
        if isinstance(restored_end, str):
            self._last_period_end = dt_util.parse_datetime(restored_end)

    @property
    def available(self) -> bool:
        """Return availability of this sensor."""
        return self.coordinator.last_update_success or self._native_value > 0

    @property
    def native_value(self) -> float:
        """Return cumulative energy value in kWh."""
        return round(self._native_value, 6)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for debugging and restore continuity."""
        if self._last_period_end is None:
            return {}
        return {"last_period_end": self._last_period_end.isoformat()}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Process new data rows and update accumulated state."""
        self._process_new_rows()
        self.async_write_ha_state()

    def _process_new_rows(self) -> None:
        """Accumulate energy using new period rows only."""
        for row in self.coordinator.data:
            period_start = self._parse_period(row.get("period_start"))
            period_end = self._parse_period(row.get("period_end"))

            if period_start is None or period_end is None or period_end <= period_start:
                continue
            if self._last_period_end is not None and period_end <= self._last_period_end:
                continue

            hours = (period_end - period_start).total_seconds() / 3600
            power_kw = max(self.entity_description.value_fn(row), 0.0)
            self._native_value += power_kw * hours
            self._last_period_end = period_end

    @staticmethod
    def _parse_period(value: Any) -> datetime | None:
        """Parse a period timestamp."""
        if not isinstance(value, str):
            return None
        return dt_util.parse_datetime(value)


class ElisaKotiakkuDerivedPowerSensor(
    CoordinatorEntity[ElisaKotiakkuDataCoordinator], SensorEntity
):
    """Live derived power sensor based on existing flow sensors."""

    entity_description: ElisaKotiakkuDerivedPowerSensorEntityDescription

    def __init__(
        self,
        coordinator: ElisaKotiakkuDataCoordinator,
        entry_id: str,
        description: ElisaKotiakkuDerivedPowerSensorEntityDescription,
    ) -> None:
        """Initialize derived power sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> float | None:
        """Return the derived live value."""
        latest = self.coordinator.latest_row
        if not latest:
            return None
        value = self.entity_description.value_fn(latest)
        if value is None:
            return None
        return round(value, 6)


class ElisaKotiakkuDiagnosticSensor(
    CoordinatorEntity[ElisaKotiakkuDataCoordinator], SensorEntity
):
    """Diagnostic sensor values for API/data state."""

    entity_description: ElisaKotiakkuDiagnosticSensorEntityDescription

    def __init__(
        self,
        coordinator: ElisaKotiakkuDataCoordinator,
        entry_id: str,
        description: ElisaKotiakkuDiagnosticSensorEntityDescription,
    ) -> None:
        """Initialize diagnostic sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> Any:
        """Return diagnostic value."""
        return self.entity_description.value_fn(self.coordinator)
