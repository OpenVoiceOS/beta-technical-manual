# Microphone Plugin Development

!!! abstract "In a nutshell"
    This page is the tutorial for building your own microphone plugin: the `Microphone` base class, the entry point that makes a plugin installable, and how to test and use it standalone. Looking for a plugin to use instead of writing one? Go to [Microphone Plugins](mic-plugins.md).

## Technical Explanation

OVOS uses a plugin architecture to decouple the audio input system from the rest of the voice stack. Microphone plugins implement a common interface, making it easy to swap between different audio sources or backends without changing application code.

### The Microphone Interface

All microphone plugins inherit from the `Microphone` dataclass found in `ovos_plugin_manager.templates.microphone`.

```python
@dataclass
class Microphone:
    sample_rate: int = 16000
    sample_width: int = 2
    sample_channels: int = 1
    chunk_size: int = 4096

    @property
    def frames_per_chunk(self) -> int:
        return self.chunk_size // (self.sample_width * self.sample_channels)

    @property
    def seconds_per_chunk(self) -> float:
        return self.frames_per_chunk / self.sample_rate

    @abc.abstractmethod
    def start(self):
        """Initialize the microphone and start recording."""

    @abc.abstractmethod
    def read_chunk(self) -> Optional[bytes]:
        """Read a single chunk of audio data from the microphone."""

    @abc.abstractmethod
    def stop(self):
        """Stop recording and release any resources."""

```

`read_chunk` returns raw little-endian PCM bytes of `chunk_size` length. The default
format (16 kHz, 16-bit, mono) is what the listener expects downstream.

## Creating Your Own Plugin

To create a new microphone plugin, subclass the `Microphone` dataclass and implement its
three abstract methods: `start()`, `read_chunk() -> Optional[bytes]`, and `stop()`.

### 1. A minimal working plugin

Project layout:

```
ovos-microphone-plugin-mydevice/
├── pyproject.toml
└── ovos_microphone_plugin_mydevice/
    └── __init__.py
```

`ovos_microphone_plugin_mydevice/__init__.py`:

```python
from typing import Optional

from ovos_plugin_manager.templates.microphone import Microphone


class MyCustomMic(Microphone):
    def __init__(self, sample_rate=16000, sample_width=2, sample_channels=1, chunk_size=4096):
        super().__init__(sample_rate, sample_width, sample_channels, chunk_size)
        self.device = None

    def start(self):
        # Open your audio device here
        self.device = open_my_device()

    def read_chunk(self) -> Optional[bytes]:
        # Return raw PCM bytes, chunk_size long
        return self.device.read(self.chunk_size)

    def stop(self):
        # Close the device
        if self.device:
            self.device.close()

```

### 2. Registration

`pyproject.toml`. The entry point is what makes it a plugin. The group must be
`opm.microphone`, and the entry-point name (left of `=`) is the string users put in their
`mycroft.conf`:

```toml
[project]
name = "ovos-microphone-plugin-mydevice"
version = "0.1.0"
dependencies = ["ovos-plugin-manager"]

[project.entry-points."opm.microphone"]
ovos-microphone-plugin-mydevice = "ovos_microphone_plugin_mydevice:MyCustomMic"

```

There is a parallel `opm.microphone.config` group for a dict of config metadata used by
installers and GUIs. It is optional. Add it once the plugin has settings worth
advertising.

> 💡 The legacy alias `ovos.plugin.microphone` is still accepted by `ovos-plugin-manager`, but new plugins should register under `opm.microphone`.

### 3. Test it without OVOS

`Microphone` is a plain dataclass with no messagebus connection, so a unit test needs no
running OVOS stack:

```python
from ovos_microphone_plugin_mydevice import MyCustomMic

mic = MyCustomMic()
mic.start()
try:
    chunk = mic.read_chunk()
    assert chunk is None or len(chunk) == mic.chunk_size
finally:
    mic.stop()
```

### 4. Verify discovery

After `pip install -e .`:

```python
from ovos_plugin_manager.microphone import find_microphone_plugins

print(find_microphone_plugins())
# {'ovos-microphone-plugin-mydevice': <class '...MyCustomMic'>}
```

`load_microphone_plugin(name)` returns the same uninstantiated class for one plugin name.
You construct it yourself with your config dict.

### 5. Checklist before you publish

1. The class subclasses `Microphone` and implements `start`, `read_chunk`, and `stop`.
2. `read_chunk` returns raw little-endian PCM bytes of `chunk_size` length, or `None`.
3. The entry-point group in `pyproject.toml` is `opm.microphone`.
4. Unit tests exercise `start`/`read_chunk`/`stop` directly, with no OVOS services running.
5. `find_microphone_plugins()` discovers the installed plugin under the expected name.

## Standalone Usage

You can use microphone plugins independently of the full OVOS stack:

```python
from ovos_plugin_manager.microphone import find_microphone_plugins

# Find and load the plugin
plugins = find_microphone_plugins()
mic_class = plugins.get("ovos-microphone-plugin-alsa")
if mic_class is None:
    raise RuntimeError("ovos-microphone-plugin-alsa is not installed")
mic = mic_class()

mic.start()
try:
    while True:
        chunk = mic.read_chunk()
        if chunk:
            # Process your audio data here
            print(f"Captured {len(chunk)} bytes")
finally:
    mic.stop()

```

## Tips & Caveats

- **Performance**: For best results on Linux, the ALSA plugin typically provides the lowest latency.


- **Cross-platform development**: Use the `sounddevice` or `files` plugin when developing on non-Linux systems.


- **Testing**: The `files` plugin is ideal for automated testing environments where live input isn't available.


---
**Read next:** [Microphone Plugins](mic-plugins.md)
**Related:** [Wake-word Plugin Development](wake-word-plugin-development.md) · [Writing an STT Plugin](stt-plugin-development.md) · [Plugin Manager](plugin-manager.md)
