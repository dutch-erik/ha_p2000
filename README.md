# HA P2000

[![GitHub Release](https://img.shields.io/github/v/release/dutch-erik/ha_p2000)](https://github.com/dutch-erik/ha_p2000/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant integration to display live P2000 emergency alerts from [AlarmeringDroid](https://beta.alarmeringdroid.nl/).

P2000 is the Dutch paging network used by emergency services (ambulance, fire brigade, police, KNRM, and Lifeliner helicopters). This integration polls the AlarmeringDroid API and exposes matching alerts as Home Assistant sensors, allowing you to build automations, notifications, and dashboard cards around them.


## Features

- Live P2000 alerts as Home Assistant sensors
- Filter by region (Veiligheidsregio), municipality (Gemeenten), capcode, service type (Diensten), and keyword
- Multiple keyword filtering with AND logic (all keywords must match)
- Automatic icon based on service type (ambulance, fire truck, helicopter, etc.)
- Sensor state restored after HA restart
- Fully configurable via the UI (no YAML required)
- Options flow: change filters without removing and re-adding the sensor


## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. Search for **HA P2000**
3. Click **Download**
4. Restart Home Assistant

### Manual

1. Download the latest release from [GitHub Releases](https://github.com/dutch-erik/ha_p2000/releases)
2. Copy the `custom_components/p2000/` folder into your HA `custom_components/` directory
3. Restart Home Assistant


## Adding sensors

### Via the UI

1. Go to **Settings → Integrations**
2. Click **+ Add integration** and search for **P2000**
3. Fill in the configuration form (see [Configuration options](#configuration-options) below)
4. Click **Submit** — the sensor appears immediately without a restart

To change filters later, click **Configure** on the integration card.


## Configuration options

| Option | Type | Description |
|---|---|---|
| **Name** | `string` | Unique name for this sensor (required) |
| **Gemeenten** | `string` | Comma-separated municipality names, e.g. `maassluis, rotterdam` (lowercase) |
| **Capcodes** | `string` | Comma-separated P2000 capcodes to filter on, e.g. `1420059, 1400121` |
| **Regios** | `list` | One or more Veiligheidsregio numbers (see [Regios](#regios-nl-veiligheidsregios) below) |
| **Diensten** | `list` | One or more service types (see [Diensten](#diensten) below) |
| **Melding** | `string` | Comma-separated keywords — **all** must be present in the alert text (AND logic), e.g. `MAASSL, reanimatie` |
| **Prio 1 only** | `bool` | When enabled, only show priority 1 alerts |
| **Life** | `bool` | When enabled, only show Lifeliner / trauma helicopter alerts |

> 💡 **Tip:** Use `tekstmelding` for keyword matching — this is the clean, human-readable version of the alert (e.g. "Ambulance met spoed naar Hoogstraat, Maassluis") rather than the raw radio code string.


## Regios NL (Veiligheidsregios)

| # | Regio |
|---|---|
| 1 | Amsterdam-Amstelland |
| 2 | Groningen |
| 3 | Noord- en Oost Gelderland |
| 4 | Zaanstreek-Waterland |
| 5 | Hollands Midden |
| 6 | Brabant Noord |
| 7 | Friesland |
| 8 | Gelderland-Midden |
| 9 | Kennemerland |
| 10 | Rotterdam-Rijnmond |
| 11 | Brabant Zuid-Oost |
| 12 | Drenthe |
| 13 | Gelderland-Zuid |
| 14 | Zuid-Holland Zuid |
| 15 | Limburg-Noord |
| 17 | IJsselland |
| 18 | Utrecht |
| 19 | Gooi en Vechtstreek |
| 20 | Zeeland |
| 21 | Limburg-Zuid |
| 23 | Twente |
| 24 | Noord-Holland Noord |
| 25 | Haaglanden |
| 26 | Midden- en West Brabant |
| 27 | Flevoland |


## Diensten

| # | Dienst | Icon |
|---|---|---|
| 1 | Politie | `mdi:police-badge` |
| 2 | Brandweer | `mdi:fire-truck` |
| 3 | Ambulance | `mdi:ambulance` |
| 4 | KNRM | `mdi:ship` |
| 5 | Lifeliner (Traumaheli) | `mdi:helicopter` |
| 7 | DARES (Dutch Amateur Radio Emergency Service) | `mdi:radio-tower` |


## Sensor attributes

Each P2000 sensor exposes the following attributes:

| Attribute | Description |
|---|---|
| `melding` | Raw alert text (radio code format) |
| `tekstmelding` | Human-readable alert text |
| `dienst` | Service name (e.g. "Ambulance") |
| `dienstid` | Service ID number |
| `regio` | Region name |
| `regioid` | Region ID number |
| `plaats` | City / postal code area |
| `postcode` | Postal code |
| `straat` | Street name |
| `datum` | Date of alert |
| `tijd` | Time of alert |
| `prio1` | `1` if priority 1, otherwise `0` |
| `brandinfo` | Fire incident type (if applicable) |
| `grip` | GRIP level (if applicable) |
| `capcodes` | List of dispatched units with descriptions |
| `capstring` | Formatted string of dispatched units |
| `subitems` | Related alerts (e.g. Lifeliner dispatched alongside Brandweer) |
| `latitude` | GPS latitude (if available) |
| `longitude` | GPS longitude (if available) |
| `filter` | Active filter configuration for this sensor |
| `last_updated` | UTC timestamp of last update |
| `helpers.dienst_id_normalized` | Normalized service ID used for icon selection |
| `helpers.icon_used` | MDI icon currently in use |


## Example automations

### Push notification on any alert in your municipality

```yaml
alias: P2000 melding notificatie
trigger:
  - platform: state
    entity_id: sensor.p2000_maassluis
action:
  - service: notify.mobile_app_your_phone
    data:
      title: >
        {{ state_attr('sensor.p2000_maassluis', 'dienst') }} — Maassluis
      message: >
        {{ state_attr('sensor.p2000_maassluis', 'tekstmelding') }}
        📍 {{ state_attr('sensor.p2000_maassluis', 'straat') }},
        {{ state_attr('sensor.p2000_maassluis', 'plaats') }}
        🕐 {{ state_attr('sensor.p2000_maassluis', 'tijd') }}
      data:
        tag: p2000_maassluis
```

### Priority 1 only — high priority push

```yaml
alias: P2000 Prio 1
trigger:
  - platform: state
    entity_id: sensor.p2000_maassluis
condition:
  - condition: template
    value_template: >
      {{ state_attr('sensor.p2000_maassluis', 'prio1') | int == 1 }}
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "🚨 PRIO 1 — Maassluis"
      message: "{{ states('sensor.p2000_maassluis') }}"
      data:
        priority: high
        ttl: 0
```

### Lifeliner alert with TTS announcement

```yaml
alias: P2000 Lifeliner
trigger:
  - platform: state
    entity_id: sensor.p2000_lifeliner_maassluis
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "🚁 LIFELINER"
      message: >
        {{ state_attr('sensor.p2000_lifeliner_maassluis', 'tekstmelding') }}
      data:
        priority: high
        ttl: 0
  - service: tts.speak
    target:
      entity_id: media_player.your_speaker
    data:
      message: >
        Lifeliner melding:
        {{ state_attr('sensor.p2000_lifeliner_maassluis', 'tekstmelding') }}
```


## Example dashboard card

```yaml
type: markdown
title: >
  {{ state_attr('sensor.p2000_maassluis', 'dienst') | default('P2000') }}
content: >
  ## {{ states('sensor.p2000_maassluis') }}

  📍 {{ state_attr('sensor.p2000_maassluis', 'straat') }}
  {{ state_attr('sensor.p2000_maassluis', 'postcode') }}

  🕐 {{ state_attr('sensor.p2000_maassluis', 'datum') }}
  {{ state_attr('sensor.p2000_maassluis', 'tijd') }}

  📻 {{ state_attr('sensor.p2000_maassluis', 'capstring') }}
```


## Data source

Alert data is provided by the [AlarmeringDroid API](https://beta.alarmeringdroid.nl/). This integration polls the API every minute. The integration is classified as `cloud_polling` — an active internet connection is required.


## Contributing

Pull requests and issues are welcome via [GitHub](https://github.com/dutch-erik/ha_p2000/issues).

For development setup:

```bash
pip install -r requirements-dev.txt

# Lint
ruff check custom_components/p2000/

# Format
ruff format custom_components/p2000/

# Type check
mypy custom_components/p2000/
```


## License

MIT License — see [LICENSE](LICENSE) for details.
