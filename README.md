# SwitchBot Relay 2PM Cover

A custom Home Assistant integration for controlling SwitchBot Relay Switch 2PM devices as native covers and reading electrical measurements using the SwitchBot Open API.

## Features

- Automatically discovers all supported Relay Switch 2PM devices in the SwitchBot account
- Automatically adds newly discovered supported devices while the integration is running
- Open and close covers, set target position, and read position feedback
- Sends the SwitchBot `pause` command for stopping movement
- Adds per-channel sensors for voltage (V), electrical current (A), and power (W)
- Polls device status and measurements together every 30 seconds
- Stores the API token and secret in Home Assistant's config entry

## Electrical sensors

For each discovered Relay Switch 2PM, the integration creates six measurement sensors:

- Switch 1 voltage and Switch 2 voltage (V)
- Switch 1 current and Switch 2 current (A)
- Switch 1 power and Switch 2 power (W)

The SwitchBot API reports current in milliamps; the integration converts it to amps for Home Assistant. Sensors use the same device-status response as the cover entity, so they do not create extra API requests per sensor. A sensor remains without a numeric value if the API omits its corresponding field.

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
7. Enter your SwitchBot API token and secret. The integration discovers all supported Relay Switch 2PM devices in that account.

Existing installations configured as individual device entries are still read using their saved credentials. If multiple old entries exist for the same account, duplicate API polling may occur.

## Security

Never commit API tokens or secrets to this repository. Enter credentials only in the Home Assistant integration setup.

## Development status

Automatic discovery and electrical measurement sensors are implemented in code but still require practical verification in Home Assistant. Confirm that the device API returns the six measurement fields for your device and firmware. The integration uses the SwitchBot cloud API and is not a safety device.
