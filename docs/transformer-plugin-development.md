# Writing a Transformer Plugin

!!! abstract "In a nutshell"
    This page is the tutorial for building your own transformer plugin: how to inherit from
    the right base class, register the entry point, package it, and test it. Looking for a
    plugin to use instead of writing one? Go to [Transformer Plugins](transformer-plugins.md).

## Creating a Plugin

1.  **Inherit** from the appropriate base class.


2.  **Implement** the `transform` method (or specific audio hooks).


3.  **Register** the entry point in your `pyproject.toml`, using the group for your transformer type (here, an utterance transformer):

```toml
[project.entry-points."opm.transformer.text"]
my-transformer = "my_package.module:MyTransformer"

```

!!! note "No config-discovery entry point for transformers"
    TTS and STT plugins can register a second entry point (`opm.tts.config`, `opm.stt.config`)
    that exposes sample configurations for UI discovery. See
    [TTS Plugins: Entry point](tts-plugin-development.md#entry-point). `ovos-plugin-manager`'s
    `PluginConfigTypes` enum has no matching entry for any transformer type (audio, utterance,
    metadata, intent, dialog, or tts transformers). A transformer plugin only registers under
    its `opm.transformer.*` group. There is no equivalent `opm.transformer.text.config` group to
    advertise its settings.

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
