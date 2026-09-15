# Parental Control for Home Assistant

<p align="center">
  <img src="icon.png" alt="Parental Control" width="128" height="128">
</p>

Weekly schedule that **automatically turns parental control switches off** during a time window defined for each day of the week. You can select as many switches as you want.

Originally created for **GL.iNet** parental control switches from the [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router) integration. Works with any Home Assistant switch.

This HACS integration is installed directly from the repository content, without a GitHub release.

Appears under **Settings → Devices & services → Integrations**. Open the entry and click **Configure** to view and edit the current weekly schedule.

## Created entities

- 🗓️ **Scheduler** *(switch)* — enable or suspend the schedule
- ⏰ **Allowed period** *(binary sensor)*
- 📅 **Weekly schedule** — current config at a glance
- ⏭️ **Next change**
- ℹ️ **Status**

## Icon

- HACS and Home Assistant use `custom_components/parental_control/brand/icon.png` and `custom_components/parental_control/brand/logo.png`.
- Root `icon.png` is only used to display this page.
