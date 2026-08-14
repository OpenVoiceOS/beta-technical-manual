# GUI Protocol Messages

!!! abstract "In a nutshell"
    This page is the wire-level message catalog for the **legacy** Qt WebSocket GUI protocol: every `mycroft.session.*`, `mycroft.gui.list.*`, and `mycroft.events.triggered` message shape, with JSON examples. For the conceptual picture (what the protocol is for, the messagebus messages skills send, and the client architecture), see [GUI Protocol](gui-protocol.md). For terms, see the [Glossary](glossary.md).

!!! danger "The OVOS GUI is deprecated: see [Screens on OVOS Today](gui-status.md) for the full picture"
    This page documents the legacy protocol. There is no generally usable OVOS GUI,
    and a replacement is **Upcoming**. Building a remote client? Skip this legacy protocol
    and see [Screens on OVOS Today](gui-status.md) for the current approach.

---

## Qt WebSocket Protocol (Legacy Adapter)

> This section applies only when `ovos-legacy-mycroft-gui-plugin` is installed.

All messages are JSON objects sent over the WebSocket connection at `ws://localhost:18181/gui`.

### Connection handshake

**Qt client → `ovos-gui` (OVOS messagebus):**

```json
{
  "type": "mycroft.gui.connected",
  "data": {
    "gui_id": "unique_identifier_provided_by_client",
    "framework": "qt5"
  }
}
```

**`ovos-gui` → Qt client (OVOS messagebus reply):**

```json
{
  "type": "mycroft.gui.port",
  "data": {
    "port": 18181,
    "gui_id": "qt-client-1",
    "framework": "qt5"
  }
}
```

The Qt client then opens a WebSocket connection to `ws://localhost:18181/gui`.

!!! example "Try it: connect a raw WebSocket client to 18181"
    You don't need a Qt client to see this handshake happen. With `ovos-gui` running and the
    legacy adapter installed, connect any WebSocket client to `ws://localhost:18181/gui` (for
    example `websocat ws://localhost:18181/gui` or a short `websockets` Python script) and trigger
    a skill that shows a GUI page. You should observe the server immediately replay
    `mycroft.session.list.insert` and `mycroft.gui.list.insert` messages for the active
    namespace. This is `GUIWebsocketHandler.synchronize()` bringing your new client up to date.

When a client connects, `GUIWebsocketHandler.synchronize()` replays the full current state:

1. Re-sends `mycroft.session.list.insert` for every namespace in the active stack (in order).


2. For each namespace, re-sends `mycroft.gui.list.insert` with its current [QML](qt5-gui.md) page.


3. Re-emits all `mycroft.session.set` messages for every key in `namespace.data`.

---

### Namespace stack management (`mycroft.system.active_skills`)

The reserved namespace `mycroft.system.active_skills` defines the display priority.
The first item is always the namespace currently shown.

**Insert namespace** (skill becomes visible):

```json
{
  "type": "mycroft.session.list.insert",
  "namespace": "mycroft.system.active_skills",
  "position": 0,
  "data": [{"skill_id": "ovos-skill-weather"}]
}
```

**Move namespace** (existing skill re-activated):

```json
{
  "type": "mycroft.session.list.move",
  "namespace": "mycroft.system.active_skills",
  "from": 2,
  "to": 0,
  "items_number": 1
}
```

**Remove namespace** (skill cleared / idle):

```json
{
  "type": "mycroft.session.list.remove",
  "namespace": "mycroft.system.active_skills",
  "position": 0,
  "items_number": 1
}
```

---

### Session data sync (`mycroft.session.*`)

Session data is a key/value dictionary kept synchronized between `ovos-gui` and each
Qt client. Values may be strings, numbers, booleans, or lists.

**Set / update a key:**

```json
{
  "type": "mycroft.session.set",
  "namespace": "ovos-skill-weather",
  "data": {
    "current_temp": 22,
    "condition": "Sunny"
  }
}
```

**Delete a key:**

```json
{
  "type": "mycroft.session.delete",
  "namespace": "ovos-skill-weather",
  "property": "current_temp"
}
```

**List operations.** The shipping service emits `mycroft.session.list.*` messages only for
the reserved `mycroft.system.active_skills` namespace stack, always with a `data` key —
there is no per-skill list-property protocol (and no `mycroft.session.list.update`
producer at all). A namespace entering the active stack:

```json
{
  "type": "mycroft.session.list.insert",
  "namespace": "mycroft.system.active_skills",
  "position": 0,
  "data": [{"skill_id": "ovos-skill-weather.openvoiceos"}]
}
```

