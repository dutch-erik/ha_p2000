"""Coordinator for P2000 integration (v2.1.5)."""

import logging
import time
from datetime import datetime, timedelta, timezone

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class P2000DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching P2000 data periodically (v2.1.5)."""

    def __init__(self, hass, api, api_filter, update_interval: timedelta):
        self.api = api
        self.api_filter = api_filter
        self.last_valid_data = None
        self.last_update_success_time: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name="p2000",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        start = time.time()
        try:
            data = await self.hass.async_add_executor_job(self.api.get_data, self.api_filter)
        except Exception as err:
            _LOGGER.exception("P2000: Unexpected error fetching data: %s", err)
            return self.last_valid_data

        duration = round(time.time() - start, 2)

        if data is None:
            _LOGGER.debug(
                "P2000: No new data (filter=%s) after %.2fs; returning cached.",
                self.api_filter,
                duration,
            )
            return self.last_valid_data

        self.last_valid_data = data
        self.last_update_success_time = datetime.now(timezone.utc)
        _LOGGER.debug(
            "P2000: Updated data in %.2fs: %s",
            duration,
            data.get("melding", "<no message>"),
        )
        return data
