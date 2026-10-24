# SwitchBot Relay 2PM Cover

A custom Home Assistant integration for controlling SwitchBot Relay Switch 2PM devices as native covers using the SwitchBot Open API.

## Features

- Automatically discovers all supported Relay Switch 2PM devices in the SwitchBot account
- Automatically adds newly discovered supported devices while the integration is running
- Open and close covers
- Set a target position and read the position reported by SwitchBot
- Send the SwitchBot `pause` command for stopping movement
- Store the API token and secret in Home Assistant's config entry

## Position mapping

The SwitchBot API reports `position: 0` as fully open and `position: 100` as fully closed. Home Assistant cover positions use the opposite convention, so the integration converts values using:

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

Existing installations that were configured as individual device entries are still read using their saved credentials. The updated discovery logic can add all supported devices from that account; duplicate entity unique IDs are based on the physical device ID.

## Security

Never commit API tokens or secrets to this repository. Enter credentials only in the Home Assistant integration setup.

## Development status

Automatic device discovery is implemented in the code but should be verified in Home Assistant with at least two supported devices, including adding a new device after setup. The integration sends commands through the SwitchBot cloud API; it is not a safety device.
