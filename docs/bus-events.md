# Bus Events Reference

!!! abstract "In a nutshell"
    Every OVOS component talks to every other one by sending small named messages over the
    shared [messagebus](bus-service.md). It works a bit like a group chat where each service
    watches for the message types it cares about. This page collects the message types
    documented elsewhere in the manual into one place, grouped by which stage of the
    [utterance lifecycle](life-of-an-utterance.md) they belong to, so you don't have to hunt
    through six different pages to find one event name. Each row links back to the page that
    documents that event in context. This page does not introduce anything new.

!!! tip "Looking for a message this page does not list?"
    This page is curated. It covers the events the manual explains in context, not every event
    that exists. For the exhaustive machine-generated catalog, browse the
    [MessageBus Protocol Reference](https://openvoiceos.github.io/ovos-pydantic-models/), built
    from [`ovos-pydantic-models`](core-libraries.md#ovos-pydantic-models). It is searchable and
    grouped by subsystem, and it includes deprecated subsystems that this page leaves out.

    Its models are generated semi-automatically from source, so entries can be incomplete or out
    of date. Check the behavior against the code or the
    [formal specifications](architecture-specs.md) before you depend on it.

!!! note
    Many events have a legacy `mycroft.*`/bare name alongside a newer `ovos.*` name. Only
    one of the two goes on the wire, and each connected client's bus library locally
    re-dispatches it under the other name too, so a handler on either name receives it
    (see [Bus Service: namespace migration](bus-namespace-migration.md#namespace-migration)). Use the
    spec name in new code: an open kill-switch pull request
    ([ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272))
    removes the legacy bridge once the fleet has migrated. The tables below show both
    names where applicable.

## Listener / wake word

Emitted by `ovos-dinkum-listener` as the audio pipeline runs. See
[Speech Service](speech-service.md) for the full lifecycle.

| Event | Data | Meaning |
|---|---|---|
| `ovos.listener.record.started` (legacy: `recognizer_loop:record_begin`) | none | Command recording started |
| `ovos.listener.record.ended` (legacy: `recognizer_loop:record_end`) | none | Command recording ended |
| `ovos.listener.wakeword` (legacy: `recognizer_loop:wakeword`) | `{"wake_word", "lang"}` | Wake word detected, capture is opening. `lang` is optional and only present when the deployment binds wake words to languages |
| `recognizer_loop:speech.recognition.unknown` | none | STT returned nothing (silence / failure) |
| `ovos.listener.sleep` | none | Request the listener enter sleep mode and suspend capture: device-scoped, see [Speech Service](speech-service.md) |
| `ovos.listener.awoken` (legacy: `mycroft.awoken`) | none | Listener woke from sleep |

## STT / utterance entry point

| Event | Data | Meaning |
|---|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `{"utterances": [str], "lang"}` | Transcribed command enters the pipeline: see [Life of an Utterance](life-of-an-utterance.md) and [Intent Service](intent-service.md#bus-events-handled) |
| `ovos.utterance.handled` | none | Universal utterance-lifecycle end-marker. See [Bus Service](bus-service.md#core-intent-pipeline) |

## Intent matching & context

Handled by `ovos-core`'s `IntentService`. See [Intent Service](intent-service.md#bus-events-handled).

| Event | Handler | Meaning |
|---|---|---|
| `ovos.utterance.handle` (legacy: `recognizer_loop:utterance`) | `handle_utterance` | Run an utterance through the pipeline |
| `add_context` / `remove_context` / `clear_context` | `handle_add_context` / `handle_remove_context` / `handle_clear_context` | Manage [intent context](context.md) |
| `intent.service.intent.get` | `handle_get_intent` | Query the best-matching intent without dispatching it |
| `intent.service.skills.deactivate` | `_handle_deactivate` | Remove a skill from active/converse consideration |
| `intent.service.pipelines.reload` | `handle_reload_pipelines` | Reload the configured pipeline plugin stack |
| `ovos.intent.unmatched` (legacy: `complete_intent_failure`) | none | No pipeline stage claimed the utterance, including the [fallback](fallback-pipeline.md) stages, which run *inside* the match loop. This is the terminal "nothing handled it" marker, not a hand-off |

`IntentService` also **emits** these on a successful match, in order (see [Intent Service](intent-service.md#intent-match-emission)):

| Event | Meaning |
|---|---|
| `{skill_id}.activate` | Mark the matched skill active in the session |
| `ovos.intent.matched` | A pipeline plugin claimed the utterance (notification) |
| `<skill_id>:<intent_name>` | The dispatch message that invokes the winning skill's intent handler |
| `ovos.intent.handler.start` → `ovos.intent.handler.complete` / `ovos.intent.handler.error` | The orchestrator-owned handler-lifecycle trio around the invocation (§8, **not** translator-bridged, see [Legacy ↔ spec migration](#legacy-spec-migration)). The skill framework separately emits the legacy `mycroft.skill.handler.start` / `.complete` as a private done-signal. There is no legacy `.error`: the explicit error leg is spec-side only |

### Converse

See [Converse Pipeline](converse-pipeline.md#bus-events-handled) for the full picture.

| Event | Handler | Meaning |
|---|---|---|
| `intent.service.skills.activate` | `handle_activate_skill_request` | Add a skill to the converse-eligible list |
| `intent.service.skills.deactivate` | `handle_deactivate_skill_request` | Remove a skill from the converse-eligible list |
| `intent.service.active_skills.get` | `handle_get_active_skills` | Query the current converse-eligible list |
| `skill.converse.get_response.enable` / `.disable` | `handle_get_response_enable` / `handle_get_response_disable` | Toggle the `get_response` window for a skill |
| `converse:skill` | `handle_converse` | Dispatch an utterance to an active skill's `converse` |
| `{skill_id}.converse.get_response` | none | Feed the user's reply back into a pending `get_response` (see [OVOSSkill API](ovos-skill.md#system-bus-events-handled-per-skill)) |

### Common Query

See [Common Query Pipeline](cq-pipeline.md).

| Event | Meaning |
|---|---|
| `question:query` | Common query pipeline request broadcast to all skills |
| `ovos.common_query.ping` | Common query service discovery |
| `question:action.{skill_id}` | Callback: this skill's answer was selected |
| `question:action` | Callback: some skill's answer was selected (generic) |

### Fallback

See [Fallback Pipeline](fallback-pipeline.md#bus-events-handled).

| Event | Handler | Meaning |
|---|---|---|
| `ovos.skills.fallback.register` | `handle_register_fallback` | Register a skill as a fallback handler |
| `ovos.skills.fallback.deregister` | `handle_deregister_fallback` | Remove a fallback handler |
| `ovos.skills.fallback.ping` | `_handle_fallback_ack` (skill-side) | Fallback service asks every registered skill whether it can handle the utterance |
| `ovos.skills.fallback.pong` | `handle_ack` (service-side) | A skill's reply to the ping, `can_handle` true/false |
| `ovos.skills.fallback.{skill_id}.request` | `_handle_fallback_request` (skill-side) | Service asks one specific skill to actually process the utterance |

## Skill lifecycle

Handled by every `OVOSSkill` instance. See [OVOSSkill API](ovos-skill.md#system-bus-events-handled-per-skill).

| Event | Meaning |
|---|---|
| `ovos.stop` (legacy: `mycroft.stop`) | Global stop broadcast: every skill subscribes and ceases activity for the inbound session (see below). Only this pair is translator-bridged |
| `<skill_id>:stop` (legacy: `{skill_id}.stop`) | Skill-directed stop dispatch. **Dual-subscribed, not translator-bridged**: the skill base class listens on both forms itself (the per-skill `{skill_id}.*` shape can't be a static map key) |
| `ovos.stop.ping` (legacy: `{skill_id}.stop.ping`) | Check whether this skill can stop. Also **dual-subscribed, not translator-bridged** (see the [Not bridged](#not-bridged-adopt-the-spec-directly) note) |
| `mycroft.skill.enable_intent` / `mycroft.skill.disable_intent` | Enable/disable one of the skill's intents |
| `mycroft.skill.set_cross_context` / `mycroft.skill.remove_cross_context` | Manage cross-skill context |
| `mycroft.skills.settings.changed` | Remote settings update: see [Skill Settings](skill-settings.md#change-callback) for the full change-notification flow |
| `ovos.skills.settings_changed` | Local settings file changed: see `settings_change_callback` in [Skill Settings](skill-settings.md#change-callback) ([Skill Cookbook recipe 2](recipe-reactive-settings.md)) for reacting to it from a skill |
| `homescreen.metadata.get` | Homescreen requesting metadata |
| `{skill_id}.public_api` | Skill API introspection (see [Skill API: Inter-Skill RPC](skill-api.md)) |

### Stop pipeline

`ovos.stop` and the per-skill stop handshake above are driven by the dedicated
[Stop Pipeline](stop-pipeline.md#bus-events) plugin, not by a generic intent match:

| Event | Direction | Meaning |
|---|---|---|
| `<pipeline_id>:global_stop` (legacy: `stop:global`) | in | Global-stop dispatch: its handler emits the `ovos.stop` broadcast (and `ovos.utterance.handled`) |
| `<skill_id>:stop` (legacy: `stop:skill` → `{skill_id}.stop`) | out | Targeted stop dispatch to one skill |
| `ovos.stop.ping` (legacy: `{skill_id}.stop.ping`) | out | Asks the active handlers whether they can stop |
| `ovos.stop.pong` (legacy: `skill.stop.pong`) | in | Handler's `can_handle` reply |
| `ovos.stop` (legacy: `mycroft.stop`) | out | Universal stop broadcast |

## TTS / audio playback

Handled by `ovos-audio`. See [Audio Service](audio-service.md).

| Event | Meaning |
|---|---|
| `ovos.utterance.speak` (legacy: `speak`) | Natural-language response to synthesize and play: the exit point of the utterance lifecycle |
| `mycroft.audio.queue` | Queue a sound effect / audio file for playback (see [`play_audio`](ovos-skill.md#playing-audio-files)) |
| `mycroft.audio.play_sound` | Play a sound effect / audio file instantly |
| `mycroft.audio.speech.stop` | Interrupt in-progress TTS speech (emitted by the [`@intent_handler(..., stop_tts=True)`](decorators.md) decorator, among others) |
| `mycroft.audio.service.play` | Legacy media audioservice: play a track (only relevant when `enable_old_audioservice` is on) |
| `recognizer_loop:utterance_start` | Emitted by the playback thread right before spoken audio starts playing |
| `recognizer_loop:audio_output_start` (spec: `ovos.audio.output.started`) | Emitted by the playback thread when audio actually starts playing |
| `recognizer_loop:audio_output_end` (spec: `ovos.audio.output.ended`) | Emitted by the playback thread when audio finishes playing |

## GUI forwarding

Handled by `ovos-gui`. See [GUI Service](gui-service.md).

| Event | Meaning |
|---|---|
| `gui.value.set` | Write session variables into a skill's GUI namespace |
| `gui.page.show` | Request one or more QML/HTML pages be shown |
| `gui.page.delete` / `gui.page.delete.all` | Remove page(s) from the namespace |
| `gui.event.send` | Send a custom event into the namespace |
| `gui.clear.namespace` | Remove a skill's namespace from the active GUI stack |

## OCP / media playback

Handled by `ovos-media`'s `MediaService`/`OCPPlayer` and the `ovos-ocp-pipeline-plugin`
intent pipeline. All topics live under the `ovos.common_play.*` namespace, there is no
legacy alias for this surface.

| Event | Direction | Meaning |
|---|---|---|
| `ovos.common_play.search` | in | Pipeline plugin asks OCP to search for playable media |
| `ovos.common_play.play_search` | in | Skill dispatch label for a matched "play X" intent |
| `ovos.common_play.play` | in | Start playback of a track or playlist |
| `ovos.common_play.pause` | in | Pause playback |
| `ovos.common_play.play_pause` | in | Toggle play/pause |
| `ovos.common_play.resume` | in | Resume paused playback |
| `ovos.common_play.stop` | in | Stop playback |
| `ovos.common_play.next` / `.previous` | in | Skip to next/previous track |
| `ovos.common_play.seek` | in | Seek within the current track |
| `ovos.common_play.get_track_length` / `.get_track_position` / `.set_track_position` | in | Query or set playback position |
| `ovos.common_play.track_info` | in | Query metadata for the current track |
| `ovos.common_play.playlist.set` / `.clear` / `.queue` | in | Manage the active playlist |
| `ovos.common_play.shuffle.toggle` / `.set` / `.unset` | in | Manage shuffle mode |
| `ovos.common_play.repeat.toggle` / `.set` / `.unset` | in | Manage repeat mode |
| `ovos.common_play.duck` / `.unduck` / `.cork` / `.uncork` | in | Manage playback ducking around TTS/other audio |
| `ovos.common_play.status` | in | Request a player state sync (also emitted by OCP itself on launch) |
| `ovos.common_play.status.response` | out | Reply to `.status`, carries current player state |
| `ovos.common_play.track.state` | out | `{"state": TrackState}` playback state changed (loading, playing audio/video, paused, ended) |
| `ovos.common_play.media.state` | out | Low-level backend media state changed |
| `ovos.common_play.home` | in | Request the OCP home/media browser view |
| `ovos.common_play.ping` / `.pong` | in/out | OCP service discovery handshake |
| `ovos.common_play.search.start` / `.search.end` | out | Marks the start/end of a search request |
| `ovos.common_play.announce` | in | A skill registers itself as an OCP media provider |
| `ovos.common_play.register_keyword` / `.deregister_keyword` | in | A skill registers/removes its media-type keywords for the pipeline plugin |
| `ovos.common_play.skills.detach` | in | Remove a skill from the OCP provider list |
| `ovos.common_play.SEI.get` / `.SEI.get.response` | out/in | Query a client's available stream extractor plugins |
| `ovos.common_play.like` / `.unlike` | in | Mark/unmark the current track as liked |
| `ovos.common_play.liked_tracks.play` | out | Play the liked-tracks playlist |

## PHAL (hardware abstraction)

Handled by the PHAL service (`ovos-PHAL`) and its plugins. See [PHAL](phal.md).

| Event | Direction | Meaning |
|---|---|---|
| `system.reboot` | in | Request a device reboot, handled by `ovos-PHAL-plugin-system` |
| `system.reboot.start` | out | Reboot is starting |
| `system.shutdown` | in | Request a device shutdown |
| `system.shutdown.start` | out | Shutdown is starting |
| `system.factory.reset` | in | Request a factory reset |
| `system.factory.reset.register` | in | A plugin registers itself as a factory-reset participant |
| `system.factory.reset.ping` | out | Ask registered plugins to run their factory-reset step |
| `system.configure.language` | in | Request a device-wide language change |
| `system.configure.language.complete` | out | Language change finished |
| `system.mycroft.service.restart` | in | Request `ovos-core` be restarted |
| `system.mycroft.service.restart.start` | out | `ovos-core` restart is starting |
| `system.ssh.enable` / `.disable` | in | Enable/disable the SSH server |
| `system.ssh.enabled` / `.disabled` | out | SSH server state changed |
| `system.ssh.status` | in | Query SSH server state |
| `system.clock.synced` | in | System clock finished syncing over NTP |

Every `PHALPlugin` subclass also listens on the same core listener/audio topics documented
above (`recognizer_loop:record_begin`, `recognizer_loop:audio_output_start`,
`mycroft.awoken`, `speak`, and the `enclosure.*` display/eyes/mouth topics), so a PHAL
plugin can react to the utterance lifecycle without going through a skill.

## Volume / mute

Handled by `ovos-PHAL-plugin-alsa` and `ovos-PHAL-plugin-pulseaudio` (whichever is loaded
for the platform's audio stack). `ovos-audio` also emits `mycroft.volume.*` on its own
startup to normalize the initial volume.

| Event | Direction | Meaning |
|---|---|---|
| `mycroft.volume.get` | in/out | Query current volume; the same topic carries the reply as a response message with `{"percent"}` |
| `mycroft.volume.set` | in | Set volume to `{"percent"}` |
| `mycroft.volume.set.gui` | in | Set volume from a GUI slider |
| `mycroft.volume.increase` | in | Raise volume by a step |
| `mycroft.volume.decrease` | in | Lower volume by a step |
| `mycroft.volume.mute` | in | Mute audio output |
| `mycroft.volume.unmute` | in | Unmute audio output |
| `mycroft.volume.mute.toggle` | in | Toggle mute state |
| `mycroft.volume.get.sliding.panel` | in | Query volume for the GUI sliding panel |

## Session & skill management

See [Bus Service: common message types](bus-service.md#key-message-categories).

| Event | From | To |
|---|---|---|
| `mycroft.skills.initialized` | `ovos-core` | GUI clients, tools |
| `skillmanager.list` | any client | `ovos-core` |
| `ovos.skills.install` | any client | `ovos-core` |
| `ovos.session.sync` | new client | `ovos-core` |
| `ovos.session.update_default` | `ovos-core` | all clients |
| `mycroft.network.connected` / `mycroft.internet.connected` | `ovos-PHAL` | `ovos-core`, skills |

## Legacy ↔ spec migration

OVOS is renaming its bus topics onto the `ovos.*` spec namespace. During the migration,
`ovos-bus-client`'s receive-side bridge makes legacy and spec names interchangeable, both
directions on by default (see
[Bus Service: namespace migration](bus-namespace-migration.md#namespace-migration)). That bridge is
scheduled for removal by the open kill-switch pull request
[ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272): after it
merges, only the spec names work. Use the table below to move any legacy name in your
code to its spec name ahead of that.

The pairs below are the authoritative rename map (`ovos_spec_tools`'s `MIGRATION_MAP`). Unless
marked **shape-changing**, the payload is identical on both topics. Shape-changing pairs are
reshaped best-effort by the translator and may lose fields, so prefer adopting the spec payload
directly.

| Legacy topic | Spec topic | Notes |
|---|---|---|
| `recognizer_loop:utterance` | `ovos.utterance.handle` | transcribed utterance (PIPELINE-1 §9.1) |
| `speak` | `ovos.utterance.speak` | TTS request (PIPELINE-1 §9.6) |
| `speak:b64_audio` | `ovos.utterance.speak.b64` | inline-audio speak request, handled by `ovos-audio`'s `handle_b64_audio` |
| `speak:b64_audio.response` | `ovos.audio.speech` | synthesized-audio reply |
| `recognizer_loop:audio_output_start` | `ovos.audio.output.started` | playback began (AUDIO-1 §5.1) |
| `recognizer_loop:audio_output_end` | `ovos.audio.output.ended` | playback ended (AUDIO-1 §5.2) |
| `mycroft.audio.queue` | `ovos.audio.queue` | enqueue a sound `{uri}` |
| `mycroft.audio.play_sound` | `ovos.audio.play_sound` | play a sound effect `{uri}` |
| `mycroft.audio.speak.status` | `ovos.audio.is_speaking` | query: is audio-out active |
| `mycroft.audio.speech.stop` | `ovos.audio.stop` | stop audio output |
| `mycroft.mic.listen` | `ovos.mic.listen` | force the listener to start listening (AUDIO-1 §4.4) |
| `recognizer_loop:record_begin` | `ovos.listener.record.started` | command recording started (AUDIO-IN-1 §6.1) |
| `recognizer_loop:record_end` | `ovos.listener.record.ended` | command recording ended (AUDIO-IN-1 §6.2) |
| `recognizer_loop:sleep` | `ovos.listener.sleep` | put listener to sleep (AUDIO-IN-1 §6.3) |
| `mycroft.awoken` | `ovos.listener.awoken` | listener woke from sleep (AUDIO-IN-1 §6.4) |
| `mycroft.stop` | `ovos.stop` | universal stop broadcast (STOP-1 §5.3) |
| `skill.stop.pong` | `ovos.stop.pong` | stoppability reply (STOP-1 §4.2) |
| `complete_intent_failure` | `ovos.intent.unmatched` | no intent claimed the utterance (PIPELINE-1 §9.3) |
| `detach_skill` | `ovos.skill.deregister` | remove a skill's intents `{skill_id}` |
| `detach_intent` | `ovos.intent.deregister` | **shape-changing**: remove one intent (INTENT-4 §8.2) |
| `mycroft.skill.enable_intent` | `ovos.intent.enable` | **shape-changing**: enable an intent (INTENT-4 §8.5) |
| `mycroft.skill.disable_intent` | `ovos.intent.disable` | **shape-changing**: disable an intent (INTENT-4 §8.5) |

### Not bridged: adopt the spec directly

A few areas are deliberately **not** in the translator, so subscribing on the spec name alone will
*not* transparently receive the legacy traffic, or the other way around. These need real adoption
in the producer and consumer, not a topic swap:

- **Handler-lifecycle trio.** `mycroft.skill.handler.start` / `.complete` are orchestrator-vs-skill
  private signals. The orchestrator emits the spec `ovos.intent.handler.start` / `.complete` /
  `.error` directly. The two namespaces are kept separate by design (PIPELINE-1 §8/§11). The pair
  is shape-changing, and bridging would double-emit.
- **Intent/entity registration.** `register_vocab` + `register_intent` (Adapt's N legacy messages)
  do not map 1:1 onto the single `ovos.intent.register.keyword` / `.register.template` /
  `ovos.entity.register` message (INTENT-4 §5), which inlines the vocab descriptors. This requires
  producers and consumers to adopt INTENT-4, not a rename.
- **Per-skill stop.** The legacy `{skill_id}.stop` / `{skill_id}.stop.ping` handshake uses
  runtime-assembled per-skill topics, which cannot be static map keys. STOP-1 replaces them with the
  broadcast `ovos.stop` / `ovos.stop.ping` / `ovos.stop.pong`. The skill base class subscribes on
  both forms rather than relying on the translator.

---
**Read next:** [Command-line Tools](cli-tools.md)
**Related:** [Bus Service](bus-service.md) · [Life of an Utterance](life-of-an-utterance.md) · [Intent Service](intent-service.md) · [OVOSSkill API](ovos-skill.md)
