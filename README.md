# Mattress Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration to track mattress maintenance, including flipping and rotating.

## Features

- **Track Side**: Keeps track of which side of the mattress is currently facing up (e.g., Side A or Side B).
- **Track Rotation**: Keeps track of the current orientation (Top at Head or Top at Foot).
- **Maintenance History**: Stores the dates of the last flip and the last rotation.
- **Easy Recording**: Use buttons in the UI to quickly record a flip or rotation today.
- **Flexible Services**: Use services to record maintenance for specific dates, useful for logging past events.

## Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Paste `https://github.com/lougovsk/ha-mattress-tracker` into the URL field.
4. Select **Integration** as the category and click **Add**.
5. Find **Mattress Tracker** in the HACS list and click **Download**.
6. Restart Home Assistant.

### Manual

1. Download the `mattress_tracker` folder from `custom_components/` in this repository.
2. Copy the folder to your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Mattress Tracker**.
3. Follow the configuration flow:
   - **Mattress Name**: A friendly name for your mattress (e.g., "Master Bedroom Mattress").
   - **Side 1 Name**: The label for one side (default: "Side A").
   - **Side 2 Name**: The label for the other side (default: "Side B").

## Lovelace Card

The Mattress Tracker integration includes a custom Lovelace card to visualize your mattress maintenance status and easily record flips and rotations.

### Installation

1. Download `mattress-tracker-card.js` from this repository and place it in your Home Assistant `config/www/` directory.
2. Add the resource to your Home Assistant:
   - Go to **Settings** > **Dashboards**.
   - Click the three dots in the top right and select **Resources**.
   - Click **Add Resource**.
   - Enter `/local/mattress-tracker-card.js` for the URL and select **JavaScript Module** as the resource type.

### Configuration

Add the card to your dashboard using the following configuration:

```yaml
type: custom:mattress-tracker-card
title: Master Bedroom Mattress
mattress_id: master_bedroom  # The slugified name of your mattress
rotation_limit_months: 6     # Optional: defaults to 6
```

**Note:** `mattress_id` is the name of your mattress as it appears in entity IDs. For example, if your sensor is `sensor.master_bedroom_last_rotated`, the `mattress_id` is `master_bedroom`.

## Usage

### Entities

Once configured, the integration provides several entities:

- `sensor.<mattress_name>_current_side`: Displays which side is currently up.
- `sensor.<mattress_name>_current_rotation`: Displays the current orientation.
- `sensor.<mattress_name>_last_flipped`: The date the mattress was last flipped.
- `sensor.<mattress_name>_last_rotated`: The date the mattress was last rotated.
- `button.<mattress_name>_flip`: Pressing this toggles the side and updates the last flipped date to today.
- `button.<mattress_name>_rotate`: Pressing this toggles the rotation and updates the last rotated date to today.

### Services

- `mattress_tracker.flip`: Toggles the side and sets the flip date.
  - `device_id`: The ID of the Mattress Tracker device.
  - `date` (Optional): The date of the flip (YYYY-MM-DD). Defaults to today.
- `mattress_tracker.rotate`: Toggles the rotation and sets the rotate date.
  - `device_id`: The ID of the Mattress Tracker device.
  - `date` (Optional): The date of the rotation (YYYY-MM-DD). Defaults to today.
- `mattress_tracker.set_side`: Sets the side and sets the flip date.
  - `device_id`: The ID of the Mattress Tracker device.
  - `side`: The side to set (e.g., "Side A").
  - `date` (Optional): The date of the flip (YYYY-MM-DD). Defaults to today.
- `mattress_tracker.set_rotation`: Sets the rotation and sets the rotate date.
  - `device_id`: The ID of the Mattress Tracker device.
  - `rotation`: The rotation to set ("Top at Head" or "Top at Foot").
  - `date` (Optional): The date of the rotation (YYYY-MM-DD). Defaults to today.

## License

This project is licensed under the MIT License.
