# Upcoming Changes

!!! abstract "In a nutshell"
    This page tracks open pull requests across the OVOS repositories that will
    change behavior once merged. Everything on this page is **unreleased and
    subject to change**: PR scope, target version, and even whether a PR lands
    at all can shift before release. Once a PR merges or closes, its content
    graduates to [Updating from Older OVOS](updating-from-older-ovos.md), which
    tracks shipped history. If a PR number below is already merged or closed by
    the time you read this, treat this page as stale for that entry and check
    the linked PR directly.

## The new GUI

[OVOS-GUI-1](architecture-specs.md) is a ground-up rework of how OVOS renders a
screen: interchangeable render-backend plugins instead of one built-in
WebSocket/QML renderer. See [Screens on OVOS Today](gui-status.md) for the full
picture. Until this work lands, the current GUI stack (`ovos-gui` +
`ovos-shell` + `mycroft-gui-qt5`) stays **deprecated but shipped**, since it is
the only screen stack that runs today.

- [ovos-gui#112](https://github.com/OpenVoiceOS/ovos-gui/pull/112): feat: land
  GUI adapter/template rework (session_id-only). Converts `ovos-gui` into a
  pure state/dispatch hub with no built-in renderer: every installed
  `opm.gui_adapter` plugin gets the `SYSTEM_*` template events, and a device
  with none installed runs headless instead of crashing. Drops `site_id`
  routing in favor of `session_id`-only addressing, and changes the
  adapter-plugin hook signatures. **Breaking.** Audience: deployers/integrators
  (an `opm.gui_adapter` plugin becomes required for any screen output),
  GUI-adapter plugin authors, skill authors relying on `site_id` routing.
  Expected 2.0.0 (unreleased). Blocked on `ovos-plugin-manager#377` and
  `ovos-legacy-mycroft-gui-plugin@dev` publishing to PyPI first.
- [ovos-gui#117](https://github.com/OpenVoiceOS/ovos-gui/pull/117): feat:
  OVOS-GUI-1 service conformance. Adds the `SYSTEM_` template-name gate, accepts
  both legacy CamelCase and GUI-1 frame names, and partitions display state per
  session, all without touching the legacy render path. Not breaking, additive
  on top of `dev`. Audience: skill authors emitting GUI pages, GUI-adapter
  authors, multi-session deployers. Expected 1.5.0 (unreleased).
- [ovos-plugin-manager#377](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/377): feat: AbstractGUIPlugin. The adapter base class ovos-gui#112 needs: an
  extensible GUI-adapter framework covering text, image, video, audio, weather,
  map, and interactive display types. Not breaking, a new abstraction. Audience:
  GUI-adapter plugin authors, OVOS-GUI integrators. Expected 2.12.0 (unreleased).
  This is the unreleased branch ovos-gui#112 is blocked on.
- [ovos-plugin-manager#406](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/406): refactor!: drop the enclosure abstraction from PHALPlugin. Removes the
  legacy Mark-1 `enclosure.*` protocol wiring from `PHALPlugin`. The listener
  side moves to `ovos-ui-enclosure-protocol`, the producer side to
  `ovos-gui-api-client`. **Breaking** for any PHAL plugin subclass using the
  removed handlers. Audience: PHAL/enclosure hardware plugin authors, GUI/
  enclosure integration maintainers. Expected 3.0.0 (unreleased). Part of the
  same enclosure-to-GUI migration as the rest of this section.
- [ovos-bus-client#238](https://github.com/OpenVoiceOS/ovos-bus-client/pull/238): fix: emit GUI-1-conformant wire shapes from GUIInterface. `gui.value.set`
  and `gui.page.show` stop emitting null-valued keys, and local image paths get
  base64-encoded into a data URI instead of a bare filesystem path. Not
  breaking, narrows the wire shape toward the spec. Audience: GUI render-backend
  implementers and other consumers of the GUI wire protocol. Expected 2.7.3
  (unreleased).
- [ovos-bus-client#197](https://github.com/OpenVoiceOS/ovos-bus-client/pull/197): refactor!: deprecate EnclosureAPI, refactor GUIInterface with a
  `PageTemplates` enum. Marks `EnclosureAPI` for deprecation (visual output
  moves to platform plugins), removes a `GUIInterface` init parameter, and
  replaces string-based GUI page-template references with `PageTemplates`
  constants. **Breaking** for direct `GUIInterface` instantiators. Audience:
  consumers of `EnclosureAPI` and `GUIInterface`. Expected 3.0.0 (unreleased).
- [ovos-workshop#420](https://github.com/OpenVoiceOS/ovos-workshop/pull/420): feat!: bind `OVOSSkill.gui` to `ovos-gui-api-client`. Points skill GUI access
  at the standalone `ovos-gui-api-client` package. `SkillGUI.__init__` drops the
  `ui_directories` argument, since skills no longer ship QML. **Breaking** for
  skill authors constructing `SkillGUI`/`GUIInterface` directly. Audience: skill
  authors. Expected 10.0.0 (unreleased).
- [ovos-workshop#421](https://github.com/OpenVoiceOS/ovos-workshop/pull/421): feat!: remove the skill-side home/resting-screen API. Deletes
  `resting_screen_handler`, `homescreen_app`, `IdleDisplaySkill`, and
  `register_resting_screen`/`register_homescreen_app`, since OVOS-GUI-1 §6.9
  treats the resting display as a render-backend concern, not a skill concern.
  **Breaking** for any skill using these decorators/methods. Audience: skill
  authors. Named downstream impact on `ovos-ocp-audio-plugin`,
  `ovos-skill-iss-location`, `ovos-pydantic-models`, `ovos-skill-homescreen`.
  Expected 10.0.0 (unreleased).

## ovos-media

`ovos-media` is **alpha and not officially released**. `ovos-audio` remains
the production audio service, and stock installs keep
`enable_old_audioservice: true` (the default). See
[Media Service (ovos-media)](ovos-media.md) for its maturity status. Two
things are changing on top of that baseline: the legacy audio service is
starting to shed its OCP integration, and the intended role of an OCP skill is
shifting.

MediaProvider plugins (`opm.media.provider`) are meant to own catalog search
once `ovos-media` loads them in-process. OCP skills stay fully supported, but
their intended role narrows: a skill whose job is "answer catalog search
queries" (a station list, a podcast feed) is expected to become a
MediaProvider plugin over time, while a skill where **the skill itself is the
playable media** (a voice game, an ebook reader) stays an OCP skill. See
[OCP Skills](ocp-skills.md) for the full split.

- [ovos-workshop#423](https://github.com/OpenVoiceOS/ovos-workshop/pull/423): feat: deprecate `OVOSCommonPlaybackSkill` in favor of MediaProvider plugins.
  Adds a deprecation notice to `OVOSCommonPlaybackSkill.__init__` steering
  authors toward `opm.media.provider`. Not breaking: existing OCP skills keep
  working, and hard removal is a future major version. Audience: OCP skill
  authors. Expected 9.4.0 (unreleased).
- [ovos-workshop#428](https://github.com/OpenVoiceOS/ovos-workshop/pull/428): feat: session-aware game-skill + OCP playback. Makes
  `OVOSCommonPlaybackSkill` playback state per-session, so state events route
  back to the originating session instead of colliding across simultaneous
  sessions. This is the piece that keeps a game-as-OCP-skill correct under
  HiveMind/remote deployments. Not breaking. Audience: OCP/game-skill authors,
  HiveMind/remote deployers. Expected 9.4.0 (unreleased). Stacked on
  ovos-workshop#427, must merge first.
- [ovos-audio#115](https://github.com/OpenVoiceOS/ovos-audio/pull/115): refactor!: drop OCP. Removes OCP (OVOS Common Playback) integration from
  `ovos-audio` entirely, leaving only the legacy audio system: drops the
  `disable_ocp` constructor parameter and the `ovos_plugin_common_play[extractors]`
  dependency. **Breaking** for anything relying on OCP inside `ovos-audio`.
  Audience: skill authors and deployers relying on OCP integration inside
  `ovos-audio`, plugin authors depending on the removed constructor parameter.
  Expected 3.0.0 (unreleased).

## Official spec adoption

Repositories across the org are being brought into conformance with the
[Formal Specifications](architecture-specs.md), largely OVOS-STOP-1,
OVOS-CONTEXT-1, OVOS-TRANSFORM-1, and OVOS-PIPELINE-1. A related but separate
effort, the legacy bus-namespace migration, already completed its removal
phase for `ovos-bus-client`'s own namespace bridge (see
[Updating from Older OVOS](updating-from-older-ovos.md)). The PRs below carry
that migration the rest of the way: a set of coordinated kill-switches that
drop the last hardcoded legacy topic literals from `ovos-core`, `ovos-workshop`,
and the `ovos-utils` test double. Each is explicitly gated to merge only once
fleets no longer run legacy-namespace consumers.

- [ovos-core#802](https://github.com/OpenVoiceOS/ovos-core/pull/802): feat!:
  OVOS-STOP-1 reserved-intent_name dispatch + separable legacy bridge.
  Reworks the stop pipeline as a single spec path: targeted stop dispatches
  `<skill_id>:stop`, global stop dispatches `<pipeline_id>:global_stop` and a
  single `ovos.stop` broadcast. Legacy stop back-compat moves into a
  separately deletable module. **Breaking**: the dispatch topic shape for
  targeted stop changes. Audience: skill authors handling stop intents,
  deployers running legacy skills, remote/HiveMind bus consumers of stop
  topics. Expected 3.0.0 (unreleased). Requires
  `ovos-plugin-manager>=2.9.0a1`. Supersedes ovos-core#777 below.
- [ovos-core#777](https://github.com/OpenVoiceOS/ovos-core/pull/777): feat:
  OVOS-STOP-1 conformance in stop_service. Adopts the OVOS-STOP-1 spec bus
  surface (`ovos.stop`, `ovos.stop.pong`, `ovos.stop.ping`) bridged to legacy
  topics via `ovos-spec-tools`. Not breaking. **Superseded by ovos-core#802**,
  which extends and completes this work. Treat #777 as likely to be closed in
  favor of #802 rather than merged separately. Expected 2.6.0 (unreleased).
- [ovos-core#786](https://github.com/OpenVoiceOS/ovos-core/pull/786): feat:
  OVOS-CONTEXT-1 orchestrator-resident intent context. Implements the
  core-resident half of OVOS-CONTEXT-1: a flat, decaying
  `session.intent_context` store with private/shared scope resolution and
  `requires_context`/`excludes_context` gating. Not breaking, additive. The
  legacy frame-based context manager stays for back-compat. Audience: skill
  authors declaring context requirements, remote/HiveMind session-sync
  consumers. Expected 2.6.0 (unreleased).
- [ovos-core#785](https://github.com/OpenVoiceOS/ovos-core/pull/785): fix:
  conform transformer chains to OVOS-TRANSFORM-1. Adds `cancel_reason`/
  `cancel_by` to `ovos.utterance.cancelled`, and moves the bulk of
  transform-chain conformance logic upstream into `ovos-plugin-manager`'s
  shared `TransformersService` bases. Not breaking. Audience: utterance/
  metadata/intent transformer plugin authors. Expected 2.5.9 (unreleased).
  Depends on `ovos-plugin-manager#417` landing first, and bumps the
  `ovos-plugin-manager` floor to `>=2.10.3a1`.
- [ovos-workshop#500](https://github.com/OpenVoiceOS/ovos-workshop/pull/500): refactor: register canonical intent topics, compat moves to
  ovos-spec-tools. `register_intent_file` now derives its topic from
  `canonical_intent_topic()` instead of the raw `.intent` filename, dropping
  the previous dual-bind on both spellings. Not marked breaking, but removes a
  runtime behavior (the dual bind). Audience: skill authors subscribed
  directly to the `.intent`-suffixed dispatch topic, deployers running mixed
  old/new skill containers. Expected 9.4.0 (unreleased).
- [ovos-workshop#414](https://github.com/OpenVoiceOS/ovos-workshop/pull/414): refactor: route `OVOSSkill` resource loading through `ovos-spec-tools`
  (back-compat). Routes resource access through
  `ovos_spec_tools.LocaleResources` internally. Every legacy resource-loading
  call (`self.resources`, `self.find_resource`, etc.) keeps working via a
  compatibility mixin that emits one `DeprecationWarning` per call. Not
  breaking. Audience: skill authors using the legacy resource-loading API.
  Expected 9.3.3 (unreleased).
- [ovos-persona#192](https://github.com/OpenVoiceOS/ovos-persona/pull/192): fix: emit PIPELINE-1 §8 done-signal for persona dispatches. Registers
  persona's `persona:*` intent handlers with `handler_info`, so the PIPELINE-1
  §9.5 `ovos.utterance.handled` end-marker fires promptly after a
  persona-handled utterance instead of only after a 5-minute dispatcher
  timeout. Not breaking, restores expected framework behavior. Audience:
  skill/pipeline authors and deployers on `ovos-core>=2.3.0a1`. Expected 0.9.1
  (unreleased).
- [ovos-bus-client#271](https://github.com/OpenVoiceOS/ovos-bus-client/pull/271): feat: legacy intent-topic bridge, wire twin on emit, modernize on
  receive. Adds a two-rule bridge covering version-skew on the
  `.intent`-suffixed dispatch topic between old and new workshop/core
  versions. Not breaking, additive. Audience: deployers running mixed-version
  fleets. Expected 2.8.0 (unreleased). This is the compat layer #272 below
  later removes.
- [ovos-utils#411](https://github.com/OpenVoiceOS/ovos-utils/pull/411): feat: `FakeBus` mirrors the `.intent`-suffixed twin for aliased intents.
  Gives `FakeBus`/`AsyncFakeBus` the same bridge ovos-bus-client#271 added to
  the real client, so test harnesses built on `FakeBus` don't hide the compat
  path. Not breaking, additive test-double parity fix. Audience: test-harness
  authors (ovoscope, skill test suites). Expected 0.14.0 (unreleased).
- [ovos-bus-client#272](https://github.com/OpenVoiceOS/ovos-bus-client/pull/272): feat!: drop legacy wire compat (kill-switch). Removes the namespace
  bridge, the handler mirror-guard, and the intent-topic twin from
  `MessageBusClient` entirely. A client constructed with a removed compat
  flag raises `RuntimeError` instead of silently no-op-ing. **Breaking.**
  Audience: deployers/operators with legacy-namespace consumers still on the
  fleet, any code constructing `MessageBusClient` with the removed compat
  flags. Expected 3.0.0 (unreleased). Must merge together with ovos-core#837,
  ovos-workshop#501, and ovos-utils#412. Depends on #271. Explicitly
  "do not merge until then."
- [ovos-core#837](https://github.com/OpenVoiceOS/ovos-core/pull/837): feat!:
  drop legacy wire compat (kill-switch). Removes the last legacy-topic
  literals `ovos-core` still writes on the wire, replacing them with
  `SpecMessage` constants. **Breaking.** Audience: deployers with un-migrated
  legacy-bus consumers, skill/plugin authors listening on the legacy
  spellings. Expected 3.0.0 (unreleased). Must merge together with the other
  three kill-switch PRs in this list.
- [ovos-workshop#501](https://github.com/OpenVoiceOS/ovos-workshop/pull/501): feat!: drop legacy wire compat (kill-switch). Rewrites every remaining
  legacy-topic literal `ovos-workshop` still emits/listens on to the
  `SpecMessage`-based canonical form. **Breaking.** Audience: deployers with
  un-migrated legacy-bus consumers, skill authors subscribing to legacy topic
  names directly. Expected 10.0.0 (unreleased). Depends on #500 above. Must
  merge together with the other three kill-switch PRs in this list.
- [ovos-utils#412](https://github.com/OpenVoiceOS/ovos-utils/pull/412): feat!: drop legacy wire compat (kill-switch). The `FakeBus`/`AsyncFakeBus`
  test-double half of the same drop: removes the namespace bridge and the
  intent-topic twin from the test double. **Breaking.** Audience: test-harness
  authors (ovoscope, skill test suites, satellite fakes) using `FakeBus` with
  the legacy-compat flags. Expected 1.0.0 (unreleased): this would also be
  the package's first stable 1.0 release. Depends on #411. Must merge
  together with the other three kill-switch PRs in this list.

## Other changes by repository

Entries here are open PRs that change behavior but don't fit the three
headline efforts above.

### ovos-audio

- [#146](https://github.com/OpenVoiceOS/ovos-audio/pull/146): Add duration to
  `utterance_start` message. Adds automatic audio-duration calculation to the
  recognizer event emitted when utterance recognition begins. Degrades
  gracefully if lookup fails. Not breaking. Audience: skill authors and remote
  bus consumers listening for `utterance_start`, plus downstream analytics/
  timing tooling. Expected 2.2.0 (unreleased).
- [#179](https://github.com/OpenVoiceOS/ovos-audio/pull/179): refactor: drop
  redundant legacy dual bus subscriptions. Removes manual legacy
  `self.bus.on(...)` subscriptions for six AUDIO-1 topic pairs, relying on the
  `ovos-bus-client` namespace bridge to mirror legacy emits for local
  listeners. Not conventional-commit-marked as breaking, but carries
  breaking risk for deployments running an older `ovos-bus-client` without
  that bridge. Audience: deployers on an older bus-client, remote bus
  consumers relying on the six legacy AUDIO-1 topics. Expected 2.1.2
  (unreleased).

### ovos-bus-client

- [#222](https://github.com/OpenVoiceOS/ovos-bus-client/pull/222): fix: emit
  `mycroft.scheduler.update_event` so `update_scheduled_event` reaches the
  scheduler. `EventsAPI` was emitting a topic the scheduler never listened on
  (`schedule` vs `scheduler`), so `update_scheduled_event()` was silently a
  no-op. Not breaking, a straightforward bug fix. Audience: any code calling
  `EventsAPI.update_scheduled_event()`. Expected 2.7.3 (unreleased).
- [#200](https://github.com/OpenVoiceOS/ovos-bus-client/pull/200): feat:
  `AsyncMessageBusClient` (async/await native client). Adds an async-native
  client mirroring the sync client's API surface, installed via an optional
  `ovos-bus-client[async]` dependency group. Not breaking, no impact on
  existing sync-client users. Audience: bus-client consumers and plugin
  authors wanting native async I/O. Expected 2.8.0 (unreleased).

### ovos-config

- [#194](https://github.com/OpenVoiceOS/ovos-config/pull/194): feat:
  `assistant_config`. Adds a new `AssistantConfig` layer for runtime changes
  OVOS itself makes to config, so plugin/component writes can no longer
  corrupt or silently overwrite the user's own config file. Deprecates
  `RemoteConf` and the `backend-client`/`personal-server`-era remote config
  stack. This is **deprecation-only**: every deprecated surface
  (`RemoteConf`, `Configuration.remote`, `read_mycroft_config`, and others)
  keeps working and emits a `DeprecationWarning` naming the future major
  version it will be removed in, so nothing breaks yet. Audience: skill/
  plugin authors that write to config at runtime, deployers, downstream
  tooling reading `Configuration().remote`. Expected 2.4.0 (unreleased).
- [#282](https://github.com/OpenVoiceOS/ovos-config/pull/282): feat:
  recommends for more languages (onnx-asr STT + phoonnx TTS). Adds offline
  STT/TTS recommends for 49 new languages. No existing entries are removed.
  Not breaking, purely additive. Audience: deployers/end users running
  `autoconfigure --offline` in a new language, downstream langpack
  maintainers. Expected 2.4.0 (unreleased).
- [#274](https://github.com/OpenVoiceOS/ovos-config/pull/274): feat: GPU STT
  tier on onnx-asr (`use_cuda`) + best per-lang models. Moves the `--gpu` STT
  recommends tier onto `ovos-stt-plugin-onnx-asr` with `use_cuda`, replacing
  the previous fasterwhisper/HiTZ mix. Not breaking. Audience: deployers
  running the `--gpu` autoconfigure tier. Expected 2.4.0 (unreleased).
- [#278](https://github.com/OpenVoiceOS/ovos-config/pull/278): feat: document
  `ww_urls` and `stt_urls` open_data endpoints. Extends the `open_data` block
  in the shipped `mycroft.conf` template with keys for the opt-in wake-word/
  STT sample-upload feature. Not breaking, opt-in and not enabled by default.
  Audience: deployers who opt in to `open_data` sample collection,
  `ovos-dinkum-listener` users. Expected 2.4.0 (unreleased).
- [#267](https://github.com/OpenVoiceOS/ovos-config/pull/267): Update STT
  model to large-v3-turbo. Fixes an incorrect fasterwhisper model id in the
  GPU-tier `en-us` recommend. Not breaking. Audience: deployers using the
  GPU-tier `en-us` fasterwhisper STT recommend. Expected 2.3.7 (unreleased).
- [#82](https://github.com/OpenVoiceOS/ovos-config/pull/82): add
  `audio_service_ducking` default config. Turns on audio ducking (lowering
  background volume during TTS/system sounds) by default in the shipped
  `mycroft.conf`, matching a feature already merged into `ovos-audio`. Not
  breaking, but changes default runtime audio behavior wherever the legacy
  audio service is in use. Audience: end users/deployers of the legacy
  `ovos-audio` service. Expected 2.3.7 (unreleased).

### ovos-core

- [#832](https://github.com/OpenVoiceOS/ovos-core/pull/832): feat: blacklist
  pipeline plugins at load time and per session. Adds
  `intents.blacklisted_pipelines`, checked before a pipeline plugin is loaded
  so its module is never imported, avoiding import cost for pipelines a
  deployment never uses. Also implements per-session runtime policy
  enforcement per OVOS-PIPELINE-1 §5.2/§5.5. Not breaking. Audience:
  deployers/operators tuning boot cost and per-session policy. Expected 2.6.0
  (unreleased).
- [#689](https://github.com/OpenVoiceOS/ovos-core/pull/689): feat: send
  pipeline + core version in intent metrics. Adds pipeline id and core version
  fields to the intent-metrics payload (scope of exact field shape unclear
  from the PR body). Not breaking. Audience: consumers of the intent-metrics
  telemetry event. Expected 2.6.0 (unreleased).

### ovos-dinkum-listener

- [#243](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/243): feat: opt-in `open_data` upload of wake word and STT samples. Adds a module
  that POSTs wake-word and STT audio samples to an `ovos-opendata-server`
  instance, but only fires if `open_data.ww_urls`/`stt_urls` are explicitly
  set in config. Not breaking, off by default, errors are swallowed on a
  daemon thread. Audience: deployers who opt in to data-sharing. Expected
  0.8.3 (unreleased). Pairs with ovos-config#278 above.
- [#215](https://github.com/OpenVoiceOS/ovos-dinkum-listener/pull/215): Add
  audio duration to utterance message. Adds a `duration` field to the
  `recognizer_loop:utterance` bus message payload when computable. Not
  breaking, purely additive. Audience: skill/plugin authors consuming that
  message payload, remote bus consumers logging utterance metadata. Expected
  0.8.3 (unreleased).

### ovos-gui

- [#73](https://github.com/OpenVoiceOS/ovos-gui/pull/73): Add support for
  the PyHTMX GUI client. Adds recognition of a new "py-htmx" GUI framework
  alongside QML/React handling. Not breaking. Audience: developers of
  PyHTMX-based GUI clients. Expected 1.5.0 (unreleased). **Likely stale**:
  opened December 2024 with no activity since February 2026, predates and does
  not account for the ovos-gui#112/#117 adapter rework.
- [#26](https://github.com/OpenVoiceOS/ovos-gui/pull/26): Initial React GUI
  support. Adds file-extension mapping and bus event forwarding for an
  external React GUI client. Not breaking. Audience: developers of a
  React-based GUI client. Expected 1.5.0 (unreleased). **Likely superseded**:
  opened August 2023, no activity since April 2024, predates the OVOS-GUI-1
  adapter rework and unlikely to land in its current form.

### ovos-persona-server

- [#60](https://github.com/OpenVoiceOS/ovos-persona-server/pull/60): fix:
  loader never passes `toolbox_id`, plugins own their id. Fixes
  `_load_toolboxes()` so it never passes `toolbox_id` itself. Each `ToolBox`
  plugin must now forward it from its own constructor. Framed as a fix, but
  **breaking** for `ToolBox` plugin authors, since it changes the public
  constructor contract. Audience: OPM `ToolBox` plugin authors. Expected
  0.13.4 or 0.14.0 (unreleased) (scope unclear from PR: depends on whether the
  org treats this as patch or minor).
- [#38](https://github.com/OpenVoiceOS/ovos-persona-server/pull/38): feat:
  Docker Compose OpenAI-proxy persona config and custom-container docs. Adds a
  ready-made `docker compose up` setup for an OpenAI-compatible chat endpoint.
  Not breaking, purely additive. Audience: deployers wanting a containerized
  OpenAI-compatible endpoint. Expected 0.14.0 (unreleased).

### ovos-plugin-manager

- [#385](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/385): feat:
  add triples semantic pipeline with entity linking and reasoning support.
  Extends the existing triples-extraction pipeline into a full semantic
  pipeline with new plugin types (`ENTITY_LINKER`, `TRIPLES_STORE`,
  `TRIPLES_REASONER`) and template classes. Also fixes a real bug where
  triples-extractor plugin discovery queried the wrong plugin type. Not
  breaking. Audience: plugin authors building semantic/knowledge-graph
  plugins. Expected 2.12.0 (unreleased).
- [#295](https://github.com/OpenVoiceOS/ovos-plugin-manager/pull/295): fix:
  modernize importlib. Removes the compatibility layer for older Python
  versions' `importlib`, switching plugin discovery to `importlib.metadata`
  directly. Also deprecates `normalize_lang()` in favor of
  `standardize_lang_tag()`. Not breaking, no public symbol removed. Audience:
  plugin authors, deployers on older Python versions relying on the compat
  shim. Expected 2.11.2 (unreleased).

### ovos-workshop

- [#372](https://github.com/OpenVoiceOS/ovos-workshop/pull/372): Implement
  updated Skill API. Adds Pydantic request/return model support to the Skill
  API and standard exception handling that reports errors back to the caller.
  The PR body states it is backward compatible except that a handler
  exception now returns a structured error response instead of silence.
  Audience: skill API consumers and plugin authors calling into skill public
  APIs. Expected 9.4.0 (unreleased).

## Related pages

- [Updating from Older OVOS](updating-from-older-ovos.md)
- [Version Compatibility Guide](version-compat-guide.md)
- [Screens on OVOS Today](gui-status.md)
- [Media Service (ovos-media)](ovos-media.md)
- [Formal Specifications](architecture-specs.md)
