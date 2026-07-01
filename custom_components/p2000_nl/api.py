"""P2000 API wrapper with defensive parsing and retries."""

import json
import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)


class P2000Api:
    """P2000 API client with retry support."""

    # Note: the remote API expects JSON appended to the URL path.
    url = "https://beta.alarmeringdroid.nl/api2/find/"

    def __init__(self) -> None:
        self.session = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _request(self, api_filter: dict[str, Any]) -> dict[str, Any] | None:
        try:
            payload = json.dumps(api_filter, ensure_ascii=False)
        except (TypeError, ValueError) as err:
            _LOGGER.error("P2000: API filter not serializable: %s", err)
            return None
        try:
            response = self.session.get(
                self.url + payload,
                timeout=10,
                allow_redirects=False,
                verify=True,
            )
            response.raise_for_status()
            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug("P2000 API response (truncated): %s", response.text[:1000])
            result: dict[str, Any] = response.json()
            return result
        except requests.exceptions.RequestException as err:
            _LOGGER.error("P2000: Error fetching API: %s", err)
            return None
        except ValueError as err:
            _LOGGER.error("P2000: Error parsing API JSON: %s", err)
            return None

    def get_data(self, api_filter: dict[str, Any]) -> dict[str, Any] | None:
        """
        Fetch data and apply optional keyword filter.

        CONF_MELDING supports multiple keywords; ALL must be present in
        either 'tekstmelding' or 'melding' for a result to match.
        Uses 'tekstmelding' preferably for search/filtering.
        """
        raw = self._request(api_filter)
        if not raw:
            return None

        # Normalise melding_filters to a list of lowercase strings.
        melding_filter_raw = api_filter.get("melding")
        if melding_filter_raw:
            if isinstance(melding_filter_raw, (list, tuple)):
                melding_filters = [str(kw).strip().lower() for kw in melding_filter_raw if kw]
            else:
                melding_filters = [str(melding_filter_raw).strip().lower()]
            melding_filters = [kw for kw in melding_filters if kw]
        else:
            melding_filters = []

        meldingen = raw.get("meldingen") or []

        if melding_filters:
            filtered = []
            for m in meldingen:
                # Prefer tekstmelding (clean human-readable field), fall back to melding.
                text = m.get("tekstmelding") or m.get("melding")
                if not isinstance(text, str):
                    continue
                text_lower = text.lower()
                # ALL keywords must be present (AND logic).
                if all(kw in text_lower for kw in melding_filters):
                    filtered.append(m)
            meldingen = filtered

        if not meldingen:
            return None

        # Get the diensten filter if set
        diensten_filter = api_filter.get("diensten")
        if diensten_filter and not isinstance(diensten_filter, list):
            diensten_filter = [str(diensten_filter)]
        elif diensten_filter:
            diensten_filter = [str(d) for d in diensten_filter]

        # Find the best matching melding:
        # If a diensten filter is set and the main melding's dienstid does not
        # match, check subitems for a match and promote that subitem as the
        # result (keeping the parent's subitems for context).
        result: dict[str, Any] = meldingen[0]

        if diensten_filter:
            main_dienstid = str(result.get("dienstid", ""))
            if main_dienstid not in diensten_filter:
                # Look in subitems for a matching dienst
                subitems = result.get("subitems") or []
                for subitem in subitems:
                    if str(subitem.get("dienstid", "")) in diensten_filter:
                        # Promote subitem to result, keep subitems for context
                        promoted = dict(subitem)
                        promoted["subitems"] = subitems
                        result = promoted
                        _LOGGER.debug(
                            "P2000: promoted subitem dienstid=%s as main result",
                            promoted.get("dienstid"),
                        )
                        break

        # Normalise location keys (lat/lon → latitude/longitude)
        result["latitude"] = result.pop("lat", result.get("latitude"))
        result["longitude"] = result.pop("lon", result.get("longitude"))
        return result
