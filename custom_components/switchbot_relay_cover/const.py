"""Constants for the SwitchBot Relay 2PM Cover integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "switchbot_relay_cover"
PLATFORM = Platform.COVER
PLATFORMS = [Platform.COVER]
CONF_TOKEN = "token"
CONF_SECRET = "secret"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"

API_BASE_URL = "https://api.switch-bot.com/v1.1"
SCAN_INTERVAL = timedelta(seconds=30)
SUPPORTED_DEVICE_TYPES = ("relay switch 2pm",)
