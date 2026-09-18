# 🐾 petTracer Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/AmbientArchitect/Home-Assistant-petTracer-integration.svg)](https://github.com/AmbientArchitect/Home-Assistant-petTracer-integration/releases)
[![License](https://img.shields.io/github/license/AmbientArchitect/Home-Assistant-petTracer-integration.svg)](LICENSE)

Track your pet's location in real-time with the **petTracer** cat collar integration for Home Assistant! 🐱📍

---

## ✨ Features

- 🗺️ **GPS Tracking** - View your pet's real-time location on the Home Assistant map
- 📍 **Device Tracker Entity** - Each petTracer collar appears as a device tracker entity
- 📊 **Sensor Entities** - Monitor battery level, charging status, tracking mode, GPS quality, and more
- 🔋 **Battery Monitoring** - Dedicated battery level sensor with voltage information
- ⚡ **Charging Status** - Know when your pet's collar is charging
- 🔴 **Live Tracking Status** - See when live tracking mode is enabled
- ⚡ **Realtime Push Updates** - Location and status changes stream in as they happen, instead of waiting on a poll interval
- 🛰️ **GPS Quality** - Monitor satellite count and signal strength
- 🎛️ **Tracking Mode Control** - Choose the collar's tracking speed (Fast, Normal, Slow, Super slow) from a select entity
- 🔎 **Find My Cat** - A button to trigger the collar's temporary high-frequency search mode
- 💡 **LED Switch** - Turn the collar's LED on or off
- 🔊 **Buzzer Switch** - Turn the collar's buzzer on or off (on collars that have one)

---

## 📦 Installation

### Manual Installation

1. 📁 Copy the `pettracer` folder to your Home Assistant `custom_components` directory
2. 🔄 Restart Home Assistant
3. ⚙️ Set up the integration through the UI

> **📝 Note:** This integration requires Home Assistant **2024.4.0** or newer (it depends on a library that requires Python 3.12+).

### HACS Installation

1. Click the button below to add this repository to HACS:
   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=AmbientArchitect&repository=Home-Assistant-petTracer-integration&category=integration)

2. Install the integration from HACS
3. 🔄 Restart Home Assistant
4. ⚙️ Set up the integration through the UI

---

## ⚙️ Configuration

### 🎨 Config Flow (UI Configuration)

This integration is configured through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
2. Click **➕ Add Integration**
3. 🔍 Search for "**petTracer**"
4. 🔑 Enter your petTracer username and password

> **📝 Note:** YAML configuration is no longer supported. Use the UI-based config flow for all setup.

---

## 🚀 Usage

Once configured, your petTracer devices will appear as:

- 📍 Device tracker entity (e.g., `device_tracker.pettracer_<device_id>`)
- 📊 Multiple sensor entities for detailed information
- 💡 LED switch, and a buzzer switch on collars that have one
- 🎛️ Tracking mode select entity
- 🔎 Find button to trigger search mode

### 📍 Device Tracker Entity

The device tracker entity shows:

- 🗺️ Current location on the Home Assistant map
- 🏠 State: "home", "not_home", or zone name based on GPS coordinates

### 📊 Sensor Entities

Each device provides the following sensors:

| Sensor                 | Icon                    | Description                                               |
| ---------------------- | ----------------------- | --------------------------------------------------------- |
| 🔋 **Battery Level**   | `mdi:battery`           | Battery percentage (0-100%)                               |
| ⚡ **Battery Voltage** | `mdi:flash`             | Raw battery voltage in millivolts _(disabled by default)_ |
| 🔌 **Charging Status** | `mdi:battery-charging`  | Shows "Charging" or "Not charging"                        |
| 🎯 **Tracking Mode**   | `mdi:crosshairs`        | Current tracking mode - "Fast", "Normal", or "Slow"       |
| 🔴 **Live Tracking**   | `mdi:radar`             | Shows "On" or "Off" for search/live tracking mode         |
| 🛰️ **GPS Satellites**  | `mdi:satellite-variant` | Number of GPS satellites connected                        |
| 📶 **Signal Strength** | `mdi:signal`            | Cellular signal strength in dBm _(disabled by default)_   |
| 🕐 **Last Contact**    | `mdi:clock`             | Timestamp of last communication with the device           |

### 📋 Entity Attributes

The device tracker entity includes additional attributes:

- 🌍 **latitude** - Current latitude coordinate
- 🌍 **longitude** - Current longitude coordinate
- 🎯 **gps_accuracy** - GPS accuracy in meters
- 🔋 **battery_voltage** - Battery voltage in millivolts
- 🛰️ **satellites** - Number of GPS satellites
- 📶 **signal_strength** - Cellular signal strength
- 🔌 **charging** - Charging status text
- 🎯 **tracking_mode** - Current tracking mode
- 🔴 **live_tracking** - Live tracking status
- 🕐 **last_update** - Timestamp of the last location update
- 📞 **last_contact** - Last communication timestamp

### 🎛️ Collar Control

Each collar also exposes control entities:

| Entity                          | Type   | Description                                                        |
| -------------------------------- | ------ | -------------------------------------------------------------------- |
| 🎯 **Tracking mode**             | Select | Choose Fast, Normal, Slow, or Super slow tracking speed              |
| 🔎 **Find**                      | Button | Activates the collar's temporary ~21s high-frequency search mode     |
| 💡 **LED**                       | Switch | Turns the collar's LED on/off                                        |
| 🔊 **Buzzer**                    | Switch | Turns the collar's buzzer on/off _(only shown if the collar has one)_ |

Mode changes and search mode are acknowledged asynchronously by the collar - watch the **Tracking mode** and **Live tracking** entities to see when the collar confirms the change.

### ⚡ Realtime Updates

Position and status updates are pushed from petTracer as they happen, rather than waiting on a fixed poll interval. A 15-minute background poll still runs as a fallback in case the push connection drops.

### 🗺️ Viewing on the Map

To view your pet's location on the map:

1. Go to the Home Assistant **🗺️ Map** view
2. Your pet's device tracker will appear as a marker on the map
3. Click the marker to see details

---

---

## 🤖 Creating Automations

You can create powerful automations based on your pet's location or device status:

### 🏠 Location-Based Automation

```yaml
automation:
  - alias: "🐱 Notify when pet leaves home"
    trigger:
      - platform: state
        entity_id: device_tracker.pettracer_<device_id>
        from: "home"
        to: "not_home"
    action:
      - service: notify.mobile_app
        data:
          message: "🚨 Your pet has left home!"
```

### 🔋 Low Battery Alert

```yaml
automation:
  - alias: "⚠️ Pet collar battery low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pettracer_<device_id>_battery_level
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "🔋 Pet collar battery is low ({{ states('sensor.pettracer_<device_id>_battery_level') }}%)"
```

### 🔌 Charging Notification

```yaml
automation:
  - alias: "⚡ Pet collar charging"
    trigger:
      - platform: state
        entity_id: sensor.pettracer_<device_id>_charging_status
        to: "Charging"
    action:
      - service: notify.mobile_app
        data:
          message: "🔌 Pet collar is now charging"
```

### 🔎 Find the Collar

```yaml
automation:
  - alias: "🔎 Find pet collar"
    trigger:
      - platform: state
        entity_id: input_boolean.find_pet
        to: "on"
    action:
      - service: button.press
        target:
          entity_id: button.pet_tracker_<device_id>_find
```

---

## 🔧 API Requirements

This integration requires the `pettracer-client` Python library (v0.3.0+), which is automatically installed by Home Assistant.

The library provides access to the petTracer API for retrieving device information and location data, a realtime push-update stream, and collar control (LED, buzzer, tracking mode, search mode).

---

## 🆘 Troubleshooting

### 🔑 Authentication Errors

If you see authentication errors in the logs:

1. ✅ Verify your username and password are correct
2. 🌐 Check that you can log in to the petTracer web interface
3. ⚙️ Use the "Reconfigure" option in Settings → Devices & Services to update credentials

### 📍 No Devices Showing

If no device trackers or sensors appear:

1. 📋 Check the Home Assistant logs for errors
2. ✅ Verify that your petTracer account has active devices
3. 🔄 Try reloading the integration from Settings → Devices & Services

### 🗺️ Location Not Updating

If location isn't updating:

1. 🛰️ Check that your pet's collar has a GPS signal (view the "GPS satellites" sensor)
2. 🔋 Verify the collar has sufficient battery (view the "Battery level" sensor)
3. 🕐 Check the "Last contact" sensor to see when the device last communicated
4. 📋 Review the Home Assistant logs for any API errors

### 👁️ Entities Missing

If some sensor entities are missing:

1. ✅ Check if they are disabled in the entity registry
2. ⚙️ Go to Settings → Devices & Services → petTracer
3. 🖱️ Click on your device
4. 👁️ Look for disabled entities and enable them if needed

---

## 💬 Support

### 🐛 Integration Issues

- 📋 Check the Home Assistant logs for errors
- 🐙 Report issues on the [GitHub repository](https://github.com/AmbientArchitect/Home-Assistant-petTracer-integration/issues)

---

## 📄 License

This integration is provided as-is for use with the petTracer pet tracking service.

---

<div align="center">

**Made with ❤️ for pet lovers**

🐱 🐶 🐾

</div>
