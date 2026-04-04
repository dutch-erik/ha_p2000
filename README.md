# HA P2000

[![GitHub Release](https://img.shields.io/github/v/release/dutch-erik/ha_p2000)](https://github.com/dutch-erik/ha_p2000/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant integration for live P2000 emergency alerts, powered by [AlarmeringDroid](https://beta.alarmeringdroid.nl/).

P2000 is the Dutch paging network for emergency services. This integration lets you track alerts in your area and build automations around them, get a push notifications when the fire brigade is dispatched to your street, or a TTS announcement when a Lifeliner is inbound.

## Features

- Live P2000 alerts as HA sensors, polled every minute
- Filter by region, municipality, capcode, service type, or keyword
- Multiple keywords supported with AND logic
- Icon automatically set based on service type
- Sensor state survives HA restarts
- Fully UI-configurable, no YAML needed

## Installation

### Via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dutch-erik&repository=ha_p2000&category=integration)

1. Click **Open HACS Repository on My** above, or search for **HA P2000** in HACS
2. Click **Download** and restart Home Assistant

### Manual

1. Download the latest release from [GitHub Releases](https://github.com/dutch-erik/ha_p2000/releases)
2. Copy `custom_components/p2000/` to your HA `custom_components/` directory
3. Restart Home Assistant

## Setup

[![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=p2000)

Click **Add Integration to My** above, or go to **Settings → Integrations → Add integration → P2000**. Each sensor gets its own filter, you can add multiple sensors, e.g. one for all alerts in your municipality and one for Lifeliners only.

To change a filter later, click **Configure** on the integration card. No restart needed.

## Configuration options

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| **Name** | `string` | ✅ | — | Unique name for this sensor |
| **Gemeenten** | `string` | ❌ | — | Comma-separated municipality names, lowercase, e.g. `maassluis, vlaardingen` |
| **Capcodes** | `string` | ❌ | — | Comma-separated capcodes, e.g. `1420059, 1400121` |
| **Regios** | `list` | ❌ | — | One or more Veiligheidsregio numbers (see [Regios NL](#regios-nl) below) |
| **Diensten** | `list` | ❌ | — | One or more service types (see [Diensten](#diensten) below) |
| **Melding** | `string` | ❌ | — | Keywords that must ALL appear in the alert, e.g. `MAASSL, reanimatie` |
| **Prio 1 only** | `bool` | ❌ | `false` | Only show priority 1 alerts |
| **Life** | `bool` | ❌ | `false` | Only show Lifeliner / trauma helicopter alerts |

> **Tip:** The `tekstmelding` attribute contains the human-readable alert text (e.g. "Ambulance met spoed naar Hoogstraat, Maassluis"). Use this for keyword filtering rather than the raw radio code in `melding`.

> ⚠️ At least one filter (Gemeenten, Capcodes, Regios, Diensten or Melding) is recommended, without any filter the sensor shows alerts from the entire Netherlands.

## Regios NL

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
| 7 | DARES | `mdi:radio-tower` |

## Sensor attributes

| Attribute | Description |
|---|---|
| `melding` | Raw alert text (radio code) |
| `tekstmelding` | Human-readable alert text |
| `dienst` | Service name |
| `dienstid` | Service ID |
| `regio` | Region name |
| `plaats` | City / postal code area |
| `postcode` | Postal code |
| `straat` | Street name |
| `datum` | Date |
| `tijd` | Time |
| `prio1` | `1` if priority 1 |
| `brandinfo` | Fire incident type (if applicable) |
| `grip` | GRIP level (if applicable) |
| `capcodes` | Dispatched units |
| `capstring` | Dispatched units as formatted string |
| `subitems` | Related alerts (e.g. Lifeliner dispatched to same incident) |
| `latitude` / `longitude` | GPS coordinates (if available) |
| `last_updated` | UTC timestamp of last update |

## Example automations

### Alert notification

```yaml
alias: P2000 notificatie
trigger:
  - platform: state
    entity_id: sensor.p2000_mijn_sensor
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "{{ state_attr('sensor.p2000_mijn_sensor', 'dienst') }}"
      message: >
        {{ state_attr('sensor.p2000_mijn_sensor', 'tekstmelding') }}
        📍 {{ state_attr('sensor.p2000_mijn_sensor', 'straat') }},
        {{ state_attr('sensor.p2000_mijn_sensor', 'plaats') }}
        🕐 {{ state_attr('sensor.p2000_mijn_sensor', 'tijd') }}
```

### Prio 1 only

```yaml
alias: P2000 Prio 1
trigger:
  - platform: state
    entity_id: sensor.p2000_mijn_sensor
condition:
  - condition: template
    value_template: "{{ state_attr('sensor.p2000_mijn_sensor', 'prio1') | int == 1 }}"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "🚨 PRIO 1"
      message: "{{ states('sensor.p2000_mijn_sensor') }}"
      data:
        priority: high
        ttl: 0
```

### Lifeliner with TTS

```yaml
alias: P2000 Lifeliner
trigger:
  - platform: state
    entity_id: sensor.p2000_lifeliner
action:
  - service: tts.speak
    target:
      entity_id: media_player.your_speaker
    data:
      message: "{{ state_attr('sensor.p2000_lifeliner', 'tekstmelding') }}"
```

## Example dashboard card

```yaml
type: markdown
title: "{{ state_attr('sensor.p2000_mijn_sensor', 'dienst') | default('P2000') }}"
content: >
  **{{ state_attr('sensor.p2000_mijn_sensor', 'tekstmelding') }}**

  📍 {{ state_attr('sensor.p2000_mijn_sensor', 'straat') }}
  🕐 {{ state_attr('sensor.p2000_mijn_sensor', 'datum') }} {{ state_attr('sensor.p2000_mijn_sensor', 'tijd') }}

  {{ state_attr('sensor.p2000_mijn_sensor', 'capstring') }}
```

## Data source

Alert data comes from the [AlarmeringDroid API](https://beta.alarmeringdroid.nl/), polled every minute.

## Contributing

Contributions, bug reports, feature requests are welcome. Feel free to open an issue or submit a pull request.
 [GitHub](https://github.com/dutch-erik/ha_p2000/issues)

## License

MIT - see [LICENSE](LICENSE).
