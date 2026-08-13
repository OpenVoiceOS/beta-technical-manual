# Public Server Stack

!!! abstract "In a nutshell"
    This page describes how the community's public speech and translation servers
    are put together, so you can build the same thing yourself. Three services —
    text-to-speech, speech-to-text, and translation — each run as a small HTTP
    server in its own container, sharing one machine and one model cache. It is a
    reference deployment, not a product: everything here is ordinary Docker and
    ordinary OVOS plugins.

--8<-- "snippets/community-servers.md"

## The Three Services

| Service | Server | Plugin | Port |
|---|---|---|---|
| Text-to-speech | [`ovos-tts-server`](tts-server.md) | `phoonnx` | `9666` |
| Speech-to-text | [`ovos-stt-server`](stt-server.md) | `onnx-asr` | `8080` |
| Translation & language ID | [`ovos-translate-server`](translate-server.md) | [`linguonnx`](linguonnx-plugins.md) | `9686` |

The pattern is the same in all three: a plugin does the work, a thin FastAPI
server puts it on HTTP, and a client plugin on the device points at the URL. The
device-side plugins are `ovos-tts-plugin-server`, `ovos-stt-plugin-server`, and
`ovos-translate-server-plugin`; each is configured with a `url` and nothing else.

All three run ONNX models on CPU. There is no GPU in this deployment and none is
required — the choice of ONNX runtimes throughout is what makes a single
modest server able to host the set.

## Machine Shape

A host that runs the three services together wants:

- **Memory.** Translation dominates. Budget 12 GB for the translation container
  alone, and give each container a hard `mem_limit` so an overrun restarts one
  service instead of OOM-killing the host. See
  [`linguonnx` deployment](https://github.com/OpenVoiceOS/ovos-plugin-linguonnx/blob/dev/docs/deployment.md)
  for how that number is derived and which settings hold it.
- **Disk.** The translation model registry is roughly 109 GB at int8 precision;
  speech models are a few GB. Put the cache on a volume that survives container
  replacement, and do not put it on the same disk you need free.
- **CPU.** Threads matter more than clock. `OMP_NUM_THREADS` bounds each
  container's ONNX threadpool; leave headroom so one busy service does not
  starve the others.

## Persist the Model Cache

None of the images bake models in. They download on first use, which means a
container without a persistent cache re-downloads tens of gigabytes on every
replacement, and its first request after each restart blocks on a real
download — several minutes for a large translation model. Mount the whole cache
directory, not one subdirectory of it:

```yaml
volumes:
  - linguonnx-cache:/home/ovos/.cache
```

That covers both `~/.cache/huggingface` and any plugin-specific store beneath
it. The images create and `chown` these paths to the non-root `ovos` user at
build time, so a bind mount over an empty host directory does not end up
root-owned and unwritable.

**Prefetch before serving traffic.** A cold cache is slow, not broken, but on a
public endpoint the two are indistinguishable to a user. Download the models you
intend to serve as part of bringing the service up, not as a side effect of the
first request.

## Configuration

The three servers differ in where their plugin settings come from — check each
server's own page before assuming `mycroft.conf` applies:

- The **TTS server** reads the `tts` section of `mycroft.conf`, keyed by plugin
  id — mount the file read-only:

    ```yaml
    volumes:
      - ./mycroft.conf:/home/ovos/.config/mycroft/mycroft.conf:ro
    ```

- The **STT server** selects and configures its STT plugin through CLI flags
  alone — the `stt` section of `mycroft.conf` is not read — but its
  audio/utterance transformer chains and default `lang` still come from
  `mycroft.conf` ([STT Server](stt-server.md)).
- The **translate server** likewise takes its engines from CLI flags and ignores
  `mycroft.conf` ([Translate Server](translate-server.md)).

A settings block placed in a section a service does not read is ignored
silently — the service starts, answers requests, and runs on defaults while
appearing configured. See [All Configuration Keys](config-all-keys.md) for the
section each plugin type reads.

Verify a config applied by observing behaviour, not by reading the file back.
Pick a request whose answer differs between your settings and the defaults, and
watch which one you get. The file being correct and the plugin having read it
are two different claims.

## Operating It

- **Health checks** should hit each server's status endpoint, which answers
  without loading a model. A real request is the wrong health check: it can
  block on a cold download and mark a healthy instance as failed.
- **Upgrades** replace one container at a time. With the cache on a volume, a
  replaced container is warm immediately.
- **Announce what you run.** A public endpoint carries no warranty and no uptime
  guarantee. Say so where the URL is published, and expect people to self-host
  once they depend on it.

## Self-hosting Without the Servers

Running these services is one option, not a requirement. Every capability here
also exists as a plugin that runs directly on the device with no network at all:
`phoonnx` for TTS, `onnx-asr` for STT, and `linguonnx` for translation are the
same code the servers wrap. A server is worth running when several devices
should share one machine's CPU and one copy of the models — not by default.

**Read next:** [Server Compatibility Layers](server-compat-layers.md)

**Related:** [STT Server](stt-server.md) · [TTS Server](tts-server.md) · [Translate Server](translate-server.md) · [Production Overview](production-overview.md)
