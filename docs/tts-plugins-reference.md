# TTS Plugins Reference

!!! abstract "In a nutshell"
    This page holds the full technical entry for each TTS plugin in the roster: repository link, license notes, and a default configuration snippet where one exists. Start at [TTS Plugins](tts-plugins.md) to pick a plugin, come here for the exact settings.

## ovos-tts-server

- **GitHub**: [OpenVoiceOS/ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server)


- **Description**: Turn any OVOS TTS plugin into a micro service!

---

## ovos-tts-plugin-polly

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-polly](https://github.com/OpenVoiceOS/ovos-tts-plugin-polly)


- **Description**: Amazon Polly cloud text-to-speech.

---

## ovos-tts-plugin-google-tx

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-google-tx](https://github.com/OpenVoiceOS/ovos-tts-plugin-google-tx)


- **Description**: OVOS TTS plugin for [gTTS](https://github.com/pndurette/gTTS)

!!! note
    gTTS works by calling the same unofficial, undocumented endpoint used by the Google
    Translate web UI's "listen" feature. It is not a published, API-keyed Google Cloud
    Text-to-Speech API. Google can change or revoke access to this endpoint at any time.

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-google-tx"
  }
 

```

---

## ovos-tts-plugin-edge-tts

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-edge-tts](https://github.com/OpenVoiceOS/ovos-tts-plugin-edge-tts)


- **Description**: TTS plugin for [OVOS](https://openvoiceos.org) based on [Edge-TTS](https://github.com/rany2/edge-tts)

---

## ovos-tts-plugin-matxa-multispeaker-cat

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat](https://github.com/OpenVoiceOS/ovos-tts-plugin-matxa-multispeaker-cat)


- **Description**: [Matxa-TTS](https://huggingface.co/projecte-aina/matxa-tts-cat-multiaccent), the multispeaker, multidialectal neural TTS model. It works together with the vocoder model [alVoCat](https://huggingface.co/projecte-aina/alvocat-vocos-22khz) to generate speech in four Catalan dialects. Warning: archived, deprecated.

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-matxa-multispeaker-cat",
    "ovos-tts-plugin-matxa-multispeaker-cat": {
      "voice": "valencia/gina"
    }
  }

```

---

## ovos-tts-plugin-piper

- **GitHub**: [https://github.com/OpenVoiceOS/ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper)

- **Description**: Offline neural TTS using the [Piper](https://github.com/rhasspy/piper) engine (ONNX voices). This is the default TTS on the raspOVOS `hybrid` and `offline` images. Warning: archived. [phoonnx](https://github.com/TigreGotico/phoonnx) runs Piper ONNX voices (including the `kusal` voice) and is the maintained successor.

- **Config**: set `"module": "ovos-tts-plugin-piper"` in the `tts` block. A `"voice"` key selects a specific Piper voice model, without it the plugin picks a voice for the configured language.

## ovos-tts-plugin-marytts

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-marytts](https://github.com/OpenVoiceOS/ovos-tts-plugin-marytts)


- **Description**: TTS Plugin for [MaryTTS](https://github.com/marytts/marytts)

### Recommended Configuration

`url` is required (the plugin refuses to load without it); only `voice` has a default
(`cmu-slt-hsmm`). Point `url` at your own MaryTTS server:

```jsonc
"tts": {
    "module": "ovos-tts-plugin-marytts",
    "ovos-tts-plugin-marytts": {
      "url": "http://0.0.0.0:59125",
      "voice": "cmu-slt-hsmm"
    }
}

```

---

## ovos-tts-plugin-espeakNG

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-espeakNG](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG)


- **Description**: eSpeak NG offline text-to-speech (robotic, supports many languages).

---

## ovos-tts-plugin-beepspeak

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-beepspeak](https://github.com/OpenVoiceOS/ovos-tts-plugin-beepspeak)


- **Description**: Novelty R2-D2-style beep text-to-speech.

---

## ovos-tts-plugin-cotovia

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-cotovia](https://github.com/OpenVoiceOS/ovos-tts-plugin-cotovia)


- **Description**: OVOS TTS plugin for [Cotovia TTS](https://web.archive.org/web/2023/http://gtm.uvigo.es/cotovia)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-cotovia",
    "ovos-tts-plugin-cotovia": {
      "voice": "iago"
    }
  }
 

```

---

## ovos-tts-plugin-mimic

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-mimic](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic)


- **Description**: OVOS TTS plugin for [Mimic](https://github.com/MycroftAI/mimic1)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-mimic",
    "ovos-tts-plugin-mimic": {
      "voice": "ap"
    }
  }

```

---

## ovos-tts-plugin-SAM

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-SAM](https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM)


- **Description**: S.A.M., Software Automatic Mouth, the classic retro speech synthesizer.

---

## ovos-tts-plugin-azure

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-azure](https://github.com/OpenVoiceOS/ovos-tts-plugin-azure)


- **Description**: This TTS service for OpenVoiceOS requires a subscription to Microsoft Azure and the creation of a Speech resource (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview#create-the-azure-resource)

### Default Configuration

!!! warning "Never commit a real `api_key`"
    Treat this like any other credential: keep the real value out of version control and
    shared config files. Use a local, untracked config or an environment-backed secret
    store instead of hard-coding it in `mycroft.conf`.

```jsonc
"tts": {
    "module": "ovos-tts-plugin-azure",
    "ovos-tts-plugin-azure": {
        "api_key": "insert_your_key_here",
        "voice": "en-US-JennyNeural",  // optional, this is already the default
        "region": "westus" // optional, if your region is westus
    }
}

```

---

## ovos-tts-plugin-ahotts

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-ahotts](https://github.com/OpenVoiceOS/ovos-tts-plugin-ahotts)


- **Description**: OVOS TTS plugin for [AhoTTS](https://github.com/aholab/AhoTTS)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-ahotts",
    "ovos-tts-plugin-ahotts": {
        "lang": "eu"
    }
  }

```

---

## ovos-tts-server-plugin

- **GitHub**: [OpenVoiceOS/ovos-tts-server-plugin](https://github.com/OpenVoiceOS/ovos-tts-server-plugin)


- **Description**: OpenVoiceOS companion plugin for [OpenVoiceOS TTS Server](https://github.com/OpenVoiceOS/ovos-tts-server)

!!! warning "Talks to a public community server by default"
    The `host` below points at a best-effort, publicly-run community server, not a private
    or guaranteed-available endpoint. Point it at your own self-hosted server (see
    [tts-server](tts-server-deployment.md#companion-plugin)) if you need privacy or reliability.

### Recommended Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-server",
    "ovos-tts-plugin-server": {
        "host": "https://tts.smartgic.io/piper",
        "v2": true,
        "verify_ssl": true,
        "tts_timeout": 5
     }
 } 

```

When `host` is omitted (the true default), the plugin shuffles the public community
server list (`tts.openvoiceos.pt` and `tts.smartgic.io/piper`) and tries them in order.
Either way these are public community-run servers, not addresses on your network. See
[tts-server](tts-server-deployment.md#companion-plugin) to self-host, or pick a fully offline voice from the
table on the [TTS Plugins](tts-plugins.md) page.

--8<-- "snippets/community-servers.md"

---

## ovos-tts-plugin-coqui

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-coqui](https://github.com/OpenVoiceOS/ovos-tts-plugin-coqui)


- **Description**: OVOS TTS plugin for [Coqui TTS](https://coqui-tts.readthedocs.io/en/latest)

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-coqui",
    "ovos-tts-plugin-coqui": {}
  }
 

```

---

## ovos-tts-plugin-pico

- **GitHub**: [OpenVoiceOS/ovos-tts-plugin-pico](https://github.com/OpenVoiceOS/ovos-tts-plugin-pico)


- **Description**: SVOX Pico lightweight offline text-to-speech.

---

## ovos-tts-plugin-phoonnx

- **GitHub**: [TigreGotico/phoonnx](https://github.com/TigreGotico/phoonnx)


- **Description**: OVOS's own multilingual, ONNX-based neural TTS engine, distributed as part of the `phoonnx` package. Registering the plugin only requires `pip install phoonnx`. Model files are fetched and cached automatically the first time a voice is used.

### Default Configuration

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-phoonnx",
    "ovos-tts-plugin-phoonnx": {
      "voice": "OpenVoiceOS/phoonnx_pt-PT_miro_tugaphone"
    }
  }

```

> If `"voice"` is omitted, the plugin picks the first bundled model that supports the configured language.

### Per-language default voices

A configured `voice` pins one voice regardless of request language. For multilingual serving
(1.86.0a1+), the `lang2voice` config map, e.g. `{"pt-br": "...", "gl": "..."}`, and
`PHOONNX_DEFAULT_VOICE_<LANG>` env vars resolve the default voice per request language. Keys
are BCP-47 tags, full tag tried before primary subtag, and resolution is table-major: the
whole `lang2voice` table wins outright for any language it names before env vars are consulted
at all. Spellings are normalized on both sides (`gl-ES`/`gl`, `pt-br`/`pt_BR` agree). An entry
naming a nonexistent voice logs the mistake and falls back to the voice index's own default
rather than refusing to serve the language.

### Bounding the voice cache

Loaded voice models stay resident in an in-process cache. Two settings bound it, and they are
not equivalent:

| Key | Bounds by | Default |
|---|---|---|
| `max_loaded_bytes` | Total size in memory, LRU-evicted. Accepts a plain byte count or a human size like `"3GB"`, `"512MB"`, `"1.5GiB"` (`KB/MB/GB/TB` are powers of 1000, `KiB/MiB/GiB/TiB` powers of 1024). | unset (no budget) |
| `max_loaded_voices` | Count of resident voices, LRU-evicted. | unset (no limit) |

`max_loaded_voices` is the older setting and a poor bound on this catalog: a Piper voice is
around 60 MB while an omnivoice voice is around 2.2 GB, roughly a 40x spread, so a count that is
safe for small voices is fatal for large ones. `max_loaded_bytes` bounds by the actual resident
size instead, and is the one to reach for on a mixed catalog. (Mirrors `max_loaded_mb` on the
[linguonnx plugins](linguonnx-plugins.md#configuration).)

```jsonc
  "tts": {
    "module": "ovos-tts-plugin-phoonnx",
    "ovos-tts-plugin-phoonnx": {
      "voice": "OpenVoiceOS/phoonnx_pt-PT_miro_tugaphone",
      "pinned_voices": ["OpenVoiceOS/phoonnx_pt-PT_miro_tugaphone"],
      "max_loaded_bytes": "3GB"
    }
  }

```

`pinned_voices` (a string or a list) names voices that are loaded at startup and never
evicted. The two caps treat pins differently. If more voices are pinned than
`max_loaded_voices` allows, that **count** limit is raised to fit them (logged as an error so
the mismatch isn't silent). The `max_loaded_bytes` **size** budget is never raised: a pin that
fits individually still loads even when resident usage then exceeds the budget (again logged,
not fatal), but a pin whose own on-disk size alone exceeds the entire budget is refused and
never becomes resident (1.82.0a1+ — loading it would be a guaranteed OOM kill, not a degraded
path). A failed pin never stops the service from starting.

Size the budget for the actual peak, not just the steady state: peak resident memory is the
cached models plus whatever is loading in flight at that moment, and a request that arrives
mid-load can tip a box over even when the cache's own ceiling looks safe.

---
**Read next:** [TTS Plugins](tts-plugins.md)
**Related:** [Writing a TTS Plugin](tts-plugin-development.md) · [TTS Server](tts-server.md) · [SSML](ssml.md)
