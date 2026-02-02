# Mattress Tracker Card for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Lovelace card to visualize and manage mattress maintenance, including flipping and rotating. This card is designed to work with the [Mattress Tracker integration](https://github.com/lougovsk/ha-mattress-tracker).

## Features

- **Current Status**: Displays which side is up and the current orientation.
- **Action Buttons**: Quickly record a flip or rotation directly from the dashboard.
- **Rotation Progress**: A dynamic progress bar showing time elapsed since the last rotation.
- **Visual Overdue Alert**: The progress bar turns **red** and an alert appears when the mattress is overdue for rotation (default 6 months).
- **Configurable**: Customize the title and the rotation limit months.

## Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Paste `https://github.com/lougovsk/ha-mattress-tracker-card` (or your repo URL) into the URL field.
4. Select **Lovelace** (or Plugin) as the category and click **Add**.
5. Find **Mattress Tracker Card** in the HACS list and click **Download**.
6. Refresh your browser.

### Manual

1. Download `mattress-tracker-card.js` from this repository.
2. Copy it to your Home Assistant `config/www/` directory.
3. Add the resource to your Home Assistant:
   - Go to **Settings** > **Dashboards**.
   - Click the three dots in the top right and select **Resources**.
   - Click **Add Resource**.
   - Enter `/local/mattress-tracker-card.js` for the URL and select **JavaScript Module** as the resource type.

## Configuration

Add the card to your dashboard using the following configuration:

```yaml
type: custom:mattress-tracker-card
title: Master Bedroom Mattress
mattress_id: master_bedroom  # The slugified name of your mattress
rotation_limit_months: 6     # Optional: defaults to 6
```

**Note:** `mattress_id` is the prefix used in your entity IDs. For example, if your sensor is `sensor.master_bedroom_last_rotated`, the `mattress_id` is `master_bedroom`.

## License

This project is licensed under the MIT License.
