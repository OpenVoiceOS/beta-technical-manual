# Skill Cookbook

!!! abstract "In a nutshell"
    The rest of this manual documents individual building blocks (settings, scheduling, playback, a GUI) one at a time. This page instead shows them **combined**, the way a real skill uses them: a complete, working file for each common job a skill needs to do. If you already know what `schedule_event` or `@ocp_search` does and just want to see it used correctly next to everything else it needs, start here. Newer skill authors are welcome too: the table below roughly progresses from simpler to more involved — the plain `OVOSSkill` recipes are approachable straight after [Your First Skill](first-skill.md), while the conversational-game, OCP, and MQTT recipes assume more (check the base-class column rather than relying strictly on row order).

Each recipe is a **complete skill module** (or a clearly-marked excerpt of one), with notes on the moving parts and links to the reference page that documents each API in full. None of these recipes invent new methods: every class, method signature, and bus event name was checked against the installed `ovos-workshop`, `ovos-bus-client`, and `ovos-utils` packages.

!!! note "Scaffolding not shown"
    To keep each recipe focused, `requirements.txt`, `manifest.yml`, `setup.py`/`pyproject.toml`, and the `__init__.py` boilerplate needed to actually publish a skill are omitted here. See [Anatomy of a Skill](skill-structure.md) for those. Intent files (`.intent`, `.voc`) referenced below live under `locale/<lang>/`.

## Recipe index

| # | Recipe | Base class | Teaches |
|---|--------|-----------|---------|
| 1 | [Reminder with restart persistence](recipe-reminder-persistence.md) | `OVOSSkill` | `schedule_event`, `settings` restart survival |
| 2 | [Configurable + reactive settings](recipe-reactive-settings.md) | `OVOSSkill` | `settings_change_callback`, `settingsmeta.yaml` |
| 3 | [Safe external API call](recipe-safe-api-call.md) | `OVOSSkill` | `runtime_requirements`, `file_system` cache |
| 4 | [Multi-turn conversation](recipe-multi-turn-conversation.md) | `ConversationalSkill` | `get_response`, `converse`, `activate` |
| 5 | [Local media playlist](recipe-local-media-playlist.md) | `OVOSCommonPlaybackSkill` | `@ocp_search`, `MediaType`/`PlaybackType` |
| 6 | [GUI + voice together](recipe-gui-plus-voice.md) | `OVOSSkill` | `self.gui`, `show_page` |
| 7 | [Fallback to an LLM solver](recipe-llm-fallback.md) | `FallbackSkill` | `register_fallback`, `QuestionSolver` |
| 8 | [Ambient bus-event behavior](recipe-ambient-bus-events.md) | `OVOSSkill` | `add_event`, `recognizer_loop:*` |
| 9 | [Converse-driven game loop](recipe-conversational-game.md) | `ConversationalGameSkill` | `on_play_game`, `on_game_command`, `converse` |
| 10 | [Validated slot collection](recipe-validated-get-response.md) | `OVOSSkill` | `get_response(validator=..., on_fail=..., num_retries=...)` |
| 11 | [Control an external device (MQTT)](recipe-mqtt-device-control.md) | `OVOSSkill` | `paho.mqtt.client.Client`, `connect`, `publish`, `disconnect` |
| 12 | [A skill with a settings UI](recipe-settings-ui.md) | `OVOSSkill` | `settingsmeta.yaml`, `ovos-skill-config-tool`, `settings_change_callback` |

## Learn from the official skills

Every pattern in this cookbook also runs in a real, installable skill. Read the source when you need to see a full manifest, locale files, and edge cases this cookbook leaves out.

| Pattern | Official skill |
|---|---|
| `ConversationalSkill` + scheduling + settings persistence | [`ovos-skill-alerts`](https://github.com/OpenVoiceOS/ovos-skill-alerts) |
| Full OCP (`@ocp_search`, `@ocp_featured_media`, `Playlist`/`MediaEntry`) | [`ovos-skill-somafm`](https://github.com/OpenVoiceOS/ovos-skill-somafm) |
| `FallbackSkill` + `@common_query` | [`ovos-skill-wolfie`](https://github.com/OpenVoiceOS/ovos-skill-wolfie), [`ovos-skill-ddg`](https://github.com/OpenVoiceOS/ovos-skill-ddg), [`ovos-skill-wordnet`](https://github.com/OpenVoiceOS/ovos-skill-wordnet) |
| `@common_query` on a plain `OVOSSkill` | [`ovos-skill-wikipedia`](https://github.com/OpenVoiceOS/ovos-skill-wikipedia) |
| Minimal `converse` | [`ovos-skill-parrot`](https://github.com/OpenVoiceOS/ovos-skill-parrot) |
| Converse-driven game (`ConversationalGameSkill`) | `skill-moon-game` (a VoiceGamez title, not currently public) |
| GUI sequencing (`show_text` then `show_image`) | [`ovos-skill-camera`](https://github.com/OpenVoiceOS/ovos-skill-camera) |
| GUI ownership handoff (`gui.release()`) | [`ovos-skill-wallpapers`](https://github.com/OpenVoiceOS/ovos-skill-wallpapers) |
| Validated `get_response` slot collection | [`ovos-skill-mark1-ctrl`](https://github.com/OpenVoiceOS/ovos-skill-mark1-ctrl) |
| Terminal fallback (priority 100) | [`ovos-skill-fallback-unknown`](https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown) |
| Locale-correct number/date speech | [`ovos-skill-count`](https://github.com/OpenVoiceOS/ovos-skill-count), [`ovos-skill-date-time`](https://github.com/OpenVoiceOS/ovos-skill-date-time) |
| Simplest complete skill | [`ovos-skill-hello-world`](https://github.com/OpenVoiceOS/ovos-skill-hello-world) |

---
**Read next:** [Skill Structure](skill-structure.md) · [Intent Design](intents.md)
**Related:** [Your First Skill](first-skill.md) · [Skill Design Best Practices](skill-best-practices.md) · [OCP Skills](ocp-skills.md) · [Common Query Framework](common-query.md)