An already-active namespace moving to the front:

```json
{
  "type": "mycroft.session.list.move",
  "namespace": "mycroft.system.active_skills",
  "from": 2,
  "to": 0,
  "items_number": 1
}
```

A namespace leaving the stack:

```json
{
  "type": "mycroft.session.list.remove",
  "namespace": "mycroft.system.active_skills",
  "position": 2,
  "items_number": 1
}
```

---

### Page management (`mycroft.gui.list.*`)

Each active skill is associated with a list of page URIs.

**Insert new page at position:**

```json
{
  "type": "mycroft.gui.list.insert",
  "namespace": "ovos-skill-weather",
  "position": 0,
  "data": [{"url": "SYSTEM:TextFrame.qml", "page": "TextFrame.qml"}]
}
```

The `SYSTEM:` URI scheme is resolved by the Qt client to the matching system-template QML
file (see [OVOS Shell](ovos-shell.md) for the `OVOS_SYSTEM_TEMPLATES` override and
resolution order). Skill-provided `.qml` pages are sent as ordinary file URIs.

**Move pages:**

```json
{
  "type": "mycroft.gui.list.move",
  "namespace": "ovos-skill-weather",
  "from": 0,
  "to": 2,
  "items_number": 1
}
```

**Remove pages:**

```json
{
  "type": "mycroft.gui.list.remove",
  "namespace": "ovos-skill-weather",
  "position": 0,
  "items_number": 1
}
```

---

### Events (`mycroft.events.triggered`)

Events can be emitted by the GUI client (e.g. user tapped a button) or by the skill
(e.g. a voice command caused a state change).

```json
{
  "type": "mycroft.events.triggered",
  "namespace": "ovos-skill-weather",
  "event_name": "my.gui.event",
  "parameters": {"item": 3}
}
```

#### Page focus / interaction (client → core)

When the user swipes to a different page or interacts with one, the Qt client signals
core. `ovos-gui` listens for `gui.page_gained_focus` and `gui.page_interaction` on the
OVOS bus. Both carry `skill_id` and a zero-based `page_number`. The interaction event also
resets the namespace's idle-removal timer.

```json
{
  "type": "gui.page_gained_focus",
  "data": {"skill_id": "ovos-skill-weather", "page_number": 0}
}
```

#### System status events

Core bus events forwarded to Qt clients:

```json
{
  "type": "mycroft.events.triggered",
  "namespace": "system",
  "event_name": "recognizer_loop:wakeword",
  "data": {}
}
```

---

### Qt client → OVOS core bus

Messages received from Qt clients over the WebSocket are forwarded to the OVOS core bus
unchanged. This allows Qt GUI interactions (button presses, text input) to reach skills
as normal bus events.

---

## Summary: message flow

```python
Skill call:   self.gui.show_text("Hello", title="Greeting")
  → bus:      gui.value.set            (skill namespace data)
  → bus:      gui.page.show            (SYSTEM_TextFrame)
  → ovos-gui: NamespaceManager records page + data on the namespace
  → WS:       mycroft.session.list.insert (namespace into active stack)
  → WS:       mycroft.gui.list.insert     (SYSTEM:TextFrame.qml)
  → WS:       mycroft.session.set         (sync data to Qt)
  → Qt client renders the page

User swipes / taps on Qt:
  → WS → bus: gui.page_gained_focus / gui.page_interaction (skill_id, page_number)
  → ovos-gui updates focused page and reschedules namespace timeout
```

---

!!! warning "Upcoming: unreleased"
    In the GUI-rework, specified by the
    [OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md) spec
    (see [GUI Service](gui-service.md)), the bus contract changes:

    - `gui.page.show` will accept **only** `SYSTEM_*` template names. Custom QML pages are no
      longer supported.
    - Instead of mirroring to Qt clients directly, template events fan out to every loaded
      `opm.gui_adapter` plugin (see [GUI Adapter Plugins](gui-adapters.md)). The Qt WebSocket
      protocol on this page becomes one such adapter.

    None of this is implemented in `ovos-gui` yet. See
    [GUI Adapter Plugins](gui-adapters.md) for what the adapter plugins being built ahead of
    this rework have already settled on.

---
**Read next:** [OVOS Shell](ovos-shell.md)
**Related:** [GUI Protocol](gui-protocol.md) · [GUI Service (legacy)](gui-service.md) · [Screens on OVOS Today](gui-status.md)
