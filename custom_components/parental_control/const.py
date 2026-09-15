"""Constants for the Parental Control integration."""

from __future__ import annotations

DOMAIN = "parental_control"

CONF_NAME = "name"
CONF_SWITCH_ENTITY = "switch_entity_id"
CONF_INVERT = "invert"

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

DEFAULT_START = "16:00:00"
DEFAULT_END = "20:00:00"

ATTR_SWITCH_ENTITY = "switch_entity_id"
ATTR_IN_PERIOD = "in_allowed_period"
ATTR_DESIRED_STATE = "desired_switch_state"
ATTR_TODAY = "today"
ATTR_TODAY_START = "today_start"
ATTR_TODAY_END = "today_end"

STATUS_DISABLED = "disabled"
STATUS_UNAVAILABLE = "unavailable"
STATUS_ALLOWED = "allowed"
STATUS_RESTRICTED = "restricted"
