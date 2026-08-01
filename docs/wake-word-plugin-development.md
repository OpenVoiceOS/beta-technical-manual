# Writing a Wake-word Plugin

!!! abstract "In a nutshell"
    This page is the tutorial for building your own wake-word plugin: the `HotWordEngine` base class, its key methods, the entry point that makes a plugin installable, and how to test it. Looking for a plugin to use instead of writing one? Go to [Wake-word Plugins](wake-word-plugins.md).


All wake-word plugins inherit from the `HotWordEngine` base class provided by
`ovos-plugin-manager`.

### The HotWordEngine Interface

This is the actual base class shipped in `ovos_plugin_manager.templates.hotwords`:

```python
class HotWordEngine:
    def __init__(self, key_phrase: str, config: Optional[Dict[str, Any]] = None):
        self.key_phrase = str(key_phrase).lower()
        self.config = config or Configuration().get("hotwords", {}).get(self.key_phrase, {})

    @abc.abstractmethod
    def found_wake_word(self) -> bool:
        """Check if wake word has been found, and reset internal tracking state."""
        raise NotImplementedError()

    def reset(self):
        """Reset the WW engine to prepare for a new detection (optional)."""

    @abc.abstractmethod
    def update(self, chunk: bytes):
        """Update the hotword engine with new audio data."""
        raise NotImplementedError()

    def stop(self):
        """Perform any actions needed to shut down the wake word engine (optional)."""

```

`self.config` is the plugin's own sub-dict from `hotwords.<name>` in `mycroft.conf`,
already resolved by the base `__init__` when a subclass doesn't pass its own `config`.

### Key Methods

- **`found_wake_word()`**: Required (abstract). Returns whether the wake word has been
  detected, and resets any internal tracking of the wake-word state. It takes no audio
  argument: real-time audio only reaches the plugin through `update(chunk)`, on the
  current `dev` contract.
- **`update(chunk)`**: Required (abstract). Processes one raw PCM audio chunk (see the
  audio format contract near the top of this page) and updates the engine's internal
  trigger state.
  Runs once per captured chunk on the mic thread, so it must stay well under the
  per-chunk time budget: do heavy inference work on a background thread and only feed
  results into `update`, the same real-time cadence constraint a
  [streaming STT plugin's `stream_data()`](stt-plugin-development.md#chunk-semantics) runs under.
- **`reset()`**: Optional. Resets internal state to prepare for a new detection. The base
  implementation is a no-op.
- **`stop()`**: Optional. Shuts down the plugin: unloading data, halting external
  processes. The base implementation is a no-op, so an override does not need to call
  `super().stop()`.

### 1. A minimal working plugin

Project layout:

```
ovos-ww-plugin-mymodel/
├── pyproject.toml
└── ovos_ww_plugin_mymodel/
    └── __init__.py
```

`ovos_ww_plugin_mymodel/__init__.py`:

```python
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from threading import Event


class MyWWPlugin(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None):
        super().__init__(key_phrase, config)
        # self.config is the plugin's own sub-dict from `hotwords.<name>` in
        # mycroft.conf — read your plugin-specific settings out of it here
        threshold = self.config.get("sensitivity", 0.5)
        self.detection = Event()
        self.engine = MyWW(key_phrase, threshold=threshold)

    def found_wake_word(self):
        # inference happens via the self.update method
        detected = self.detection.is_set()
        if detected:
            self.detection.clear()
        return detected

    def update(self, chunk):
        if self.engine.found_it(chunk):
            self.detection.set()

    def stop(self):
        self.engine.bye()


# sample valid configuration
MyWWConfig = {
    "hey mycroft": [{"module": "ovos-ww-plugin-mymodel",
                      "sensitivity": 0.5,
                      "display_name": "MyWW",
                      "priority": 70}]
}

```

### 2. Registration

`pyproject.toml`. The entry-point name (left of `=`) is the string users put in the
`hotwords.<name>.module` key of `mycroft.conf`:

```toml
[project]
name = "ovos-ww-plugin-mymodel"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.wake_word"]
ovos-ww-plugin-mymodel = "ovos_ww_plugin_mymodel:MyWWPlugin"

[project.entry-points."opm.wake_word.config"]
ovos-ww-plugin-mymodel.config = "ovos_ww_plugin_mymodel:MyWWConfig"

```

> **Backward Compatibility**: `ovos-plugin-manager` still supports legacy
> `mycroft.plugin.wake_word` entry points, but new plugins should use the `opm.*`
> namespace.

### 3. Test it without OVOS

`HotWordEngine` is a plain class with no messagebus connection, so a unit test needs no
running OVOS stack:

```python
from ovos_ww_plugin_mymodel import MyWWPlugin

ww = MyWWPlugin(key_phrase="hey mycroft", config={"sensitivity": 0.5})
silence_chunk = b"\x00" * 4096
ww.update(silence_chunk)
assert ww.found_wake_word() is False
```

### 4. Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.wakewords import find_wake_word_plugins

print(find_wake_word_plugins())
# {'ovos-ww-plugin-mymodel': <class '...MyWWPlugin'>}
```

`load_wake_word_plugin(name)` returns the same uninstantiated class for one plugin name.
You construct it yourself with a `key_phrase` and config dict.

### 5. Checklist before you publish

1. The class subclasses `HotWordEngine` and implements `found_wake_word() -> bool` and
   `update(chunk)`.
2. `__init__` accepts `key_phrase` and `config=None`, and calls
   `super().__init__(key_phrase, config)` (or otherwise sets `self.key_phrase` and
   `self.config`).
3. `found_wake_word()` takes no arguments and resets its own detection state before
   returning.
4. `update(chunk)` returns promptly; slow inference runs on a background thread.
5. The entry-point group in `pyproject.toml` is `opm.wake_word`, with a matching
   `opm.wake_word.config` entry once the plugin has settings worth advertising in UIs.
6. Unit tests exercise `update`/`found_wake_word` directly, with no OVOS services
   running.
7. `find_wake_word_plugins()` discovers the installed plugin under the expected name.


---
**Read next:** [Wake-word Plugins](wake-word-plugins.md)
**Related:** [Writing an STT Plugin](stt-plugin-development.md) · [Microphone Plugin Development](mic-plugin-development.md) · [Plugin Manager](plugin-manager.md)
