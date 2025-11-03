# HA P2000

Een Home Assistant integratie om P2000 meldingen uit [AlarmeringDroid](https://beta.alarmeringdroid.nl/) te tonen.

## Installatie via HACS

1. Voeg deze repo toe aan HACS als aangepaste opslagplaats:  
   `https://github.com/dutch-erik/ha-p2000`
2. Installeer de integratie "HA P2000".
3. Voeg een sensor toe in `configuration.yaml`:


## Regios (Veiligheidsregios)

```yaml
1: Amsterdam-Amstelland
2: Groningen
3: Noord- en Oost Gelderland
4: Zaanstreek-Waterland
5: Hollands Midden
6: Brabant Noord
7: Friesland
8: Gelderland-Midden
9: Kennemerland
10: Rotterdam-Rijnmond
11: Brabant Zuid-Oost
12: Drenthe
13: Gelderland-Zuid
14: Zuid-Holland Zuid
15: Limburg-Noord
17: IJsselland
18: Utrecht
19: Gooi en Vechtstreek
20: Zeeland
21: Limburg-Zuid
23: Twente
24: Noord-Holland Noord
25: Haaglanden
26: Midden- en West Brabant
27: Flevoland
```
## Diensten
```yaml
1: Politie
2: Brandweer
3: Ambulance
4: KNRM
5: Lifeliner
7: DARES
```
## Voorbeelden
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
```
---
MIT License

Copyright (c) 2025 [dutch-erik]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
