# Writing PHAL Plugins

!!! abstract "In a nutshell"
    This section teaches you how to write your own PHAL (or AdminPHAL) plugin: which
    base class to subclass, what the constructor does for you, how to register the
    entry point, and how to test the result without a running OVOS stack.

## Base class

```python
from ovos_plugin_manager.templates.phal import PHALPlugin

class MyHardwarePlugin(PHALPlugin):
    def __init__(self, bus=None, name="MyHardwarePlugin", config=None):
        super().__init__(bus=bus, name=name, config=config)
        # hardware setup
        self.bus.on("mycroft.stop", self.handle_stop)

    def handle_stop(self, message):
        pass  # respond to bus events

    def shutdown(self):
        super().shutdown()  # unregisters the base enclosure handlers
        pass  # clean up hardware

```

The base class (`PHALPlugin`) is a `threading.Thread`. Key points:

- Stores `self.bus`, `self.config` and `self.name`. There is **no** `self.skill_id`
  attribute. When it emits events it derives a per-plugin id of the form
  `ovos.PHAL.<name>`.


- `PHALPlugin` is a `Thread`, and its `__init__` calls `self.start()` on its last line.
  Instantiating a plugin already runs its thread.

  Register your own bus handlers **after** `super().__init__()`, not before: `self.bus` is
  assigned inside that call, so there is nothing to register on until it returns.

  The default `run()` is a no-op, so for most plugins the started thread does nothing and
  the ordering does not bite. If you override `run()`, it can begin executing before your
  post-`super()` setup finishes — set anything `run()` depends on before you call
  `super().__init__()`, or have `run()` wait for it.


- It auto-registers a large set of legacy enclosure (`enclosure.eyes.*`,
  `enclosure.mouth.*`) and `recognizer_loop:*` bus handlers. Override the matching
  `on_*` methods to react to them. Call `super().shutdown()` to unregister them.

