# Calling an external API safely: timeouts, spoken errors, and a cache

!!! abstract "In a nutshell"
    You build an `OVOSSkill` that calls a remote HTTP API without ever hanging the skill process, using a request timeout, a spoken-error fallback, and a `file_system` cache.

**When you'd want this:** a skill answers "what's the exchange rate" or similar by hitting a remote HTTP API, and needs to (a) never hang the skill process on a slow/dead endpoint, and (b) fail with a spoken sentence instead of a traceback.

!!! note
    This recipe also shows `runtime_requirements`, the declaration a skill uses to state what
    connectivity it needs. See [Runtime Requirements](skill-runtime-requirements.md) for how
    the loader uses it. New skills don't need it for the timeout/cache/spoken-error
    pattern below, which works regardless.

```python
import json
import time

import requests
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

API_URL = "https://api.example.com/rate"
CACHE_TTL = 3600  # seconds


class ExchangeRateSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        # declares that this skill needs a live network connection.
        # only gates loading if "skills.use_deferred_loading" is enabled.
        return RuntimeRequirements(
            network_before_load=True,
            internet_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=False,
            no_network_fallback=False,
        )

    def _cache_path(self):
        return self.file_system.path + "/rate_cache.json"

    def _read_cache(self):
        try:
            with open(self._cache_path()) as f:
                data = json.load(f)
            if time.time() - data["fetched_at"] < CACHE_TTL:
                return data["rate"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
        return None

    def _write_cache(self, rate):
        with open(self._cache_path(), "w") as f:
            json.dump({"rate": rate, "fetched_at": time.time()}, f)

    def _fetch_rate(self):
        cached = self._read_cache()
        if cached is not None:
            return cached
        try:
            resp = requests.get(API_URL, timeout=5)
            resp.raise_for_status()
            rate = resp.json()["rate"]
        except requests.exceptions.Timeout:
            self.speak_dialog("api_timeout")
            return None
        except requests.exceptions.RequestException as e:
            self.log.warning(f"exchange rate API call failed: {e}")
            self.speak_dialog("api_error")
            return None
        self._write_cache(rate)
        return rate

    @intent_handler("exchange_rate.intent")
    def handle_exchange_rate(self, message):
        rate = self._fetch_rate()
        if rate is not None:
            self.speak_dialog("exchange_rate", {"rate": rate})
```

### Moving parts

- `runtime_requirements` (a `@classproperty` you override, returning `RuntimeRequirements(...)`) declares what a skill needs at load time. Its `*_before_load` flags only gate loading when `skills.use_deferred_loading` is enabled in config. With the default config, all skills load unconditionally regardless of this declaration. See [Runtime Requirements](skill-runtime-requirements.md) for the current behavior.
- Always pass `timeout=` to `requests.get`/`.post`. An OVOS skill runs on the shared bus-handling thread pool, and a hung HTTP call can stall other skill callbacks.
- `self.file_system` (a `FileSystemAccess`, exposing `.path`) is a writable, skill-private directory distinct from `settings.json`. It is the right place for a response cache, downloaded assets, or anything larger than a few settings keys.
- Wrap the network call narrowly (`requests.exceptions.Timeout` / `.RequestException`) so a real bug elsewhere in the handler still raises normally instead of being swallowed by a broad `except Exception`.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Runtime Requirements](skill-runtime-requirements.md) · [Control an external device (MQTT)](recipe-mqtt-device-control.md) · [Skill Settings](skill-settings.md)
