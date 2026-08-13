# A voice game: converse-driven game loop

!!! abstract "In a nutshell"
    You build a `ConversationalGameSkill` that runs a full voice game on top of OCP, using `on_play_game`/`on_game_command` so free-form input reaches game logic instead of the intent parser.

**When you'd want this:** the skill runs a game entirely by voice, such as a number-guessing game or a text adventure. While the game is playing, almost anything the user says is game input, not a new command, and the skill must still respond correctly to "stop" or "pause".

`ConversationalGameSkill` (from `ovos_workshop.skills.game_skill`) is a small set of `on_*` hooks over `OVOSCommonPlaybackSkill`. The OCP media pipeline treats a game as `MediaType.GAME`: saying "play guess the number" reaches the skill through the same "play X" matching as music or a podcast, and OCP's play/pause/resume/stop transport controls double as the game's transport.

```python
import random

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills.game_skill import ConversationalGameSkill


class GuessNumberGameSkill(ConversationalGameSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(skill_voc_filename="GuessNumberGameKeyword",
                         *args, **kwargs)
        self.secret = None
        self.guesses_left = 0

    def on_play_game(self):
        # the framework already set self.is_playing True before this runs
        self.secret = random.randint(1, 100)
        self.guesses_left = 7
        self.speak_dialog("game_start", {"tries": self.guesses_left})

    def on_stop_game(self):
        self.speak_dialog("game_stop")

    def on_abandon_game(self):
        # called before on_stop_game if the user goes quiet mid-game
        self.speak_dialog("game_abandoned")

    def on_game_command(self, utterance: str, lang: str):
        # every utterance that isn't claimed by an intent below lands here
        try:
            guess = int(utterance)
        except ValueError:
            self.speak_dialog("not_a_number", expect_response=True)
            return

        self.guesses_left -= 1
        if guess == self.secret:
            self.speak_dialog("guess_correct")
            self.stop_game()
        elif self.guesses_left <= 0:
            self.speak_dialog("guess_out_of_tries", {"answer": self.secret})
            self.stop_game()
        elif guess < self.secret:
            self.speak_dialog("guess_higher", {"tries": self.guesses_left},
                             expect_response=True)
        else:
            self.speak_dialog("guess_lower", {"tries": self.guesses_left},
                             expect_response=True)

    @intent_handler("cheat_hint.intent")
    def handle_cheat_hint(self, message):
        # this is the ONLY declared intent in the whole skill; every other
        # utterance while playing falls through to on_game_command above,
        # keeping the game's own vocabulary out of the intent parser entirely
        if self.is_playing:
            self.speak_dialog("hint_refused")
```

### Moving parts

- `ConversationalGameSkill` subclasses `OVOSGameSkill`, which subclasses `OVOSCommonPlaybackSkill`. The constructor requires `skill_voc_filename`, a `.voc` file (`locale/en-us/vocab/GuessNumberGameKeyword.voc`) listing the game's name, so OCP's search step recognizes "play guess the number" as this skill and not a music query.
- `on_play_game()`, `on_stop_game()`, `on_save_game()`, `on_load_game()` are the abstract hooks every game must implement. The last two default to speaking a "can't save" dialog if left alone. OCP calls `on_play_game()` after already marking the skill as playing, so `self.is_playing` is `True` inside it.
- `on_pause_game()` and `on_resume_game()` also come from the base class with a working default: an acknowledgement sound, plus an optional dialog gated by the `pause_dialog` setting. Override them only if pausing needs game-specific behavior.
- `on_game_command(utterance, lang)` is where free-form game input arrives. The base class's `converse()` calls it whenever the skill is playing and not paused, and the utterance would not otherwise trigger one of this skill's own `@intent_handler`s (checked via `skill_will_trigger`). That is what "keeping intents inert during play" means in practice. Declare as few `@intent_handler`s as the game truly needs, such as `cheat_hint.intent` above. Everything else reaches `on_game_command`: digits, "up", "north", whatever the game vocabulary is. Without this, those utterances would miss every intent and fall through to a fallback skill.
- `self.stop_game()` is the base class helper a skill calls to end the game itself, after a correct guess or running out of tries. It clears playback state and then calls `on_stop_game()` for you. Do not call `on_stop_game()` directly.
- Abort/inactivity is handled above the skill entirely: if the user goes quiet for a while, the intent service deactivates the skill, which calls `on_abandon_game()` and then `stop_game()` (which in turn calls `on_stop_game()`). Explicit "stop" while playing goes through the normal OCP stop transport, which calls `stop_game()` the same way.
- Set `self.settings["auto_save"] = True` and implement `on_save_game()` for autosave-before-stop behavior. `ConversationalGameSkill` then calls it for you on every `converse()` turn and on `stop()`, when both the setting and the override are present (checked via `save_is_implemented`).

!!! tip "Full production example"
    `skill-moon-game` (a VoiceGamez title, not currently public) is a full `ConversationalGameSkill`: a branching narrative driven entirely through `on_game_command`, with `IntentLayers` gating which branch-specific phrases are even considered at each story beat. `FrotzSkill` (from the [`pyfrotz`](https://github.com/JarbasAl/pyfrotz) package) shows the same hooks wrapping something entirely different: every utterance in `on_game_command` is piped as a raw command to an external Z-machine interpreter process, and its text output is what gets spoken.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [A small local media playlist](recipe-local-media-playlist.md) · [OCP Skills](ocp-skills.md) · [Continuous conversation](recipe-multi-turn-conversation.md)
