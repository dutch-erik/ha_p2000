import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)

class P2000Api:
    """Wrapper rond de P2000 API."""

    url = "https://beta.alarmeringdroid.nl/api2/find/"

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _request(self, api_filter: dict) -> dict | None:
        """Voer API-aanvraag uit en geef JSON-data terug of None."""
        try:
            response = self.session.get(
                self.url + json.dumps(api_filter),
                timeout=5,
                allow_redirects=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            _LOGGER.warning("Timeout bij ophalen data van %s met filter: %s", self.url, api_filter)
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Fout bij API-aanvraag: %s", err)
            return None

    def _filter_data(self, data: dict, melding_filter: str | None) -> dict | None:
        """Filter ruwe P2000 data."""
        meldingen = data.get("meldingen", [])
        if not meldingen:
            _LOGGER.debug("Geen meldingen ontvangen.")
            return None

        if melding_filter:
            meldingen = [
                m for m in meldingen
                if melding_filter.lower() in m.get("melding", "").lower()
            ]

        if not meldingen:
            _LOGGER.debug("Geen meldingen voldeden aan de filter '%s'", melding_filter)
            return None

        result = meldingen[0]
        result["latitude"] = result.pop("lat", None)
        result["longitude"] = result.pop("lon", None)
        return result

    def get_data(self, api_filter: dict) -> dict | None:
        """Haal volledige en gefilterde data op."""
        raw = self._request(api_filter)
        if not raw:
            return None
        melding_filter = api_filter.get("melding")
        return self._filter_data(raw, melding_filter)
