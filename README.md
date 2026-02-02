# petTracer Integration for Home Assistant

This custom integration allows you to track your pet's location using the petTracer cat collar in Home Assistant.

## Features

- **GPS Tracking**: View your pet's real-time location on the Home Assistant map
- **Device Tracker Entity**: Each petTracer collar appears as a device tracker entity
- **Battery Monitoring**: Track the battery level of your pet's collar (shown in entity attributes)
- **Automatic Updates**: Location updates every 5 minutes

## Installation

1. Copy the `pettracer` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the configuration to your `configuration.yaml` file

## Configuration

### YAML Configuration (Simple Setup)

Add the following to your `configuration.yaml`:

```yaml
pettracer:
  username: your_pettracer_username
  password: your_pettracer_password

device_tracker:
  - platform: pettracer
```

After adding this configuration:
1. Save the file
2. Restart Home Assistant
3. Your pet trackers will appear as device tracker entities

### Config Flow (UI Configuration)

Alternatively, you can set up the integration through the Home Assistant UI:
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "petTracer"
4. Enter your petTracer username and password

## Usage

Once configured, your petTracer devices will appear as:
- Device tracker entities (e.g., `device_tracker.pettracer_<device_id>`)
- Each entity will show up on the Home Assistant map
- The entity state will show "home", "not_home", or a zone name based on the GPS coordinates

### Entity Attributes

Each device tracker entity provides the following information:
- **latitude**: Current latitude coordinate
- **longitude**: Current longitude coordinate
- **gps_accuracy**: GPS accuracy in meters
- **source_type**: Always "gps"
- **battery_level**: Battery percentage (if available)
- **last_update**: Timestamp of the last location update

### Viewing on the Map

To view your pet's location on the map:
1. Go to the Home Assistant **Map** view
2. Your pet's device tracker will appear as a marker on the map
3. Click the marker to see details

### Creating Automations

You can create automations based on your pet's location:

```yaml
automation:
  - alias: "Notify when pet leaves home"
    trigger:
      - platform: state
        entity_id: device_tracker.pettracer_<device_id>
        from: "home"
        to: "not_home"
    action:
      - service: notify.mobile_app
        data:
          message: "Your pet has left home!"
```

## API Requirements

This integration requires the `pettracer-client` Python library (version 0.1.0), which should be automatically installed by Home Assistant.

The library provides access to:
- `async_get_devices()`: Retrieve list of all petTracer devices
- `async_get_device_location(device_id)`: Get current location for a specific device

## Troubleshooting

### Authentication Errors
If you see authentication errors in the logs:
1. Verify your username and password are correct
2. Check that you can log in to the petTracer web interface
3. Restart Home Assistant after correcting credentials

### No Devices Showing
If no device trackers appear:
1. Check the Home Assistant logs for errors
2. Verify that your petTracer account has active devices
3. Ensure the `pettracer-client` library is installed correctly

### Location Not Updating
If location isn't updating:
1. Check that your pet's collar has a GPS signal
2. Verify the collar has sufficient battery
3. Check the `last_update` attribute to see when the last update occurred

## Support

For issues with the integration:
- Check the Home Assistant logs for errors
- Report issues on the GitHub repository

For issues with the petTracer service or hardware:
- Contact petTracer support
- Visit https://github.com/AmbientArchitect/petTracer-API

## License

This integration is provided as-is for use with the petTracer pet tracking service.
