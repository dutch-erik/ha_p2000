import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class P2000DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator die periodiek P2000-data ophaalt."""

    def __init__(self, hass, api, api_filter, update_interval: timedelta):
        self.api = api
        self.api_filter = api_filter
        super().__init__(
            hass,
            _LOGGER,
            name="p2000",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        data = await self.hass.async_add_executor_job(self.api.get_data, self.api_filter)
        if not data:
            raise UpdateFailed("Geen data ontvangen van P2000 API")
        return data
