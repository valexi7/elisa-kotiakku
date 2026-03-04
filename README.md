# Elisa Kotiakku Home Assistant Custom Component

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?business=DS47TSR4VGKFL&no_recurring=0&item_name=Tech+is+a+playground+for+solving+real-world+problems+and+building+tools+that+make+life+easier+for+others.&currency_code=EUR)
[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/valexi)

Custom integration for Home Assistant that reads your Elisa Kotiakku data from:

- `https://residential.gridle.com/api/public/measurements`
- Authentication header: `x-api-key: <your_api_key>`

## Features

- Config Flow UI setup (no YAML required)
- Automatic sensor creation for all public API measurement variables
- Correct units and device classes
- Emoji-enhanced sensor names for quick dashboard readability
- Period metadata (`period_start`, `period_end`) in sensor attributes

## Installation

### Install with HACS

1. Open HACS in Home Assistant.
2. Go to `Integrations`.
3. Open the menu (three dots) and select `Custom repositories`.
4. Add this repository URL and select category `Integration`.
5. Search for `Elisa Kotiakku` in HACS and install it.
6. Restart Home Assistant.
7. Go to `Settings -> Devices & Services -> Add Integration`.
8. Search for `Elisa Kotiakku` and open it.
9. Enter your API key.

### HACS Requirements

- HACS must already be installed in Home Assistant.
- This repository needs to be available as a public GitHub repository for HACS custom repository installation.

## API Key

Create your API key in the Kotiakku app:

- `Settings -> Data -> API`

## Sensors Created

The integration creates sensors for:

- `battery_power_kw` (`kW`)
- `state_of_charge_percent` (`%`)
- `solar_power_kw` (`kW`)
- `grid_power_kw` (`kW`)
- `house_power_kw` (`kW`)
- `solar_to_house_kw` (`kW`)
- `solar_to_battery_kw` (`kW`)
- `solar_to_grid_kw` (`kW`)
- `grid_to_house_kw` (`kW`)
- `grid_to_battery_kw` (`kW`)
- `battery_to_house_kw` (`kW`)
- `battery_to_grid_kw` (`kW`)
- `spot_price_cents_per_kwh` (`c/kWh`)
- `battery_temperature_celsius` (`°C`)

## Notes

- API data is polled every 5 minutes.
- If the latest row has `null` values for a field, that sensor becomes temporarily unavailable.
