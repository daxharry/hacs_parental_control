"""Weekly schedule helpers for Parental Control."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any

from .const import DEFAULT_END, DEFAULT_START, WEEKDAYS


@dataclass(frozen=True)
class DaySchedule:
    """One day's allowed window."""

    enabled: bool
    start: time
    end: time


def merged_config(entry_data: dict[str, Any], entry_options: dict[str, Any]) -> dict[str, Any]:
    """Return config options over data."""
    return {**entry_data, **entry_options}


def parse_time(value: str | None, default: str) -> time:
    """Parse a Home Assistant time selector value (HH:MM or HH:MM:SS)."""
    raw = (value or default).strip()
    parts = [int(p) for p in raw.split(":")]
    while len(parts) < 3:
        parts.append(0)
    hour, minute, second = parts[0], parts[1], parts[2]
    return time(hour % 24, minute, second)


def format_time(value: time) -> str:
    """Format a time as HH:MM."""
    return value.strftime("%H:%M")


def weekday_key(dt: datetime) -> str:
    """Return monday..sunday for a datetime."""
    return WEEKDAYS[dt.weekday()]


def day_from_config(config: dict[str, Any], day: str) -> DaySchedule:
    """Build a DaySchedule from flattened config keys."""
    return DaySchedule(
        enabled=bool(config.get(f"{day}_enabled", False)),
        start=parse_time(config.get(f"{day}_start"), DEFAULT_START),
        end=parse_time(config.get(f"{day}_end"), DEFAULT_END),
    )


def _combine(day: datetime | Any, t: time, tzinfo) -> datetime:
    """Combine a date and time, keeping tzinfo when present."""
    date_value = day.date() if isinstance(day, datetime) else day
    result = datetime.combine(date_value, t)
    if tzinfo is not None:
        result = result.replace(tzinfo=tzinfo)
    return result


def window_bounds(day_date, schedule: DaySchedule, tzinfo) -> tuple[datetime, datetime] | None:
    """Return (start, end) datetimes for a schedule attached to day_date."""
    if not schedule.enabled or schedule.start == schedule.end:
        return None
    start_dt = _combine(day_date, schedule.start, tzinfo)
    if schedule.start < schedule.end:
        end_dt = _combine(day_date, schedule.end, tzinfo)
    else:
        end_dt = _combine(day_date + timedelta(days=1), schedule.end, tzinfo)
    return start_dt, end_dt


def is_in_allowed_period(now: datetime, config: dict[str, Any]) -> bool:
    """True when now is inside an enabled allowed window."""
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    for attached in (today, yesterday):
        schedule = day_from_config(config, weekday_key(attached))
        bounds = window_bounds(attached, schedule, now.tzinfo)
        if bounds is None:
            continue
        start_dt, end_dt = bounds
        if start_dt <= now < end_dt:
            return True
    return False


def next_change(now: datetime, config: dict[str, Any]) -> datetime | None:
    """Return the next start or end of an allowed window after now."""
    candidates: list[datetime] = []
    start_date = now.date()
    for offset in range(0, 8):
        day_date = start_date + timedelta(days=offset)
        attached = _combine(day_date, time.min, now.tzinfo)
        schedule = day_from_config(config, weekday_key(attached))
        bounds = window_bounds(day_date, schedule, now.tzinfo)
        if bounds is None:
            continue
        candidates.extend(bounds)
    future = sorted(dt for dt in candidates if dt > now)
    return future[0] if future else None


def today_window(now: datetime, config: dict[str, Any]) -> DaySchedule:
    """Return today's configured schedule."""
    return day_from_config(config, weekday_key(now))


DAY_SHORT = {
    "monday": "Mon",
    "tuesday": "Tue",
    "wednesday": "Wed",
    "thursday": "Thu",
    "friday": "Fri",
    "saturday": "Sat",
    "sunday": "Sun",
}

DAY_LABELS = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}


def day_window_label(config: dict[str, Any], day: str) -> str:
    """Return 'HH:MM–HH:MM' or 'off' for a weekday."""
    schedule = day_from_config(config, day)
    if not schedule.enabled:
        return "off"
    return f"{format_time(schedule.start)}–{format_time(schedule.end)}"


def week_config(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return structured weekly windows for attributes and the UI."""
    result: dict[str, dict[str, Any]] = {}
    for day in WEEKDAYS:
        schedule = day_from_config(config, day)
        result[day] = {
            "enabled": schedule.enabled,
            "start": format_time(schedule.start) if schedule.enabled else None,
            "end": format_time(schedule.end) if schedule.enabled else None,
            "label": day_window_label(config, day),
        }
    return result


def schedule_summary(config: dict[str, Any]) -> str:
    """Compact one-line view of the weekly schedule."""
    return " · ".join(f"{DAY_SHORT[day]} {day_window_label(config, day)}" for day in WEEKDAYS)


def schedule_markdown(config: dict[str, Any]) -> str:
    """Markdown table of the weekly schedule."""
    lines = ["| Day | Window |", "|---|---|"]
    for day in WEEKDAYS:
        lines.append(f"| {DAY_LABELS[day]} | {day_window_label(config, day)} |")
    return "\n".join(lines)
