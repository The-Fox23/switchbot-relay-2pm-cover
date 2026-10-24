# SwitchBot Relay 2PM Cover

A custom Home Assistant integration for controlling a SwitchBot Relay Switch 2PM as a native cover (roller shutter) using the SwitchBot Open API.

## Features

- Open and close the cover
- Set a target position
- Read the position reported by SwitchBot
- Select a supported Relay Switch device during setup
- Store the API token and secret in Home Assistant's config entry

## Position mapping

The SwitchBot API reports `position: 0` as fully open and `position: 100` as fully closed. Home Assistant cover positions use the opposite convention, so the integration converts values using:

`Home Assistant position = 100 - SwitchBot position`

## Requirements

- A SwitchBot account and an API token/secret from the SwitchBot app
- A SwitchBot Relay Switch 2PM configured for roller-shutter control and calibrated
- Home Assistant with custom integrations support

## Installation via HACS

1. In HACS, open **Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add `The-Fox23/switchbot-relay-2pm-cover` as an **Integration**.
4. Install **SwitchBot Relay 2PM Cover**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration** and search for **SwitchBot Relay 2PM Cover**.
7. Enter your SwitchBot API token and secret, then select the device.

## Security

Never commit API tokens or secrets to this repository. Enter credentials only in the Home Assistant integration setup.

## Development status

Initial development scaffold. Test device selection, position reporting, and movement in your own installation before relying on it for everyday use. The integration sends commands through the SwitchBot cloud API; it is not a safety device.
