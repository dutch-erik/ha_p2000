# HA P2000

Een Home Assistant integratie om P2000 meldingen uit [AlarmeringDroid](https://beta.alarmeringdroid.nl/) te tonen.

## Installatie via HACS

1. Voeg deze repo toe aan HACS als aangepaste opslagplaats:  
   `https://github.com/dutch-erik/ha-p2000`
2. Installeer de integratie "HA P2000".
3. Voeg een sensor toe in `configuration.yaml`:

```yaml
sensor:
  - platform: p2000
    name: p2000_mss
    gemeenten:
      - maassluis

  - platform: p2000
    name: p2000_llrsmss
    icon: mdi:helicopter
    gemeenten:
      - maassluis
    diensten:
      - 5

  - platform: p2000
    name: p2000_haaglanden_mss
    regios:
      - 25
    melding:
      - 'MAASSL'
