# Parental Control – Home Assistant integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

HACS integration for Home Assistant that applies a **weekly schedule** to one or more parental control switches. For each day of the week you define a time window during which the selected switches are **turned off automatically**. Outside that window they are **turned back on**.

This integration was originally created to drive **GL.iNet parental control switches** exposed by [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router). It works with any Home Assistant switch.

---

## Purpose

On a GL.iNet router, parental control often appears as Home Assistant switches (a group, a profile, or a child's internet access). This integration **opens access during specific hours** and **re-enables parental control the rest of the time**, without writing YAML automations.

You can select as many switches as you want on a single schedule, and add several instances if you need different weekly windows.

---

## How it works

| When | Default action on every selected switch |
|------|------------------------------------------|
| During the day's window | `switch.turn_off` — parental control is deactivated |
| Outside the window | `switch.turn_on` — parental control is reactivated |
| Day not enabled in the schedule | switches stay on all day |

- If the start time is **later** than the end time (for example 21:00 → 07:00), the window **crosses midnight**.
- The schedule is re-evaluated **every minute** and also when Home Assistant starts.
- A **Scheduler** switch can suspend automatic enforcement without deleting the schedule.
- **Invert switch logic** flips on/off if your GL.iNet (or other) switches work the other way around.

---

## Created entities

For each instance (for example `Kids`):

| Entity | Type | Description |
|--------|------|-------------|
| `switch.kids_scheduler` | Switch | Enables or suspends the automatic schedule |
| `binary_sensor.kids_allowed_period` | Binary sensor | `on` during the allowed window |
| `sensor.kids_weekly_schedule` | Sensor | Current weekly windows (also as attributes) |
| `sensor.kids_next_change` | Sensor | Timestamp of the next on/off change |
| `sensor.kids_status` | Sensor | `allowed` / `restricted` / `disabled` / `unavailable` |

Entity IDs depend on the name you give the instance. Attributes list every selected switch, its current state, and the full week.

---

## Installation via HACS

1. Open HACS in Home Assistant
2. Click **Integrations** → ⋮ → **Custom repositories**
3. Add the URL: `https://github.com/daxharry/hacs_parental_control`
4. Category: **Integration**
5. Click **Download**
6. Restart Home Assistant

This HACS integration is installed from the repository branch content, without a GitHub release archive. `hacs.json` therefore sets `zip_release: false`.

## Manual installation

1. Copy the `custom_components/parental_control/` folder into `/config/custom_components/`
2. Restart Home Assistant

---

## Configuration

Parental Control is a normal Home Assistant integration. After install and restart it appears under **Settings → Devices & services → Integrations** (not under Helpers).

1. Go to **Settings → Devices & services → Integrations**
2. Click **Add integration** and search for **Parental Control**
3. Give it a name (for example a child's name)
4. Select **one or more** parental control switches (GL.iNet switches from ha-glinet-router, or any other switches)
5. For each weekday, optionally enable a window and set the start and end times

### View and edit the current config

1. Open **Settings → Devices & services → Integrations**
2. Select **Parental Control**
3. Click **Configure**

The dialog shows the current weekly schedule at the top, then the selected switches and every weekday window so you can change them in one place.

The **Weekly schedule** sensor on the device also displays the same config (`Mon 16:00–20:00 · Tue off · …`), with a markdown table in the `schedule_markdown` attribute for Lovelace.

### Example

| Day | Window |
|-----|--------|
| Monday – Friday | 16:00 – 20:00 |
| Saturday – Sunday | 10:00 – 21:00 |

During those hours, every selected GL.iNet parental control switch is turned off (access allowed). The rest of the time they are turned back on.

---

## Requirements

- Home Assistant ≥ 2024.1.0
- One or more existing switches in Home Assistant, typically parental control switches from [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router)

---

## Icon

- HACS and Home Assistant use `custom_components/parental_control/brand/icon.png` and `custom_components/parental_control/brand/logo.png`
- Root `icon.png` is used for GitHub display
- Entities use `mdi:*` icons

---

## License

MIT License
