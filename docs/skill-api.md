# Skill API: Inter-Skill RPC

!!! abstract "In a nutshell"
    Skills usually work alone, but sometimes one skill needs to ask another for something, like a client asking a server. `SkillApi` is the bus-based remote procedure call (RPC) mechanism that makes this possible: a skill exposes chosen methods with `@skill_api_method`, and any other skill can call them through a `SkillApi` proxy object. For the base-class reference this material was split from, see [OVOSSkill](ovos-skill.md).

`SkillApi` provides a [messagebus](bus-service.md)-based remote procedure call (RPC) mechanism. Methods decorated with `@skill_api_method` are exposed on the bus. Any other skill (or application) can call them by fetching a `SkillApi` proxy object.

**Source:** `ovos_workshop/skills/api.py`

---

## Overview

The bus message protocol for `SkillApi` has two phases:

1. **Discovery**: the caller emits `<skill_id>.public_api` on the bus. The target skill responds with a dict mapping method names to their bus message type and docstring.


2. **Call**: the caller emits a `Message` of the method's registered type with `{"args": [...], "kwargs": {...}}`. The target skill responds with `{"result": <return value>}`.

Return values must be JSON-serializable. Standard Python builtins (`str`, `int`, `list`, `dict`, `None`, `bool`) work. Custom classes are not supported.

---

## `@skill_api_method` Decorator

`skill_api_method`, defined in `ovos_workshop/decorators/__init__.py`

Tag a skill method as part of the public API. The decorator sets `func.api_method = True`. During skill initialization `OVOSSkill` discovers all methods with this attribute and registers a bus listener for each one at `<skill_id>.<method_name>`.

```python
from ovos_workshop.decorators import skill_api_method

class MySkill(OVOSSkill):

    @skill_api_method
    def get_temperature(self, city: str) -> float:
        """Return the current temperature for the given city."""
        return self._fetch_temperature(city)

```

---

## `SkillApi` Class

`SkillApi`, defined in `ovos_workshop/skills/api.py`

### Setup

Before calling `SkillApi.get()`, register the bus client once during skill initialization:

```python
from ovos_workshop.skills.api import SkillApi

SkillApi.connect_bus(self.bus)

```

### `SkillApi.get(skill, api_timeout=3)`

Fetches the public API for the given skill and returns a proxy object.

| Parameter | Description |
|---|---|
| `skill` | The `skill_id` of the target skill |
| `api_timeout` | Seconds to wait for each remote method call (default `3`) |

Returns `None` if the skill is not running or exposes no API methods. Raises `RuntimeError` if `SkillApi.bus` has not been set.

The proxy object has one attribute per exposed method. Calling `proxy.method_name(*args, **kwargs)` emits the corresponding bus message and returns the `result` field of the response. Returns `None` on timeout.

---

## Bus Message Protocol

### Discovery

**Request:** `<skill_id>.public_api` (no data)

**Response:** `<skill_id>.public_api` with data:

```json
{
  "get_temperature": {
    "help": "Return the current temperature for the given city.",
    "type": "my-weather-skill.get_temperature"
  }
}

```

### Method Call

**Request:** `my-weather-skill.get_temperature` with data:

```json
{"args": ["London"], "kwargs": {}}

```

**Response:** same message type with data:

```json
{"result": 18.5}

```

---

## Full Example

### Exposing methods (server skill)

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.decorators import skill_api_method


class WeatherSkill(OVOSSkill):

    @skill_api_method
    def get_temperature(self, city: str) -> float:
        """Return the current temperature in Celsius for the given city."""
        # … real implementation …
        return 18.5

    @skill_api_method
    def get_forecast(self, city: str, days: int = 3) -> list:
        """Return a weather forecast list for the given city."""
        return [{"day": i, "condition": "sunny"} for i in range(days)]

```

### Calling methods (client skill)

```python
from ovos_workshop.skills.ovos import OVOSSkill
from ovos_workshop.skills.api import SkillApi


class MyClientSkill(OVOSSkill):

    def initialize(self):
        SkillApi.connect_bus(self.bus)

    def handle_ask_weather(self, message):
        weather_api = SkillApi.get("my-weather-skill.author")
        if weather_api is None:
            self.speak("Weather skill is not available.")
            return

        temp = weather_api.get_temperature("London")
        if temp is None:
            self.speak("No response from weather skill.")
            return

        self.speak(f"It is {temp} degrees in London.")

```

---

## Limitations

- Return values must be JSON-serializable.


- The target skill must be running when `SkillApi.get()` is called. It emits a live bus message.


- Method calls time out after `api_timeout` seconds (default `3`). The caller receives `None` on timeout.


- `SkillApi.get()` returns `None` (not an exception) if the target skill is absent or unresponsive.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Skill Classes](skill-classes.md)
**Related:** [OVOSSkill](ovos-skill.md) · [Decorators](decorators.md) · [ovos-workshop Documentation](workshop-overview.md) · [Session Aware Skills](session.md)
