async def async_setup_entry(hass, entry, async_add_entities):
    """Set up P2000 via config entry (UI)."""
    conf = entry.data
    name = conf.get(CONF_NAME)
    icon = conf.get(CONF_ICON)
    api_filter = {}

    for prop in [CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS]:
        value = conf.get(prop)
        if value:
            api_filter[prop] = value  # is al lijst

    for prop in [CONF_PRIO1, CONF_LIFE]:
        if conf.get(prop, False):
            api_filter[prop] = "1"

    if CONF_MELDING in conf and conf[CONF_MELDING]:
        melding_values = conf[CONF_MELDING]
        if isinstance(melding_values, list):
            api_filter[CONF_MELDING] = melding_values[0]  # enkel eerste gebruikt

    api = P2000Api()
    coordinator = P2000DataUpdateCoordinator(hass, api, api_filter, SCAN_INTERVAL)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([P2000Sensor(coordinator, name, icon, api_filter)], True)
