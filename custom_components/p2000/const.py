"""Constants for P2000 integration (v2.1.5)."""

DOMAIN = "p2000"

# Configuration keys (strings used in config entries)
CONF_NAME = "name"
CONF_GEMEENTEN = "gemeenten"
CONF_CAPCODES = "capcodes"
CONF_DIENSTEN = "diensten"
CONF_REGIOS = "regios"
CONF_PRIO1 = "prio1"
CONF_LIFE = "life"
CONF_MELDING = "melding"

# Options lists (used in flows)
REGIO_OPTIES = [
    {"value": "1", "label": "Amsterdam-Amstelland"},
    {"value": "2", "label": "Groningen"},
    {"value": "3", "label": "Noord- en Oost Gelderland"},
    {"value": "4", "label": "Zaanstreek-Waterland"},
    {"value": "5", "label": "Hollands Midden"},
    {"value": "6", "label": "Brabant Noord"},
    {"value": "7", "label": "Friesland"},
    {"value": "8", "label": "Gelderland-Midden"},
    {"value": "9", "label": "Kennemerland"},
    {"value": "10", "label": "Rotterdam-Rijnmond"},
    {"value": "11", "label": "Brabant Zuid-Oost"},
    {"value": "12", "label": "Drenthe"},
    {"value": "13", "label": "Gelderland-Zuid"},
    {"value": "14", "label": "Zuid-Holland Zuid"},
    {"value": "15", "label": "Limburg-Noord"},
    {"value": "17", "label": "IJsselland"},
    {"value": "18", "label": "Utrecht"},
    {"value": "19", "label": "Gooi en Vechtstreek"},
    {"value": "20", "label": "Zeeland"},
    {"value": "21", "label": "Limburg-Zuid"},
    {"value": "23", "label": "Twente"},
    {"value": "24", "label": "Noord-Holland Noord"},
    {"value": "25", "label": "Haaglanden"},
    {"value": "26", "label": "Midden- en West Brabant"},
    {"value": "27", "label": "Flevoland"},
]

DIENST_OPTIES = [
    {"value": "1", "label": "Politie"},
    {"value": "2", "label": "Brandweer"},
    {"value": "3", "label": "Ambulance"},
    {"value": "4", "label": "KNRM"},
    {"value": "5", "label": "Lifeliner (Traumaheli)"},
    {"value": "7", "label": "DARES"},
]
