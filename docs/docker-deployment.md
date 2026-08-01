# Running OVOS in Containers

!!! abstract "In a nutshell"
    [`ovos-docker`](https://github.com/OpenVoiceOS/ovos-docker) publishes one container image
    per OVOS service, plus reference `docker-compose.yml` files that wire them together. Every
    compose service uses `network_mode: host`, so containers reach each other and the bus over
    the host's own loopback and network interfaces, not a private bridge network. This page
    covers the compose layout, audio device passthrough, networking, and the headless-server
    pattern for STT/TTS.

## What ovos-docker ships

`ovos-docker` builds one image per service, published under `docker.io/smartgic`:

- `ovos-messagebus`, `ovos-core`, `ovos-audio`, `ovos-listener`, `ovos-cli`
- `ovos-phal`, `ovos-phal-admin`, `ovos-plugin-ggwave`
- `ovos-gui-websocket`, `ovos-gui-original`, `ovos-gui-shell`
- `ovos-skill-base` and default skill images

There is no single "OVOS in one container" image. Each image installs one Python package and
runs one process. This mirrors the split described in
[Composable Deployments](composable-deployments.md): scale, restart, or relocate any one
service without touching the rest.

`ovos-docker` builds its images with Docker Buildx Bake for `linux/amd64` and `linux/arm64`
(the default `PLATFORMS` in its `docker-bake.hcl`), which covers a 64-bit Raspberry Pi OS
install. Check the actual tags on Docker Hub for the image and version you plan to run before
deploying to a Pi: not every image or channel is guaranteed to carry both architectures.

## A working compose file

This is a trimmed version of the reference
[`compose/docker-compose.yml`](https://github.com/OpenVoiceOS/ovos-docker/blob/dev/compose/docker-compose.yml).
It covers the messagebus, core, listener, and audio services, with the config, tmp, and
IPC volume mounts the upstream file uses.

```yaml title="docker-compose.yml"
services:
  ovos_messagebus:
    image: docker.io/smartgic/ovos-messagebus:${VERSION}
    network_mode: host
    volumes:
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft:ro
      - ovos_local_state:/home/${OVOS_USER}/.local/state/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft

  ovos_listener:
    image: docker.io/smartgic/ovos-listener:${VERSION}
    network_mode: host
    devices:
      - /dev/snd
    volumes:
      - ~/.config/pulse/cookie:/home/${OVOS_USER}/.config/pulse/cookie:ro
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft:ro
      - ovos_local_state:/home/${OVOS_USER}/.local/state/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft
      - ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro
    depends_on:
      - ovos_messagebus

  ovos_audio:
    image: docker.io/smartgic/ovos-audio:${VERSION}
    network_mode: host
    devices:
      - /dev/snd
    volumes:
      - ~/.config/pulse/cookie:/home/${OVOS_USER}/.config/pulse/cookie:ro
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft
      - ovos_tts_cache:/home/${OVOS_USER}/.cache/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft
      - ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro
    depends_on:
      - ovos_messagebus

  ovos_core:
    image: docker.io/smartgic/ovos-core:${VERSION}
    network_mode: host
    volumes:
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft
      - ovos_local_state:/home/${OVOS_USER}/.local/state/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft
    depends_on:
      - ovos_messagebus

volumes:
  ovos_local_state:
  ovos_tts_cache:
```

`OVOS_CONFIG_FOLDER` mounts the host's `mycroft.conf` directory into every container's
`~/.config/mycroft`. Every service reads the same file this way, so a single edit on the host
reaches all of them. `TMP_FOLDER` mounts a shared host directory to `/tmp/mycroft` in every
container: this is how the listener hands recorded audio to the rest of the pipeline. Named
volumes (`ovos_local_state`, `ovos_tts_cache`, and in the full reference file also
`ovos_models`, `ovos_vosk`, `ovos_listener_records`, `ovos_nltk`) hold anything that must
survive a container rebuild: downloaded models, the TTS cache, and local runtime state.

The [full reference file](https://github.com/OpenVoiceOS/ovos-docker/blob/dev/compose/docker-compose.yml)
also runs `ovos_phal` and `ovos_phal_admin` with `privileged: true` and `cap_add: [SYS_ADMIN,
DAC_OVERRIDE]`, plus `/dev` and `/sys` mounts, for hardware access (LEDs, buttons, power
control). Add those only for the services that need direct hardware access.

## Audio device passthrough

The listener and audio containers both need `/dev/snd` passed through with `devices:
["/dev/snd"]`, plus access to the host's sound server. Upstream mounts PulseAudio's or
PipeWire's runtime socket read-only:

```yaml
volumes:
  - ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro
  - ${XDG_RUNTIME_DIR}/pipewire-0:${XDG_RUNTIME_DIR}/pipewire-0:ro
  - ~/.config/pulse/cookie:/home/${OVOS_USER}/.config/pulse/cookie:ro
environment:
  PULSE_SERVER: unix:${XDG_RUNTIME_DIR}/pulse/native
  PULSE_COOKIE: /home/${OVOS_USER}/.config/pulse/cookie
```

Without the PulseAudio cookie, the containers cannot authenticate against the host's sound
server even with the socket mounted. `ovos-docker` ships separate compose overlays for macOS
and Windows (`docker-compose.macos.yml`, `docker-compose.windows.yml`), because neither host
exposes a native PulseAudio/PipeWire socket the same way Linux does.

## Networking

Every service in the reference compose files runs with `network_mode: host`. There is no
private bridge network and no inter-container DNS: a container reaches the bus at
`localhost:8181`, same as a bare-metal process would.

!!! danger "Host networking shares the loopback across every container"
    With `network_mode: host`, `127.0.0.1` inside a container is the **host's** loopback, not
    a container-private one. Any process on that host, containerized or not, can reach a bus
    bound to `127.0.0.1`. Treat the whole host as the trust boundary, not the individual
    container. See [Production Operations](production-operations.md#thin-clients-a-shared-speech-backend)
    for the same warning applied to a thin-client fleet.

The bus listens on port `8181`. The GUI service listens on a separate port, `18181` by
default (config key `gui_websocket.base_port`, see [Bus Service](bus-service.md)). The bus
binds `127.0.0.1` by default, but the GUI socket ships bound to `0.0.0.0`. Combined with host
networking, that puts the unauthenticated GUI socket on the whole LAN, not just the device.
Set `gui_websocket.host` to `127.0.0.1` unless a remote display client needs it.

If you ever run these images with a non-host network driver instead (a private bridge
network), point `websocket.host` in each container's `mycroft.conf` at the messagebus
container's name or hostname, the way any other split-host OVOS deployment does (see
[Composable Deployments](composable-deployments.md)). The upstream compose files do not do
this: they rely on host networking and `localhost` throughout.

## Server/satellite split

For the one-brain-many-speakers pattern described in
[Satellites](satellites.md#build-walkthrough-a-raw-shared-bus), split the compose file above
into a server stack and a satellite stack. The server runs the messagebus and `ovos-core`
(plus skills); each satellite runs only a listener and an audio service, with PHAL added only
if the device needs direct hardware access. Both stacks use the same images and volume layout
as [the reference compose file](#a-working-compose-file); only which services run where
changes.

```yaml title="docker-compose.yml — server"
services:
  ovos_messagebus:
    image: docker.io/smartgic/ovos-messagebus:${VERSION}
    network_mode: host
    volumes:
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft:ro
      - ovos_local_state:/home/${OVOS_USER}/.local/state/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft

  ovos_core:
    image: docker.io/smartgic/ovos-core:${VERSION}
    network_mode: host
    volumes:
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft
      - ovos_local_state:/home/${OVOS_USER}/.local/state/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft
    depends_on:
      - ovos_messagebus

volumes:
  ovos_local_state:
```

```yaml title="docker-compose.yml — satellite (per device)"
services:
  ovos_listener:
    image: docker.io/smartgic/ovos-listener:${VERSION}
    network_mode: host
    devices:
      - /dev/snd
    volumes:
      - ~/.config/pulse/cookie:/home/${OVOS_USER}/.config/pulse/cookie:ro
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft:ro
      - ${TMP_FOLDER}:/tmp/mycroft
      - ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro

  ovos_audio:
    image: docker.io/smartgic/ovos-audio:${VERSION}
    network_mode: host
    devices:
      - /dev/snd
    volumes:
      - ~/.config/pulse/cookie:/home/${OVOS_USER}/.config/pulse/cookie:ro
      - ${OVOS_CONFIG_FOLDER}:/home/${OVOS_USER}/.config/mycroft
      - ovos_tts_cache:/home/${OVOS_USER}/.cache/mycroft
      - ${TMP_FOLDER}:/tmp/mycroft
      - ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro

  # ovos_phal:
  #   image: docker.io/smartgic/ovos-phal:${VERSION}
  #   network_mode: host
  #   # add only if this satellite needs direct hardware access (LEDs, buttons, power)

volumes:
  ovos_tts_cache:
```

Point each satellite's mounted `mycroft.conf` at the server, since `network_mode: host`
puts every container on the satellite behind the satellite host's own IP, not a container
name:

```jsonc
{
  "websocket": {
    "host": "192.168.1.10",
    "port": 8181,
    "route": "/core"
  }
}
```

Replace `192.168.1.10` with the server host's real LAN address. With `network_mode: host`
this must be a real IP or hostname, never a container or service name: host networking has
no inter-container DNS (see [Networking](#networking) above). See
[Satellites: Satellite config](satellites.md#satellite-config) for the same setting applied
to a bare-metal deployment, and the warnings there about the shared-session and
localhost-default pitfalls.

## Headless: STT/TTS servers as containers

`ovos-docker` also builds standalone STT and TTS server images, one per baked-in engine:
`ovos-stt-server-onnx-asr`, `ovos-stt-server-onnx-asr-cuda`, `ovos-tts-server-piper`,
`ovos-tts-server-kokoro`, `ovos-tts-server-phoonnx`, and others. These serve plain HTTP and
have no bus dependency, so they work as a shared backend for bare-metal or thin-client
satellites that only run the bus, listener, and audio locally. See
[Self-hosted STT Server](stt-server.md) and [Self-hosted TTS Server](tts-server.md) for the
HTTP contract and plugin-side config keys, and
[Production Operations: thin clients + a shared speech backend](production-operations.md#thin-clients-a-shared-speech-backend)
for a worked compose example splitting the speech backend from the thin client.

## Containerized HiveMind

`ovos-docker` does not publish a HiveMind image. HiveMind has its own separate project,
[HiveMind-Docker](https://github.com/JarbasHiveMind/hivemind-docker), with its own images
(published under `docker.io/smartgic`, built with Docker Buildx Bake for `linux/amd64` and
`linux/arm64`) and compose files for a HiveMind hub and its satellite/listener/chatroom
components. See [Remote Agents with HiveMind](hivemind-agents.md) for the pip-installed,
bare-metal path this manual documents in detail; check the HiveMind-Docker repository
directly for current image tags and compose usage.

## Limitations

- **Wake word and mic latency.** The listener still runs continuous audio capture and wake
  word detection inside the container. Passing `/dev/snd` and the sound-server socket through
  adds a layer compared to a bare-metal process; on constrained hardware, measure wake word
  latency before committing to a containerized listener rather than assuming it matches
  bare metal.
- **GPU access.** `ovos-stt-server-onnx-asr-cuda` exists as a named image, which implies GPU
  passthrough for that variant, but the upstream README and compose files documented here do
  not spell out the `docker run --gpus` or NVIDIA Container Toolkit setup needed to use it.
  Treat GPU passthrough as unverified until you check the image's own Dockerfile or open an
  issue against `ovos-docker` for the missing steps.
- **Privileged containers.** PHAL and PHAL-admin need `privileged: true` for hardware access
  (LEDs, buttons, power). That is a real, not cosmetic, trust boundary: a privileged
  container has the same access to the host as a root process would.

---
**Read next:** [Production Operations](production-operations.md)
**Related:** [Composable Deployments](composable-deployments.md) · [Self-hosted STT Server](stt-server.md) · [Self-hosted TTS Server](tts-server.md)
