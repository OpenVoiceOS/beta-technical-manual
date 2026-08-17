# GUI Protocol

!!! abstract "In a nutshell"
    This is a developer reference for the **legacy** (old, deprecated) way OVOS put things on a screen. It documents the set of behind-the-scenes messages that a skill, the screen service, and the on-device display use to stay in sync about what to show. Think of it as the agreed "language" two parts of the system speak so the right page and data appear. There is no generally usable OVOS screen today. This is kept mainly for **Mark 2** devices and reference, and a ground-up replacement is being built (see [GUI Adapter Plugins](gui-adapters.md)). For terms, see the [Glossary](glossary.md).

!!! danger "The OVOS GUI is deprecated: see [Screens on OVOS Today](gui-status.md) for the full picture"
    This page documents the legacy protocol. There is no generally usable OVOS GUI,
    and a replacement is **Upcoming**. Building a remote client? Skip this legacy protocol
    and see [Screens on OVOS Today](gui-status.md) for the current approach.

??? info "Formal specification"
    The **forward** model for the display subsystem is **[OVOS-GUI-1: GUI Display Subsystem](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md)** (a formal [architecture spec](architecture-specs.md)). It replaces the legacy protocol on this page with a clean separation: an application declares *what* to show by naming a template from a **closed `SYSTEM_*` vocabulary** and pushing flat session-data. Interchangeable **render backends (adapters)** decide *how* to draw it, fanned out to every installed adapter. The wire messages stay `gui.value.set` / `gui.page.show` / `gui.clear.namespace`, but a `gui.page.show` whose first page is **not** a `SYSTEM_*` template is rejected (no more arbitrary QML). A GUI message is routed **solely by its `session_id`**. This page documents the legacy Qt-WebSocket protocol that the OVOS-GUI-1 adapter model supersedes. Where they differ, the spec is the canonical target (see the "Upcoming" note at the foot of this page and [GUI Adapter Plugins](gui-adapters.md)).

The `ovos-gui` service exposes two communication channels:

1. **OVOS [messagebus](bus-service.md)**: used by skills and core components to set GUI state.


2. **Qt WebSocket** (default port 18181, served by `ovos-gui` itself): used by Qt5/Qt6
   GUI clients (`mycroft-gui-qt5`, `ovos-shell`) to receive display commands and send
   back user interaction events.

