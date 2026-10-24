"""Minimal asynchronous client for the SwitchBot Open API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
import uuid
from typing import Any

import aiohttp
from homeassistant.exceptions import HomeAssistantError

from .const import API_BASE_URL


class SwitchBotApi:
    """Small client for the SwitchBot cloud API."""

    def __init__(self, session: aiohttp.ClientSession, token: str, secret: str) -> None:
        self._session = session
        self._token = token
        self._secret = secret

    def _headers(self) -> dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        message = f"{self._token}{timestamp}{nonce}"
        signature = base64.b64encode(
            hmac.new(
                self._secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        return {
            "Authorization": self._token,
            "sign": signature,
            "t": timestamp,
            "nonce": nonce,
            "Content-Type": "application/json; charset=utf8",
        }

    async def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a signed API request and return the decoded response."""
        url = f"{API_BASE_URL}{path}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers(),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    raise HomeAssistantError(
                        f"SwitchBot API returned HTTP {response.status}"
                    )
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise HomeAssistantError("Unable to communicate with the SwitchBot API") from err

        if not isinstance(data, dict):
            raise HomeAssistantError("Unexpected response from the SwitchBot API")
        if data.get("statusCode", 100) != 100:
            message = data.get("message", "Unknown SwitchBot API error")
            raise HomeAssistantError(f"SwitchBot API error: {message}")
        return data

    async def get_devices(self) -> list[dict[str, Any]]:
        """Return the devices known to the SwitchBot account."""
        data = await self.request("GET", "/devices")
        body = data.get("body", {})
        devices = body.get("deviceList", [])
        if not isinstance(devices, list):
            raise HomeAssistantError("SwitchBot API returned an invalid device list")
        return [device for device in devices if isinstance(device, dict)]

    async def get_status(self, device_id: str) -> dict[str, Any]:
        """Return status for one device."""
        data = await self.request("GET", f"/devices/{device_id}/status")
        body = data.get("body", {})
        if not isinstance(body, dict):
            raise HomeAssistantError("SwitchBot API returned an invalid device status")
        return body

    async def pause(self, device_id: str) -> None:
        """Pause movement of a Relay Switch 2PM cover."""
        await self.request(
            "POST",
            f"/devices/{device_id}/commands",
            {
                "command": "pause",
                "parameter": "",
                "commandType": "command",
            },
        )

    async def turn_off(self, device_id: str, channel: int) -> None:
        """Turn off one relay channel."""
        if channel not in (1, 2):
            raise ValueError("SwitchBot relay channel must be 1 or 2")
        await self.request(
            "POST",
            f"/devices/{device_id}/commands",
            {
                "command": "turnOff",
                "parameter": str(channel),
                "commandType": "command",
            },
        )

    async def set_position(self, device_id: str, position: int) -> None:
        """Set the device position using the SwitchBot 0=open, 100=closed scale."""
        await self.request(
            "POST",
            f"/devices/{device_id}/commands",
            {
                "command": "setPosition",
                "parameter": str(max(0, min(100, position))),
                "commandType": "command",
            },
        )
