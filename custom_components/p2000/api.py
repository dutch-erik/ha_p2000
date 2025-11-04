import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)

class P2000Api:
    """P2000 API-wrapper."""

    url = "https://beta.alarmeringdroid.nl/api2/find/"

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _request(self, api_filter: dict) -> dict | None:
        try:
            response = self.session.get(
                self.url + json.dumps(api_filter),
                timeout=5,
                allow_redirects=False,
            )
            response.raise_for_status()
            _LOGGER.debug("API response: %s", response.text)
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Fout bij API-aanvraag: %s", err)
            return None

    def get_data(self, api_filter: dict) -> dict | None:
        raw = self._request(api_filter)
        if not raw:
            return None

        melding_filter = api_filter.get("melding")
        meldingen = raw.get("meldingen", [])

        if melding_filter:
            meldingen = [
                m for m in meldingen
                if melding_filter.lower() in m.get("melding", "").lower()
            ]
            _LOGGER.debug("Aantal meldingen na filter '%s': %d", melding_filter, len(meldingen))

        if not meldingen:
            _LOGGER.debug("Geen meldingen voldeden aan de filter '%s'", melding_filter)
            return None

        result = meldingen[0]
        result["latitude"] = result.pop("lat", None)
        result["longitude"] = result.pop("lon", None)
        return result