The Qt WebSocket server runs inside `ovos-gui` (`ovos_gui/bus.py`, Tornado). The
client-side transport is implemented in the
[mycroft-gui-qt5](https://github.com/OpenVoiceOS/mycroft-gui-qt5) library.

![Diagram of ovos-gui sitting between the bus (messages from OVOS) and a GUI websocket, fanning out over the GUI protocol to five client implementations: ovos-gnome-shell (GTK), ovos-shell (Qt5), ovos-gui-app (Qt6), ovos-tui (CLI), and ovos-react (web)](https://github.com/OpenVoiceOS/ovos-technical-manual/assets/33701864/92e73af7-f7d2-4aa3-a294-77f87aa22390)

---

## OVOS messagebus Messages

### Messages emitted by skills (via `GUIInterface`)

#### `gui.value.set`

Sent by `GUIInterface.__setitem__` / `_sync_data()` to write session variables into
the skill's namespace.

```json
{
  "type": "gui.value.set",
  "data": {
    "current_temp": 22,
    "condition": "Sunny",
    "__from": "ovos-skill-weather",
    "__idle": null
  }
}
```

| Field | Description |
|---|---|
| `__from` | [Skill](skill-design-guidelines.md) ID (namespace owner) |
| `__idle` | Idle timeout in seconds, or `null` |
| All other keys | Skill-defined session variables |

`NamespaceManager` stores all keys in `namespace.data`. The reserved keys
(`RESERVED_KEYS = ['__from', '__idle']`) are stripped before the values are mirrored to
clients as `mycroft.session.set`.

---

#### `gui.page.show`

Sent by `GUIInterface.show_page()` / `show_pages()` to request one or more pages be shown.

```json
{
  "type": "gui.page.show",
  "data": {
    "page_names": ["SYSTEM_TextFrame"],
    "index": 0,
    "__from": "ovos-skill-weather",
    "__idle": null
  }
}
```

`page_names` are page resource identifiers. The built-in pages use `SYSTEM_*` names (e.g.
`SYSTEM_TextFrame`, `SYSTEM_ImageFrame`, `SYSTEM_Face`). Skills may also ship their own
`.qml` pages and reference them by name. `NamespaceManager` records the page list against
the namespace and mirrors it to clients as `mycroft.gui.list.insert` with the resolved
page URIs.

---

#### `gui.page.delete`

Removes a specific page from a skill's namespace page list.

```json
{
  "type": "gui.page.delete",
  "data": {
    "page_names": ["Weather.qml"],
    "__from": "ovos-skill-weather"
  }
}
```

---

#### `gui.page.delete.all`

Clears all pages from a skill's namespace.

```json
{
  "type": "gui.page.delete.all",
  "data": {
    "__from": "ovos-skill-weather"
  }
}
```

---

#### `gui.event.send`

Sends an arbitrary event into a skill's namespace. `NamespaceManager` forwards it to
clients as `mycroft.events.triggered` with `namespace = __from`.

```json
{
  "type": "gui.event.send",
  "data": {
    "__from": "ovos-skill-weather",
    "event_name": "my.gui.event",
    "params": {"item": 3}
  }
}
```

---

### Messages consumed by `NamespaceManager` (from skills / core)

#### `gui.clear.namespace`

Removes a skill's namespace from the active display stack and discards its
[Session](session.md) data.

```json
{
  "type": "gui.clear.namespace",
  "data": {
    "__from": "ovos-skill-weather"
  }
}
```

---

#### `mycroft.gui.screen.close`

A global "back" request. `NamespaceManager.handle_namespace_global_back()` removes the
namespace currently at the top of the active stack. It carries no payload.

```json
{
  "type": "mycroft.gui.screen.close",
  "data": {}
}
```

---

### Messages emitted by `ovos-gui` service

#### `gui.namespace.removed`

Emitted by `NamespaceManager` after a namespace has been deactivated and cleared.

```json
{
  "type": "gui.namespace.removed",
  "data": {
    "skill_id": "ovos-skill-weather"
  }
}
```

#### `gui.namespace.displayed`

Emitted when a namespace moves to the top of the active display stack.

```json
{
  "type": "gui.namespace.displayed",
  "data": {
    "skill_id": "ovos-skill-weather"
  }
}
```

---

### Status events forwarded to GUI clients

`NamespaceManager` subscribes to the following core bus messages and re-emits each to
connected Qt clients (via `forward_to_gui` → `mycroft.events.triggered` in the `system`
namespace), so the UI can react to listening/speaking state:

| Bus message type | Meaning |
|---|---|
| `recognizer_loop:wakeword` | Wake word detected |
| `ovos.listener.record.started` (legacy: `recognizer_loop:record_begin`) | Microphone opened |
| `ovos.listener.record.ended` (legacy: `recognizer_loop:record_end`) | Microphone closed |
| `recognizer_loop:utterance` | [Utterance](life-of-an-utterance.md) recognized |
| `recognizer_loop:recognition_unknown` | Intended STT-empty forward; the listener actually emits `recognizer_loop:speech.recognition.unknown`, so this subscription never fires (topic-name mismatch in `ovos-gui`) |
| `speak` | [TTS](tts-plugins.md) about to speak |
| `recognizer_loop:audio_output_start` | Audio playback started |
| `recognizer_loop:audio_output_end` | Audio playback ended |
| `ovos.listener.sleep` (legacy: `recognizer_loop:sleep`) | Device going to sleep |
| `recognizer_loop:wake_up` | Device waking up |
| `ovos.listener.awoken` (legacy: `mycroft.awoken`) | Wake-up acknowledged |
| `mycroft.skill.handler.start` | A skill handler started |
| `mycroft.skill.handler.complete` | A skill handler completed |
| `complete_intent_failure` | No intent/fallback matched the utterance |
| `ovos.utterance.handled` | Intent matched and handled |
| `ovos.utterance.cancelled` | Utterance canceled |

`NamespaceManager` also forwards a set of legacy `enclosure.eyes.*` / `enclosure.mouth.*` /
`enclosure.weather.display` messages, kept for [Mark 1](mark1.md)-style enclosure animations.

!!! note "Producer/consumer split for `enclosure.*`"
    The `enclosure.*` protocol has two independent halves in separate packages: `EnclosureAPI`
    (the skill-facing producer that emits `enclosure.*`, in `ovos-gui-api-client` alongside
    `GUIInterface`) and `EnclosureProtocolListener` (the consumer mix-in that wires those
    messages to overridable no-op handlers, in
    [`ovos-ui-enclosure-protocol`](https://github.com/OpenVoiceOS/ovos-ui-enclosure-protocol)).
    A hardware enclosure plugin inherits `EnclosureProtocolListener` to receive the commands.
    [`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1) is the
    reference listener implementation.

---

## Qt WebSocket Protocol (Legacy Adapter)

> This section applies only when `ovos-legacy-mycroft-gui-plugin` is installed.

The messagebus messages above are mirrored to Qt clients as a separate set of
`mycroft.session.*` / `mycroft.gui.list.*` / `mycroft.events.triggered` wire messages over a
WebSocket connection. The full message catalog, with JSON examples for the connection
handshake, namespace stack management, session data sync, page management, and events, has
moved to its own page: **[GUI Protocol Messages](gui-protocol-messages.md)**.

---
**Read next:** [GUI Protocol Messages](gui-protocol-messages.md)
**Related:** [GUI Service (legacy)](gui-service.md) · [Screens on OVOS Today](gui-status.md) · [GUI Adapters](gui-adapters.md)
