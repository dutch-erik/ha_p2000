import requests
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)

class P2000Api:
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

    def get_data(self, apiFilter):
        try:
            response = self.session.get(
                self.url + json.dumps(apiFilter),
                params={},
                allow_redirects=False,
                timeout=5  # <-- Toegevoegde timeout
            )

            if response.status_code != 200:
                _LOGGER.error("Request failed with status code %s: %s", response.status_code, response.text)
                return None

            data = json.loads(response.content.decode('utf-8'))

            if len(data.get('meldingen', [])) == 0:
                _LOGGER.debug("Geen meldingen ontvangen voor filter: %s", apiFilter)
                return None

            # Filter op melding (optioneel)
            melding_filter = apiFilter.get('melding', None)
            if melding_filter:
                filtered_meldingen = [
                    melding for melding in data['meldingen']
                    if melding_filter.lower() in melding.get('melding', '').lower()
                ]
            else:
                filtered_meldingen = data['meldingen']

            if len(filtered_meldingen) == 0:
                _LOGGER.debug("Geen meldingen voldeden aan de filter '%s'", melding_filter)
                return None

            # Neem de eerste gefilterde melding
            result = filtered_meldingen[0]

            # Herbenoem lat/lon naar latitude/longitude
            result["latitude"] = result.pop("lat", None)
            result["longitude"] = result.pop("lon", None)

            return result

        except requests.exceptions.Timeout:
            _LOGGER.warning("Timeout bij ophalen data van %s met filter: %s", self.url, apiFilter)
            return None
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Fout bij ophalen data van %s: %s", self.url, str(e))
            return None