!!! note "Hardware-interface ABCs live in `ovos-hardware-helpers`"
    The abstract base classes that hardware PHAL plugins implement,
    `AbstractLed`, `AbstractFan`, and `AbstractSwitches` (plus a suite of ready-made
    LED animations) live in the
    [`ovos-hardware-helpers`](https://github.com/OpenVoiceOS/ovos-hardware-helpers)
    library. Subclass them there when writing a hardware PHAL plugin. See
    [Building Hardware on OVOS](hardware-integrators.md#writing-your-own-hardware-driver-abstractled-abstractswitches)
    for a worked example.

## Methods you can override

`PHALPlugin` has no `@abstractmethod`: every hook is a `pass`-bodied no-op, so a plugin
that overrides nothing still loads and runs, it just does nothing. The signatures that
matter in practice:

```python
from typing import Optional

from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.phal import PHALPlugin


class MyHardwarePlugin(PHALPlugin):

    def __init__(self, bus=None, name="", config=None):
        """Called before self.start() runs the thread. See 'Lifecycle' below
        for what must happen here vs. in run()."""
        super().__init__(bus=bus, name=name, config=config)

    def run(self):
        """Thread body (PHALPlugin subclasses threading.Thread). Optional:
        most plugins do all their work in bus handlers and leave this empty."""

    def on_record_begin(self, message: Optional[Message] = None):
        """Listening started."""

    def on_record_end(self, message: Optional[Message] = None):
        """Listening ended."""

    def on_audio_output_start(self, message: Optional[Message] = None):
        """Speaking started."""

    def on_audio_output_end(self, message: Optional[Message] = None):
        """Speaking ended."""

    def shutdown(self):
        """Clean teardown. Call super().shutdown() first to unregister the
        base class's enclosure/recognizer_loop handlers, then release hardware."""
        super().shutdown()
```

The full handler list (`on_eyes_*`, `on_display*`, `on_viseme*`, `on_system_*`, ...)
lives in `ovos_plugin_manager.templates.phal.PHALPlugin` — override only the ones your
hardware actually implements. `emit(msg_type, msg_data=None)` is a convenience the base
class provides for the common case: it emits `Message(f"ovos.PHAL.{self.name}.{msg_type}",
msg_data)` on `self.bus`.

## Validator

Controls whether the plugin is auto-enabled:

```python
from ovos_plugin_manager.templates.phal import PHALPlugin, PHALValidator

class MyValidator(PHALValidator):
    @staticmethod
    def validate(config=None) -> bool:
        """Return True if hardware is present and plugin should load."""
        try:
            import smbus
            smbus.SMBus(1).read_byte(0x1a)
            return True
        except Exception:
            return False

class MyHardwarePlugin(PHALPlugin):
    validator = MyValidator

```

For admin plugins, the validator runs **after** the explicit `enabled: true` check.

## Entry points

**User PHAL plugin:**

```toml

# pyproject.toml
[project.entry-points."opm.phal"]
my-phal-plugin = "my_package:MyHardwarePlugin"

```

**Admin PHAL plugin:**

```toml
[project.entry-points."opm.phal.admin"]
my-admin-phal-plugin = "my_package:MyAdminPlugin"

```

**Dual registration** (plugin can run as either user or admin. The service that has the
plugin name in its config section loads it. The other skips it):

```toml
[project.entry-points."opm.phal"]
my-phal-plugin = "my_package:MyPlugin"

[project.entry-points."opm.phal.admin"]
my-phal-plugin = "my_package:MyPlugin"

```

Each group has a parallel `.config` group (`opm.phal.config` / `opm.phal.admin.config`)
where a plugin can register a dict of config metadata for installers and GUIs:

```toml
[project.entry-points."opm.phal.config"]
my-phal-plugin = "my_package:MY_PLUGIN_CONFIG"
```

It is optional. Add it once the plugin has settings worth advertising.

## Plugin configuration

```json
{
  "PHAL": {
    "my-phal-plugin": {
      "enabled": true,
      "i2c_bus": 1,
      "brightness": 80
    }
  }
}

```

```python
class MyPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, config=config)
        self.brightness = self.config.get("brightness", 100)

```

## Lifecycle

- Set up bus listeners in `__init__`, after the `super().__init__()` call that creates
  `self.bus`


- Provide a `shutdown()` method for clean teardown


- No hot-reload. Configuration changes require restarting the PHAL service

## Minimal complete example

A plugin that reads a temperature sensor and reports it over the bus, with a validator
that skips the plugin when the sensor isn't present.

**Project layout:**

```
ovos-PHAL-plugin-mysensor/
├── pyproject.toml
└── ovos_PHAL_plugin_mysensor/
    └── __init__.py
```

**`ovos_PHAL_plugin_mysensor/__init__.py`:**

```python
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.phal import PHALPlugin, PHALValidator


class MySensorValidator(PHALValidator):
    @staticmethod
    def validate(config: dict = None) -> bool:
        try:
            import smbus
            smbus.SMBus(1).read_byte(0x1a)
            return True
        except Exception:
            return False


class MySensorPlugin(PHALPlugin):
    validator = MySensorValidator

    def __init__(self, bus=None, name="ovos-PHAL-plugin-mysensor", config=None):
        super().__init__(bus=bus, name=name, config=config)
        self.poll_interval = self.config.get("poll_interval", 60)
        self.bus.on("mysensor.read", self.handle_read_request)

    def handle_read_request(self, message: Message):
        temp_c = self._read_sensor()
        self.emit("temperature", {"celsius": temp_c})

    def _read_sensor(self) -> float:
        import smbus
        return smbus.SMBus(1).read_byte(0x1a) / 2.0

    def shutdown(self):
        self.bus.remove("mysensor.read", self.handle_read_request)
        super().shutdown()
```

**`pyproject.toml`**:

```toml
[project]
name = "ovos-PHAL-plugin-mysensor"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.phal"]
ovos-PHAL-plugin-mysensor = "ovos_PHAL_plugin_mysensor:MySensorPlugin"
```

## Unit-testing without OVOS

`PHALPlugin.__init__` starts the thread and connects to the real bus by default, so a
unit test passes an explicit `FakeBus` and, for hardware plugins, monkeypatches the
hardware call:

```python
from ovos_utils.fakebus import FakeBus

from ovos_PHAL_plugin_mysensor import MySensorPlugin


def test_read_emits_temperature(monkeypatch):
    monkeypatch.setattr(MySensorPlugin, "_read_sensor", lambda self: 21.5)
    bus = FakeBus()
    plugin = MySensorPlugin(bus=bus, config={})
    received = []
    bus.on("ovos.PHAL.ovos-PHAL-plugin-mysensor.temperature",
           lambda msg: received.append(msg.data))

    plugin.handle_read_request(message=None)

    assert received == [{"celsius": 21.5}]
    plugin.shutdown()
```

Test the validator separately, as a plain static call with no plugin instance:

```python
from ovos_PHAL_plugin_mysensor import MySensorValidator

assert MySensorValidator.validate({"enabled": True}) in (True, False)  # depends on hardware
```

## Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.phal import find_phal_plugins
print(find_phal_plugins())
# {'ovos-PHAL-plugin-mysensor': <class 'ovos_PHAL_plugin_mysensor.MySensorPlugin'>}
```

Admin plugins use `find_admin_plugins()` from the same module instead.

## Publish checklist

1. The class subclasses `PHALPlugin` (or `AdminPlugin` for a privileged plugin) and does
   not block in `__init__` — heavy setup goes in `run()` or lazily on first use.
2. The entry-point group in `pyproject.toml` matches the intended service: `opm.phal`
   for user-space, `opm.phal.admin` for root-privilege hardware access.
3. `__init__` accepts `bus=None, name="", config=None` and works with an empty config.
4. A `validator` is set whenever the plugin depends on hardware that may not be
   present, so the service can silently skip it instead of crashing.
5. `shutdown()` calls `super().shutdown()` and releases any hardware resources the
   plugin's own `__init__`/`run()` acquired.
6. Unit tests exercise the plugin directly with a `FakeBus`, with no OVOS services
   running.
7. `find_phal_plugins()` (or `find_admin_plugins()`) discovers the installed plugin
   under the expected name.

---
**Read next:** [PHAL — Platform/Hardware Abstraction Layer](phal.md) · [Building Hardware on OVOS](hardware-integrators.md)
**Related:** [MessageBus Service](bus-service.md) · [Security & Trust Model](security-model.md) · [Choosing Between PHAL and a Skill](phal.md#choosing-between-phal-and-a-skill)
