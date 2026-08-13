# Session Aware Skills

!!! success "Maturity — Mature ⬤⬤⬤⬤⬤"
    Long-lived and actively maintained. Depend on it freely. Rated by [repository health](maturity.md), not version.

!!! abstract "In a nutshell"
    One OVOS device can talk to several people at once: your phone, a kitchen speaker, and other connected devices may all be asking it things at the same time. A *session* is simply the information that says who is asking and in what language. If your skill remembers anything between requests, like a running game or a chat history, it needs to keep each person's information separate so two users don't get each other's answers, much like separate tables at a restaurant — key that state by `session_id` instead of stashing it in a single instance variable. This page shows how to make a skill session aware. New terms are explained in the [Glossary](glossary.md).

??? info "Formal specification"
    **SESSION-1 is the field registry.** Other specs *claim* fields into it (e.g. `intent_context` → CONTEXT-1, the transformer-chain lists → OVOS-TRANSFORM-1). See also the [spec index](architecture-specs.md).

    - **[OVOS-SESSION-1 — Session Carrier](https://github.com/OpenVoiceOS/architecture/blob/dev/session-1.md)**: the session's wire shape and field registry.
    - **[OVOS-SESSION-2 — Session Lifecycle & State Ownership](https://github.com/OpenVoiceOS/architecture/blob/dev/session-2.md)**: who owns and may mutate session state, and the reserved `"default"` device-local session.
    - **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)**: the decaying per-session `intent_context` that gates which intents may match across turns.

    ```mermaid
    flowchart LR
        Sat["Voice satellite / HiveMind node"] -->|Message + Session| Bus["Messagebus"]
        Bus --> SM["SessionManager"]
        SM -->|"default" session, device-local| Core["ovos-core orchestrator"]
        SM -->|unique session_id, external client| Core
        Core -->|SessionManager.get message| Skill["Skill"]
    ```

    *Diagram:* The flow starts at the voice satellite or HiveMind node, passes through the messagebus and SessionManager, and ends at the skill, branching on whether the session is the device-local "default" session or a unique external session_id.

If you want your skills to handle simultaneous users, make them **Session** aware.

Each remote client, usually a [voice satellite](https://jarbashivemind.github.io/HiveMind-community-docs/satellites/), sends a `Session` with the `Message`.

Your skill should keep track of any session-specific state separately, for example a chat history.

> **WARNING**: Stateful Skills need to be Session Aware to play well with [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/)

## SessionManager

You can access the `Session` in a `Message` object via the `SessionManager` class

```python
from ovos_bus_client.session import SessionManager, Session

class MySkill(OVOSSkill):

    def on_something(self, message):
        sess = SessionManager.get(message)
        print(sess.session_id)

```

If the message originated in the device itself, the `session_id` is always equal to the reserved value `"default"`. If it comes from an external client, it will be a unique uuid. The `"default"` session is special: it is the device-local session whose state the orchestrator holds and persists in-process, rather than receiving it from a client on every message (OVOS-SESSION-2 §5).

!!! warning "A bare `session_id` does not carry state — replay the whole session"
    An external client (a HiveMind satellite, any non-`"default"` session) is not tracked
    in-process the way the device-local session is. `ovos-core` only refreshes what it
    already holds for a given `session_id`; a `session_id` this process never folded a full
    session for is carried through untouched, with none of the previous turn's state. To keep
    multi-turn continuity — `intent_context`, `lang`, presentation preferences, and the rest —
    a client must send the **complete serialized session** (`Session.serialize()`) back on
    each message, not just the bare `session_id` string. Losing that round trip is
    indistinguishable from starting a brand new session every turn — a `session_id` this
    process has never folded a full session for gets a **fresh** session by design, not an
    error and not a reconstruction from history.

    There is no topic that *pushes* an updated session from the orchestrator down to a
    client to keep it current. `ovos.session.sync` is the closest thing, and it runs the
    other way: a client emits it carrying its *own* snapshot, and the receiver merges that
    snapshot's `intent_context` onto whatever it already holds for that `session_id`
    (OVOS-CONTEXT-1 §5.3) — a pull-shaped merge triggered by the sender, not a broadcast.
    A bare `ovos.session.sync` with no session carrier is handled differently again: it is
    read as a legacy request for the current **default** session and answered with a
    `ovos.session.update_default` echo, which only ever concerns the device-local
    `"default"` session, never an external client's. Multiple clients each carrying their
    own full session converge on consistent state by every one of them adopting this
    same discipline, not by any message that reconciles them from the server side.

!!! note "A present-but-malformed session never crashes the bus client"
    `Session.from_message` treats an *absent* `session` key (or an explicit
    `null`) as "use the default session," which is completely normal. A `session`
    key that *is* present but is not a JSON object (a bare string, a number)
    is a different case: a producer bug. Rather than raising and tearing
    down the whole bus connection, the client discards just that one
    malformed message and logs a warning, so one badly-behaved emitter can't
    force every other client into a reconnect loop.

## Language signals

`lang` is one of **six** BCP-47 language fields a session may carry (SESSION-1 §3.2). Each
names a different *kind* of signal. Each is optional and written independently, by
different components or different stages of the pipeline. Their meanings are fixed. How a
consumer folds them into one language for a given operation is not fixed, and is left to the stage
doing the work.

| Field | Meaning | Typically written by |
|---|---|---|
| `lang` | The participant's **preferred language**: the stable base signal for the session, and the fallback when nothing per-utterance is available | The client or bridge that opened the session, or the deployment default otherwise |
| `secondary_langs` | Additional languages the participant also speaks, most-preferred first. Never contains `lang` itself | The client or bridge that opened the session |
| `output_lang` | The language the participant wants **replies rendered in**, independently of what they speak | The client, or a user preference. Consumed by dialog/prompt rendering |
| `stt_lang` | The language the **speech-to-text stage was configured to assume** for the audio. Diverges from the transcript's language when a speech-translation model is used | The audio input service, before or at STT invocation |
| `request_lang` | The language the **emitter reported** for this utterance: a hint, never authoritative (e.g. the language bound to the wake word that fired) | The emitter: listener, UI selector, or a routing layer |
| `detected_lang` | The language a **detection component** classified the utterance as. May disagree with both `stt_lang` and `lang`. Disagreement is normal | A language-detection plugin or transformer |

Rough guidance on which to read: render responses in `output_lang` when it is set. Constrain a
detector's candidate set with `lang` plus `secondary_langs`. For intent matching, `ovos-core`
does not read a single field in isolation. See [Language Selection](lang-selection.md) for the
authoritative resolution order (`stt_lang` → `request_lang` → `detected_lang` → configured
default). Never assume a field is present, and never assume one equals another.

!!! warning "`data.lang` is per-payload, not session state"
    Many bus topics carry a `data.lang` describing the language of the content *in that
    message*, the utterance just transcribed, the dialog just rendered. It is owned by the
    spec defining the topic, is not a session field, and is not propagated with the session
    (SESSION-1 §3.2.8). A consumer that needs a payload's content language reads `data.lang`
    directly and **must not** assume it equals `session.lang` or any other session signal.
    TTS voice selection keys on `data.lang` for exactly this reason.

See [Language Selection and Disambiguation](lang-selection.md) for how `ovos-core` resolves
these signals into the language it matches an utterance in.

## Intent context

A session also carries `intent_context`: a per-key decaying context store that gates which
intents may match across turns (e.g. "book a flight" setting context so a follow-up "to
Paris" is understood without repeating "flight"). It is a session field claimed into the
SESSION-1 registry by **OVOS-CONTEXT-1**, holding `{value, expires_at}` per key. In the spec
model each entry decays via its `expires_at` / `turns_remaining`; the legacy keyword-context
manager ages whole frames out after the `context.timeout` config value (minutes, default `2`).
Note that entries written through `set_context` currently never decay at all — the core write
path drops the expiry stamp (see the caveats on [Conversational Context](context.md)). See
[Intent Service](intent-service.md) for how context is set, read, and consumed during
pipeline matching.

## Presentation preferences

Beyond `session_id` and the language signals, a session carries **presentation
preferences** that follow the session's originator rather than the device.
This is useful when a remote participant (a HiveMind satellite, a different-locale
caller) wants times, dates, units, and place-relative answers rendered for
*their* locale: `location` (an object holding city/coordinate/timezone),
`system_unit` (`"metric"` / `"imperial"`), `time_format` (`"full"` for
24-hour, `"half"` for 12-hour), and `date_format` (e.g. `"DMY"` / `"MDY"`).
All four are optional. An absence falls back to the deployment default,
and `location` is what backs the `location` / `location_pretty` /
`location_timezone` magic properties below.

## Magic Properties

Skills have some "magic properties." These reflect the current `Session`'s value when it has
one, falling back to Configuration otherwise.

```python
    # magic properties -> depend on message.context / Session
    @property
    def lang(self) -> str:
        """
        Get the current language as a BCP-47 language code. This will consider
        current session data if available, else Configuration.
        """
        
    @property
    def location(self) -> dict:
        """
        Get the JSON data struction holding location information.
        This info can come from Session
        """

    @property
    def location_pretty(self) -> Optional[str]:
        """
        Get a speakable city from the location config if available
        This info can come from Session
        """

    @property
    def location_timezone(self) -> Optional[str]:
        """
        Get the timezone code, such as 'America/Los_Angeles'
        This info can come from Session
        """
        
    @property
    def dialog_renderer(self) -> Optional[MustacheDialogRenderer]:
        """
        Get a dialog renderer for this skill. Language will be determined by
        message context to match the language associated with the current
        session or else from Configuration.
        """

    @property
    def resources(self) -> SkillResources:
        """
        Get a SkillResources object for the current language. Objects are
        initialized for the current Session language as needed.
        """

```

!!! note "Two different ways a session gets updated"
    An inbound client message **merges** field-by-field onto the stored
    `"default"` session. A field the client omits is left alone, so a
    client can never delete a stored field just by not sending it. A
    pipeline plugin's `Match.updated_session`, by contrast, is a **complete
    snapshot**: whatever it doesn't include is treated as deleted. Deletion
    by omission exists on that one pathway only.

## Per User Interactions

Let's consider a skill that keeps track of a chat history, how would such a skill keep track of `Sessions`?

```python
from ovos_bus_client.session import SessionManager, Session
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class UtteranceRepeaterSkill(OVOSSkill):

    def initialize(self):
        self.chat_sessions = {}
        self.add_event('recognizer_loop:utterance', self.on_utterance)

    # keep chat history per session
    def on_utterance(self, message):
        utt = message.data['utterances'][0]
        sess = SessionManager.get(message)
        if sess.session_id not in self.chat_sessions:
            self.chat_sessions[sess.session_id] = {"current_stt": ""}
        self.chat_sessions[sess.session_id]["prev_stt"] = self.chat_sessions[sess.session_id]["current_stt"]
        self.chat_sessions[sess.session_id]["current_stt"] = utt

    # retrieve previous STT per session
    @intent_handler('repeat.stt.intent')
    def handle_repeat_stt(self, message):
        sess = SessionManager.get(message)
        if sess.session_id not in self.chat_sessions:
            utt = self.resources.render_dialog('nothing')
        else:
            utt = self.chat_sessions[sess.session_id]["prev_stt"]
        self.speak_dialog('repeat.stt', {"stt": utt})
            
    # session specific stop event 
    # if this method returns True then self.stop will NOT be called
    def stop_session(self, session: Session):
        if session.session_id in self.chat_sessions:
            self.chat_sessions.pop(session.session_id)
            return True
        return False

```

A full example can be found in the [parrot skill](https://github.com/OpenVoiceOS/ovos-skill-parrot)

---
**Read next:** [Statements](statements.md)
**Related:** [Converse](converse.md) · [Context](context.md) · [Configuration Management](config.md) · [Skill Settings](skill-settings.md)
