# SwitchBot Relay 2PM Cover

A custom Home Assistant integration for controlling SwitchBot Relay Switch 2PM devices as native covers and reading electrical measurements using the SwitchBot Open API.

## Features

- Automatically discovers supported Relay Switch 2PM devices in the SwitchBot account
- Automatically adds newly discovered devices while the integration is running
- Native cover control: open, close, set position, and stop
- Cover icon uses a roller-shutter/window-shutter symbol
- Four aggregate sensors per device: voltage, current, power, and daily energy
- Combines current, power, and daily energy across both relay channels; voltage uses channel 1, falling back to channel 2
- Polls device status and measurements together every 30 seconds
- Stores the API token and secret in Home Assistant's config entry

## Measurement sensors

- **Voltage (V):** uses the voltage reported for channel 1, falling back to channel 2 if channel 1 is absent. The channels share the same mains supply.
- **Current (A):** sums the reported current from both channels. The API reports current in milliamps, which is converted to amps.
- **Power (W):** sums the power from both channels.
- **Daily energy (kWh):** sums `switch1UsedElectricity` and `switch2UsedElectricity`. The API documents these values in watt-minutes, converted to kWh by dividing by 60,000. This is daily consumption, not a lifetime cumulative counter.

The sensors use the same status response as the cover, so they do not create extra API requests per sensor. If the API omits a field, the sensor returns no numeric value rather than inventing one.

## Position mapping

The SwitchBot API reports `position: 0` as fully open and `position: 100` as fully closed. Home Assistant cover positions use the opposite convention:

`Home Assistant position = 100 - SwitchBot position`

## Requirements

- A SwitchBot account and an API token/secret from the SwitchBot app
- SwitchBot Relay Switch 2PM device(s) configured for roller-shutter control and calibrated
- Home Assistant with custom integrations support

## Installation via HACS

1. In HACS, open **Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add `The-Fox23/switchbot-relay-2pm-cover` as an **Integration**.
4. Install **SwitchBot Relay 2PM Cover**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration** and search for **SwitchBot Relay 2PM Cover**.
7. Enter your SwitchBot API token and secret. The integration discovers supported devices in that account.

Existing installations configured as individual device entries are still read using their saved credentials. If multiple old entries exist for the same account, duplicate API polling may occur.

## Security

Never commit API tokens or secrets to this repository. Enter credentials only in the Home Assistant integration setup.

## Development status

Aggregate electrical sensors and daily energy calculation are implemented in code but still require practical verification in Home Assistant. Confirm the device API returns the expected fields for your device and firmware. The integration uses the SwitchBot cloud API and is not a safety device.
