"""P2000 API wrapper with defensive parsing and retries."""

import json
import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)

# urllib3 logs its own raw retry attempts (connection/read timeouts) at
# WARNING level, including the full request URL. Those messages are cryptic
# and duplicate what P2000Api already reports through _LOGGER, and they fire
# once per sensor per failed poll — with several sensors configured this
# floods the HA log with near-identical noise. We handle and report
# connectivity issues ourselves (see _request below), so silence urllib3's
# own chatter and only let real errors through.
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


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
        # Tracks whether the previous poll failed, so we only log a WARNING
        # on the first failure of a streak and an INFO once it recovers —
        # instead of repeating the same warning on every single poll.
        self._last_poll_failed = False

    def _log_failure(self, message: str, *args: Any) -> None:
        if not self._last_poll_failed:
            _LOGGER.warning(message, *args)
            self._last_poll_failed = True
        else:
            _LOGGER.debug(message, *args)

    def _reset_failure_state(self) -> None:
        self._last_poll_failed = False

    def _request(self, api_filter: dict[str, Any]) -> dict[str, Any] | None:
        try:
            payload = json.dumps(api_filter, ensure_ascii=False)
        except (TypeError, ValueError) as err:
            _LOGGER.error("P2000: filter could not be encoded: %s", err)
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
            self._reset_failure_state()
            return result
        except requests.exceptions.Timeout:
            self._log_failure(
                "P2000: AlarmeringDroid did not respond in time (filter=%s); "
                "using last known data.",
                api_filter,
            )
            return None
        except requests.exceptions.RequestException as err:
            self._log_failure(
                "P2000: could not reach AlarmeringDroid (filter=%s): %s",
                api_filter,
                err,
            )
            return None
        except ValueError as err:
            _LOGGER.error("P2000: could not parse AlarmeringDroid response: %s", err)
            return None

    def get_data(self, api_filter: dict[str, Any]) -> dict[str, Any] | None:
        """
        Fetch data and apply optional keyword and GRIP filters.

        CONF_MELDING supports multiple keywords; ALL must be present in
        either 'tekstmelding' or 'melding' for a result to match.
        Uses 'tekstmelding' preferably for search/filtering.

        CONF_GRIP (grip_min) is a local-only filter: the remote API doesn't
        support it, so it's stripped from the outgoing request and applied
        client-side. Only meldingen with a GRIP level >= grip_min are kept.
        """
        # grip_min is a local-only filter, never send it to the remote API.
        remote_filter = {k: v for k, v in api_filter.items() if k != "grip_min"}
        raw = self._request(remote_filter)
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

        # Local GRIP filter: keep only meldingen with grip >= grip_min.
        grip_min_raw = api_filter.get("grip_min")
        if grip_min_raw:
            try:
                grip_min = int(grip_min_raw)
            except (TypeError, ValueError):
                grip_min = None
            if grip_min:
                filtered = []
                for m in meldingen:
                    try:
                        grip_val = int(m.get("grip") or 0)
                    except (TypeError, ValueError):
                        grip_val = 0
                    if grip_val >= grip_min:
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
        # result. The promoted item's "subitems" becomes the original main
        # melding plus all *other* subitems — it must not include itself.
        result: dict[str, Any] = meldingen[0]

        if diensten_filter:
            main_dienstid = str(result.get("dienstid", ""))
            if main_dienstid not in diensten_filter:
                subitems = result.get("subitems") or []
                for idx, subitem in enumerate(subitems):
                    if str(subitem.get("dienstid", "")) in diensten_filter:
                        promoted = dict(subitem)
                        original_main = {
                            k: v for k, v in result.items() if k != "subitems"
                        }
                        siblings = [original_main] + [
                            s for j, s in enumerate(subitems) if j != idx
                        ]
                        promoted["subitems"] = siblings
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
