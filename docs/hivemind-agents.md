# Remote Agents with HiveMind

!!! info "No maturity badge here"
    HiveMind is a separate project, with its own organization and [community docs](https://jarbashivemind.github.io/HiveMind-community-docs/). The OVOS [Maturity Scale](maturity.md), which rates OVOS-org repository health, does not apply to it. This page covers the OVOS-side integration only.

!!! abstract "In a nutshell"
    OpenVoiceOS runs **local-first**. Sometimes you want one capable machine to do the
    thinking while several small devices ("satellites") listen and speak. Or you want to
    reach your assistant securely from off-device. **HiveMind** is the companion project
    that makes this possible. It exposes an OVOS install, or a single persona, over an
    authenticated, encrypted protocol that satellites and clients connect to.

!!! info "HiveMind lives under its own org"
    The HiveMind packages referenced here are maintained in the **[JarbasHiveMind](https://github.com/JarbasHiveMind)**
    GitHub organization (not `OpenVoiceOS`). The full guide is the
    [HiveMind community docs](https://jarbashivemind.github.io/HiveMind-community-docs/). This
    page covers how HiveMind relates to OVOS.

!!! note "HiveMind vs. agent-interop protocols"
    HiveMind is the **voice-satellite transport**: how a mic/speaker device or remote client
    reaches an OVOS brain. MCP and A2A (see [Agent Interop](agent-interop.md)) are different.
    They are LLM/agent tool protocols that let AI systems call each other's tools.

!!! tip "Building a remote client"
    If you are writing a remote or native (non-Python) client that connects over HiveMind,
    this manual is **not** the place to look for the wire details. HiveMind defines its own
    protocol: the connect URL, the access-key auth handshake, the message envelope, and the
    reconnect/backoff behavior a client must implement. That protocol is documented in the
    HiveMind project's own community documentation:
    [HiveMind community docs](https://jarbashivemind.github.io/HiveMind-community-docs/).
    This page only covers the OVOS side, meaning how an OVOS install is exposed as a
    HiveMind agent.

---

## The pieces

| Piece | Role |
|---|---|
| **`hivemind-core`** | The server. Listens for connections, authenticates clients, enforces permissions, and routes messages to an **agent**. |
| **Agent** | What actually answers: either a full [ovos-core](core.md) install (`hivemind-ovos-agent-plugin`) or a single [persona](personas.md) (`hivemind-persona-agent-plugin`). |
| **Satellites / clients** | The devices and apps that connect to `hivemind-core` (mic satellites, CLI clients, your own code). |

`hivemind-core` is **pluggable** via the **HiveMind Plugin Manager (HPM)** across four axes.
You can swap implementations without touching the rest:

- **Agent protocol**: what brain answers (OVOS / persona / others).
- **Network protocol**: how clients connect (WebSocket is the reference implementation).
- **Database**: where client credentials live (JSON / SQLite / Redis).
- **Binary data handler**: how binary payloads (e.g. audio) move over the mesh.

```mermaid
flowchart LR
    Kitchen[Kitchen satellite] -- HiveMind protocol --> Listener["hivemind_listener\n:5678"]
    Bedroom[Bedroom satellite] -- HiveMind protocol --> Listener
    Restroom[Restroom satellite] -- HiveMind protocol --> Listener
    Listener --> Core["hivemind-core\n(auth + permissions)"]
    Core --> Agent["ovos-core\n(hivemind-ovos-agent-plugin)"]
```

![Diagram of a server running ovos-core and hivemind-core, exposing a hivemind_listener on port 5678 that three satellite clients (Kitchen, Bedroom, Restroom) connect to, each relaying its own spoken request back to the server](img/satellites.png)

---

## Quickstart: expose an OVOS install

```bash
pip install hivemind-core
```

**1. Provision a client.** Every satellite or client needs an access key issued by the server:

```bash
hivemind-core add-client       # prints an access key + password for one client
```

This writes the client to the server's credentials database (under
`xdg_data_home()/hivemind-core`), separate from the server config at
`~/.config/hivemind-core/server.json`.

**2. Start the server:**

```bash
hivemind-core listen           # start listening for HiveMind connections
```

By default it serves the local `ovos-core` via `hivemind-ovos-agent-plugin` (configured under
`agent_protocol` in `server.json`).

**3. Give a client its identity, then connect.** On the *client* device, save the access key
issued in step 1. This step makes everything else work:

```bash
pip install hivemind-websocket-client
hivemind-client set-identity    # stores the access key / host for this node
```

After `set-identity`, clients (and the [solver](#using-hivemind-as-a-solver) below) can connect
without being handed connection details each time.

**4. Verify the satellite actually connected.** Run this on the client after `set-identity`:

```bash
hivemind-client test-identity
```

On success it prints:

```text
== Identity successfully connected to HiveMind!
```

If it hangs or errors, check that the server is running (`hivemind-core listen`) and reachable
on the configured host and port. Also check that the access key matches one printed by
`hivemind-core add-client`.

---

## Choosing the agent: full OVOS vs a single persona

The agent is selected by the `agent_protocol.module` key in `~/.config/hivemind-core/server.json`.

### Full OVOS: `hivemind-ovos-agent-plugin`

The default. Bridges HiveMind to a running [ovos-core](core.md) over its messagebus. Remote
clients get the whole assistant: skills, pipelines, OCP, and more.

### A single persona: `hivemind-persona-agent-plugin`

Exposes just one [persona](personas.md), with no `ovos-core` and no messagebus, so the attack
surface stays minimal. It answers straight from the configured persona.

```json
{
  "agent_protocol": {
    "module": "hivemind-persona-agent-plugin",
    "hivemind-persona-agent-plugin": {
      "persona": {
        "name": "Llama",
        "solvers": ["ovos-solver-openai-plugin"],
        "ovos-solver-openai-plugin": {
          "api_url": "https://llama.smartgic.io/v1",
          "key": "sk-xxxx",
          "system_prompt": "You are helpful, creative, clever, and very friendly."
        }
      }
    }
  }
}
```

The `persona` value may be an inline config dict, as above, or a path to an
[ovos-persona](https://github.com/OpenVoiceOS/ovos-persona) JSON file (`~` is expanded). The
`"module"` value must equal the plugin's entry-point name. That same string is reused as the
key holding its config.

---

## Satellites & clients

A server is only useful once something connects to it. On the client side:

- **[`hivemind-websocket-client`](https://github.com/JarbasHiveMind/hivemind-websocket-client)**: the client library and the `hivemind-client` CLI (`set-identity`, send utterances, and more).
- **[`hivemind-mic-satellite`](https://github.com/JarbasHiveMind/hivemind-mic-satellite)**: a thin device that only does wake-word and microphone capture. STT and TTS run server-side.
- **[`hivemind-listener`](https://github.com/JarbasHiveMind/hivemind-listener)**: the server-side audio entry point that performs STT/TTS for audio satellites, with binary audio moving over the mesh.

This split is the real "voice satellite" story: cheap devices listen and speak, and the server thinks.

---

## Permissions & access control

HiveMind is **deny-by-default**: a client may only do what it has been explicitly granted.
`hivemind-core` enforces this at the message-type level with a `PolicyChain` of pluggable
`PolicyPlugin`s, including `MessageTypeACLPolicy`, that checks every inbound message. Its
admin CLI manages this, including:

- `add-client` / `list-clients` / `delete-client`: manage who may connect.
- `allow-msg` / `blacklist-msg`: allow or block specific bus message types per client.
- `make-admin` / `revoke-admin`, `allow-escalate` / `allow-propagate`: elevate or restrict a client.
- `blacklist-skill` / `allow-skill`, `blacklist-intent` / `allow-intent`: stop or re-allow a
  client from reaching specific skills or intents. These verbs only write `skill_blacklist` and
  `intent_blacklist` client metadata. Enforcing them against skill or intent IDs requires the
  `OVOSAgentPolicy` plugin (from `hivemind-ovos-agent-plugin`) to be present in the server's
  policy chain. The CLI verbs alone block nothing without it.

This is what makes HiveMind safe to expose to satellites or other users, unlike the plain
[persona-server](persona-server.md), which is HTTP with no auth.

!!! tip "Web admin UI"
    [`hivemind-admin-panel`](https://github.com/JarbasHiveMind/hivemind-admin-panel) is a web UI
    for managing clients, permissions, plugins and personas instead of the CLI.

---

## Using HiveMind as a solver

Your local assistant can ask a remote HiveMind agent when it's stuck. Install the
**[`ovos-solver-hivemind-plugin`](https://github.com/JarbasHiveMind/ovos-solver-hivemind-plugin)**
(class `HiveMindSolver`, import `ovos_hivemind_solver`) and add it to a persona. It is a normal
[solver](agent-plugins.md), so it slots into a mixture-of-solvers chain. This helps when
delegating hard questions or surviving local outages.

```json
{
  "name": "HiveMind Agent",
  "solvers": ["ovos-solver-hivemind-plugin"],
  "ovos-solver-hivemind-plugin": {"autoconnect": true}
}
```

Or from your own code (the node identity must already be set with `hivemind-client set-identity`):

```python
from ovos_hivemind_solver import HiveMindSolver

bot = HiveMindSolver()          # reads the identity provisioned via `hivemind-client set-identity`
bot.connect()
print(bot.spoken_answer("what is the speed of light?"))
```

### As an intent-pipeline stage

There is also a pipeline-plugin form,
**[`ovos-hivemind-pipeline-plugin`](https://github.com/JarbasHiveMind/ovos-hivemind-pipeline-plugin)**
(entry point `opm.pipeline`, class `HiveMindPipeline`). Instead of living inside a persona, it
slots directly into the [intent pipeline](pipelines-overview.md). The idea: when in doubt, ask
a smarter OVOS install. Add it to `intents.pipeline` and configure it under `mycroft.conf`:

```json
{
  "intents": {
    "pipeline": ["...", "ovos-hivemind-pipeline-plugin", "..."],
    "ovos-hivemind-pipeline-plugin": {
      "name": "Hive Mind",
      "confirmation": true,
      "slave_mode": false
    }
  }
}
```

Use the **solver** form to delegate inside a persona's reasoning. Use the **pipeline** form to
delegate at the intent-matching stage, for example as a late, catch-all matcher.

---

## Deployment patterns

HiveMind and the [persona-server](persona-server.md) cover different trust boundaries:

| Use case | Tools | Secure? | Notes |
|---|---|---|---|
| Local interface + persona | `ovos-persona-server` + `persona.json` | ❌ | OpenAI-compatible HTTP, no auth, quick setups only |
| Local interface + OpenVoiceOS | `ovos-persona-server` + the `ovos-messagebus` handler | ❌ | Exposes the OVOS bus to the persona server; HTTP, no auth |
| Local interface + remote HiveMind agent | `ovos-persona-server` + `ovos-solver-hivemind-plugin` | ❌ | HTTP front, but the agent itself is remote |
| Secure remote OpenVoiceOS agent | `hivemind-core` + `hivemind-ovos-agent-plugin` + `ovos-core` | ✅ | Auth, encryption, granular permissions |
| Secure remote persona agent | `hivemind-core` + `hivemind-persona-agent-plugin` + `persona.json` | ✅ | Same, persona-only (minimal surface) |

The HTTP rows are useful for wiring a persona into local tools, such as Home Assistant's Ollama
integration or OpenWebUI, on a trusted network. The HiveMind rows are what you expose to
satellites or untrusted networks.

> ⚠️ The plain [`persona-server`](persona-server.md) is **HTTP only, not encrypted or
> authenticated**. Keep it on a trusted local network. Use HiveMind for anything remote.

---

## Further reading

- [HiveMind community docs](https://jarbashivemind.github.io/HiveMind-community-docs/)
- [A real use case with OVOS and Hivemind](https://blog.openvoiceos.org/posts/2025-07-25-A-real-use-case-with-OVOS-and-Hivemind) (OVOS blog)
- [OVOS & HiveMind in the Manufacturing Industry](https://blog.openvoiceos.org/posts/2026-01-14-OVOS-hivemind-industry) (OVOS blog)
