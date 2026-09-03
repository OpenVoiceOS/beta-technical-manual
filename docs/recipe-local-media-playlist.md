# A small local media playlist: an OCP skill

!!! abstract "In a nutshell"
    You build an `OVOSCommonPlaybackSkill` that serves a short, fixed local playlist through OCP's `@ocp_search` provider mechanism.

**When you'd want this:** "play the office playlist" should hand back a short, fixed list of
local audio files. It should need no external search or streaming service.

**Prerequisite:** the base class and decorator ship with `ovos-workshop`. Matching "play …"
requests requires the OCP pipeline stage. Check it is installed (`pip show
ovos-ocp-pipeline-plugin`) and in your `intents.pipeline`, the same way
[Your First Skill](first-skill.md) checks for Padatious. See [OCP Pipeline](ocp-pipeline.md).

```python
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill

PLAYLIST = [
    {
        "title": "Morning Briefing",
        "uri": "file:///opt/office-media/morning-briefing.mp3",
        "length": 180,
    },
    {
        "title": "Lobby Loop",
        "uri": "file:///opt/office-media/lobby-loop.mp3",
        "length": 600,
    },
]


class OfficePlaylistSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, supported_media=[MediaType.MUSIC], **kwargs)
        self.skill_icon = ""  # optional path/URI to an icon shown in OCP's UI

    @ocp_search()
    def search_office_playlist(self, phrase, media_type=MediaType.GENERIC):
        # self.voc_match() lets a skill claim narrow phrases confidently;
        # everything else gets a low, generic confidence
        confident = self.voc_match(phrase, "office_playlist")
        for track in PLAYLIST:
            if confident or track["title"].lower() in phrase.lower():
                yield {
                    "title": track["title"],
                    "uri": track["uri"],
                    "media_type": MediaType.MUSIC,
                    "playback": PlaybackType.AUDIO,
                    "match_confidence": 90 if confident else 40,
                    "length": track["length"],
                }
```

`locale/en-us/vocab/office_playlist.voc`:

```text
office playlist
lobby music
```

### Moving parts

- `MediaType` and `PlaybackType` are enums imported from `ovos_utils.ocp`. Results are plain dicts, not a dedicated result class. Mandatory keys are `uri`, `title`, `media_type`, `playback`, `match_confidence` (0-100), with `artist`, `album`, `image`, `length` (seconds) optional. Full field table: [OCP Skills](ocp-skills.md).
- `@ocp_search()` (imported from `ovos_workshop.decorators.ocp`) marks a method as a search provider. OCP queries every OCP skill in parallel across the bus (a single skill's own `@ocp_search` methods run sequentially) and keeps the best-confidence result across all installed OCP skills. A search method may `return` a list or `yield` results incrementally.
- `supported_media` (passed to `super().__init__()`) tells OCP which `MediaType`s this skill should even be asked about.
- `self.voc_match(phrase, "office_playlist")` reuses the same vocabulary mechanism as intents to give a confident match a high score, while still falling back to a loose substring check.
- [OCP Skills](ocp-skills.md) also documents `self.extend_timeout()` (ask OCP to wait longer for a slow search). It notes that new integrations not needing the full skill lifecycle may prefer a `MediaProvider` plugin instead. See that page's opening warning.

!!! tip "Full production example (archived, source only)"
    [`ovos-skill-somafm`](https://github.com/OpenVoiceOS/ovos-skill-somafm) is a full modern OCP skill: `@ocp_search`, `@ocp_featured_media`, `register_ocp_keyword`, and results built as `Playlist`/`MediaEntry` objects instead of plain dicts. [`ovos-skill-news`](https://github.com/OpenVoiceOS/ovos-skill-news) applies the same pattern for `MediaType.NEWS`. Both repos are archived. Their MediaProvider plugin replacements are what a new deployment should install; see [Music & Radio](skill-examples-media.md).

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [OCP Skills](ocp-skills.md) · [Converse-driven game loop](recipe-conversational-game.md) · [Common Query Framework](common-query.md)
