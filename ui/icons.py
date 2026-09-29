"""Ikonki emoji dla gry — zero zewnętrznych assetów, działają wszędzie.

Emoji są renderowane natywnie przez Qt jako tekst kolorowy (jeśli system ma
font emoji) lub czarno-biały. Na Windows 10+ działają kolorowo (Segoe UI Emoji).
"""
from __future__ import annotations

# Ikonki głównych obiektów
ICON_SERVER = "🖥️"
ICON_SERVER_DOWN = "🖥️❌"
ICON_SERVER_WARN = "🖥️⚠️"
ICON_CUSTOMER = "👥"
ICON_EMPLOYEE = "👤"
ICON_MONEY = "💰"
ICON_CASH = "💵"
ICON_REPUTATION = "⭐"
ICON_WARNING = "⚠️"
ICON_OK = "✅"
ICON_ERROR = "❌"
ICON_DOWN = "🔴"
ICON_COOL = "🟢"
ICON_FIRE = "🔥"
ICON_BOLT = "⚡"
ICON_NETWORK = "🌐"
ICON_DDNS = "🛡️"
ICON_DDoS = "💀"
ICON_DISK = "💾"
ICON_CPU = "⚙️"
ICON_RAM = "🔋"
ICON_RACK = "🗄️"
ICON_DC = "🏢"
ICON_REGION = "🌍"
ICON_GARAGE = "🏠"

# Ikonki ról pracowników
ROLE_ICONS = {
    "support": "🎧",     # słuchawki — support
    "sysadmin": "🔧",   # klucz francuski — sysadmin
    "neteng": "🌐",     # kula ziemska — network engineer
    "sales": "💼",       # walizka — sprzedaż
    "marketing": "📢",  # megafon — marketing
}

# Ikonki typów awarii
FAILURE_ICONS = {
    "disk": "💾❌",
    "cpu_overload": "⚙️🔥",
    "overheat": "🌡️🔥",
    "power": "⚡❌",
    "network": "🌐❌",
    "ddos": "💀",
}

# Ikonki typów produktów
PRODUCT_ICONS = {
    "www": "🌐",
    "vps": "🖥️",
    "dedicated": "🗄️",
    "domain": "🏷️",
}

# Ikonki akcji
ICON_ACTION_RESTART = "🔄"
ICON_ACTION_REPLACE = "🔁"
ICON_ACTION_FAILOVER = "↩️"
ICON_ACTION_IGNORE = "🗑️"
ICON_EDIT = "✏️"
ICON_DELETE = "🗑️"
ICON_ADD = "➕"
ICON_SAVE = "💾"
ICON_PLAY = "▶️"
ICON_PAUSE = "⏸️"


def role_icon(role: str) -> str:
    return ROLE_ICONS.get(role, "👤")


def product_icon(product_type: str) -> str:
    return PRODUCT_ICONS.get(product_type, "📦")


def failure_icon(failure_type: str) -> str:
    return FAILURE_ICONS.get(failure_type, "⚠️")


def server_icon(status: str = "ok") -> str:
    if status == "down":
        return ICON_SERVER_DOWN
    if status == "maintenance":
        return ICON_SERVER_WARN
    return ICON_SERVER