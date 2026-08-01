# Writing a Transformer Plugin

!!! abstract "In a nutshell"
    This page is the tutorial for building your own transformer plugin: how to inherit from
    the right base class, register the entry point, package it, and test it. Looking for a
    plugin to use instead of writing one? Go to [Transformer Plugins](transformer-plugins.md).

## Creating a Plugin

1.  **Inherit** from the base class for your transformer type. All six live in
    `ovos_plugin_manager.templates.transformers`:

    | Base class | Stage | Entry-point group |
    |---|---|---|
    | `UtteranceTransformer` | text, before intent matching | `opm.transformer.text` |
    | `MetadataTransformer` | message context, before intent matching | `opm.transformer.metadata` |
    | `IntentTransformer` | after a match, before the handler runs | `opm.transformer.intent` |
    | `DialogTransformer` | spoken text, before TTS | `opm.transformer.dialog` |
    | `TTSTransformer` | synthesized audio, after TTS | `opm.transformer.tts` |
    | `AudioTransformer` | captured audio, before STT | `opm.transformer.audio` |

    Every one of them takes `__init__(self, name, priority=50, config=None)`, and **`name` is
    a required positional argument**. Pass your plugin's name as the default, because that
    name is also the key the base class reads your settings under in `mycroft.conf`:

    ```python
    from ovos_plugin_manager.templates.transformers import UtteranceTransformer


    class MyCustomTransformer(UtteranceTransformer):
        def __init__(self, name="my-custom-transformer", priority=50, config=None):
            super().__init__(name, priority, config)

        def transform(self, utterances, context=None):
            return [u.lower() for u in utterances], {}
    ```

2.  **Implement** the `transform` method (or specific audio hooks). It returns a tuple of
    `(utterances, context)` — return `{}` for the context if you add none.

3.  **Register** the entry point in your `pyproject.toml`, using the group for your transformer type (here, an utterance transformer):

```toml
[project.entry-points."opm.transformer.text"]
my-transformer = "my_package.module:MyTransformer"

```

!!! note "The optional config-discovery entry point"
    Like TTS and STT plugins, a transformer can register a second entry point that exposes
    sample configurations for UI discovery. `PluginConfigTypes` defines one for every
    transformer type: append `.config` to the group, so `opm.transformer.text.config`,
    `opm.transformer.audio.config`, and so on.

    ```toml
    [project.entry-points."opm.transformer.text.config"]
    my-transformer.config = "my_package.module:MY_CONFIGS"
    ```

    The entry-point **name** needs the `.config` suffix too, and the target must be a plain
    dict — see [Plugin Manager: Expose language
    configurations](plugin-manager.md#4-expose-language-configurations-optional). This is
    optional; add it once the plugin has settings worth advertising.

---

## Package and publish

1. **Pin the dependency version.** Put a floor and a ceiling on `ovos-plugin-manager` in
   `pyproject.toml`, for example `ovos-plugin-manager>=0.5.0,<1.0.0`, so a future breaking
   release does not silently pull in.

2. **Install for local development.** Run `pip install -e .` from the plugin's own repository.
   See [OVOS Plugin Manager: Install and verify](plugin-manager.md#3-install-and-verify) for the
   check that confirms the plugin is discoverable.

3. **Publish to PyPI.** The Plugin Arena's benchmark sweep installs competitors from PyPI, so a
   transformer plugin needs a PyPI release before it can be entered. See
   [Plugin Arena: Getting Your Plugin Ranked](plugin-arena.md#getting-your-plugin-ranked) and
   [TTS Plugins: Package and publish](tts-plugin-development.md#package-and-publish) for the shared steps.

## Test your plugin locally

Instantiate the class directly and call `transform()` on it:

```python
from my_transformer_package import MyCustomTransformer

transformer = MyCustomTransformer()
utterances, context = transformer.transform(["HELLO WORLD"])
assert utterances == ["hello world"]
```

The constructor above works only because the example gives `name` a default. Without one,
`MyCustomTransformer()` raises `TypeError: __init__() missing 1 required positional
argument: 'name'` — the base class does not supply it.

Turn that into a pytest test that checks both return values:

```python
from my_transformer_package import MyCustomTransformer

def test_transform_lowercases_utterances():
    transformer = MyCustomTransformer()
    utterances, context = transformer.transform(["HELLO WORLD"], context={})
    assert utterances == ["hello world"]
    assert isinstance(context, dict)
```

To exercise the plugin inside a full OVOS install, `pip install -e .` it into the same virtual
environment or container `ovos-core` runs in, then add its name under the matching section of
`mycroft.conf` (for example `"utterance_transformers": {"my-custom-transformer": {}}`) and
restart OVOS.

---
**Read next:** [Transformer Plugins](transformer-plugins.md)
**Related:** [Utterance Transformers](utterance-transformers.md) · [Plugin Manager](plugin-manager.md) · [Plugin Arena](plugin-arena.md)
