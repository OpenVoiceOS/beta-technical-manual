# Context

!!! abstract "In a nutshell"
    Normally each thing you say to your assistant is treated on its own, with no memory of the last sentence. Conversational context is the short-term memory that lets you ask a follow-up like "where's *he* from?" right after "how tall is John Cleese?" The assistant remembers you were talking about Cleese and fills in the blank. Skill authors mark which details to remember. That memory is kept separate for each ongoing conversation, so different people or devices don't get mixed up. See [Skill design guidelines](skill-design-guidelines.md) or the [Glossary](glossary.md).

??? info "📐 Formal specification"
    Intent context is specified by **[OVOS-CONTEXT-1 — Intent Context](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-context.md)**, the *declarative* gating primitive over **[OVOS-PIPELINE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/pipeline-1.md)** (its imperative complement is the converse plugin, **[OVOS-CONVERSE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md)**, see [Converse Pipeline](converse-pipeline.md)). See the [spec index](architecture-specs.md).

    **The spec model: a decaying per-session store that *gates* matching.** In CONTEXT-1 terms, intent context is the field **`session.intent_context`**, a flat map of **entries**, each `{value, expires_at?, turns_remaining?}`. Every entry **decays**. The orchestrator prunes dead entries before each match round and decrements `turns_remaining` after it (CONTEXT-1 §4), so a confirmation flag set with `turns_remaining: 1` lives for exactly the next utterance. An intent **gates** on context by declaring **`requires_context`** (match only while a key is live) and/or **`excludes_context`** (match only while a key is absent). These are normative across every intent engine (CONTEXT-1 §6/§6.1). Keys are **scoped by shape**: a bare key like `person` is **shared** (cross-skill), and a prefixed key `<skill_id>:flag` is **private** to that owner. Bare-string `requires_context` entries default to private scope, the safe default, so a foreign skill's shared `person` can never accidentally satisfy a private gate. You must write `{key: person, scope: shared}` to read across skills.

    **Four different things called 'context': do not conflate them.** CONTEXT-1 §1.1 is explicit that the word *context* names four unrelated things:

    | Name | What it is | JSON path |
    |---|---|---|
    | `Message.context` | the bus-envelope metadata on every Message (routing keys, the `session` carrier) | `context` |
    | `session.intent_context` | the field *inside* the session that holds context entries | `context.session.intent_context` |
    | **intent context** (the term) | the decaying key/value state itself — the entries in that field | (entries of the above) |
    | `Match.slots` | the slot map produced *at match time* for one dispatch | `data.slots` |

    This page is about the third (and the field that holds it). It is not `Message.context`, and a context entry is not a `Match.slot`. CONTEXT-1 §7's context-supplied-slot rule is the bridge: when a `requires_context` key also names a slot, its value fills that slot if the utterance did not. This is exactly the "remember which person" mechanism below.

    **A capped store.** CONTEXT-1 §2 says the orchestrator SHOULD enforce a maximum
    live-entry count per session, evicting the entry closest to natural expiry when a write
    would exceed it. `ovos-spec-tools` ships the eviction helper with
    `DEFAULT_MAX_ENTRIES = 1024`, but the shipped core does not call it yet — today the only
    bound on the store is entry expiry. Either way this is a safety bound, not a limit a
    skill author needs to plan around.

    **When context and the utterance both fill a slot, the utterance wins.** CONTEXT-1 §7 only
    fills a slot from context when the utterance itself left it empty; a value the matcher
    already extracted from what the user said is never overridden by a stored context entry.

Conversational context makes voice interactions feel more natural. The assistant keeps track of the subject you are discussing, so you do not have to repeat it.

**What works in a skill today**: the declarative `requires_context=`/`excludes_context=`
kwargs on `@intent_handler` (file-registered/Padatious intents, see below), a blocking prompt,
`ask_yesno()`/`get_response()` (see [Statements and Prompts](prompts.md)), keeping the skill in
the conversation with [`converse()`](converse.md), or the Adapt path: `self.set_context()` plus
`IntentBuilder().require()` (the [TeaSkill example](#using-context-to-enable-intents) below).

`requires_context` and `excludes_context` gate matching in both the
[Adapt](adapt-pipeline.md) and [Padatious](padatious-pipeline.md) pipelines, as CONTEXT-1 §6
requires of every intent engine. Adapt gates keyword intents. Padatious gates template intents,
carrying the two declarations on the intent registration payload and dropping any candidate
whose gate is not satisfied against `session.intent_context` at match time:

```json
{
  "skill_id": "context.skill",
  "intent_name": "guarded",
  "lang": "en-US",
  "samples": ["do the guarded thing"],
  "requires_context": ["confirming"],
  "excludes_context": ["muted"]
}
```

The private/shared scoping rules are identical on both sides: a bare key gates privately
against the registering `skill_id`, and reading a shared key needs the explicit
`{"key": "person", "scope": "shared"}` form.

Since `ovos-workshop` `9.6.0a1`, `@intent_handler` carries the declaration side too, on any
intent, adapt or file-registered:

```python
from ovos_workshop.decorators import intent_handler

@intent_handler("guarded.intent",
                 requires_context=["confirming"],
                 excludes_context=["muted"])
def handle_guarded(self, message):
    ...
```

The declaration reaches every engine, but each engine gates on it independently: the template
engines (Padatious, Padacioso, M2V) filter candidates against `session.intent_context` at match
time, and so does Adapt, whose keyword matcher stores each intent's declared
`requires_context`/`excludes_context` at registration and admits a candidate only when the gate
is satisfied (OVOS-CONTEXT-1 §6/§6.1). Adapt also keeps its own separate legacy mechanism
(`.require()` on a context keyword, the TeaSkill example below) for gating today, so a skill can
use either the declarative kwargs or `.require()`.

!!! danger "A bare-string entry silently never matches a shared entry"
    A bare string like `requires_context=["prev_dialog"]` resolves to **private** scope, keyed
    to the declaring skill (the safe default). If the context entry was stored with
    `scope: "shared"`, or by a different skill's private key, the gate never sees it. This is
    not a crash or a warning. The intent just never matches. Use the long form,
    `requires_context=[{"key": "prev_dialog", "scope": "shared"}]`, to read an entry another
    skill wrote as shared.

Context lives on the per-conversation [Session](session.md), in `Session.intent_context`. It
is **session-scoped**, not a single global store, so concurrent users and devices keep
separate context.

`Session.context` still resolves as a read/write view projected over `intent_context`, kept
for older code: reads project from the canonical map and legacy writes
(`inject_context`, `update_context`, `remove_context`, `clear_context`) fold back into it,
so old mutation calls still take effect. Touching it warns. New code writes to
`intent_context` directly.

---

## Follow-up questions

### Keyword Contexts

> How tall is John Cleese?

`"John Cleese is 196 centimeters"`

> Where's he from?

`"He's from England"`

Context is added manually by the **[Skill](skill-design-guidelines.md)** creator using either the `self.set_context()` method or the `@adds_context()` decorator.

Consider the following intent handlers:

```python
    @intent_handler(IntentBuilder().require('PythonPerson').require('Length'))
    def handle_length(self, message):
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is {length_dict[python]} cm tall')

    @intent_handler(IntentBuilder().require('PythonPerson').require('WhereFrom'))
    def handle_from(self, message):
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is from {from_dict[python]}')

```

To interact with the above handlers the user would need to say

```text
User: How tall is John Cleese?
OVOS: John Cleese is 196 centimeters
User: Where is John Cleese from?
OVOS: He's from England

```

To get a more natural response the functions can be changed to let OVOS know which `PythonPerson` we're talking about by using the `self.set_context()` method to give context:

```python
    @intent_handler(IntentBuilder().require('PythonPerson').require('Length'))
    def handle_length(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'{python} is {length_dict[python]} cm tall')
        self.set_context('PythonPerson', python)

    @intent_handler(IntentBuilder().require('PythonPerson').require('WhereFrom'))
    def handle_from(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'He is from {from_dict[python]}')
        self.set_context('PythonPerson', python)

```

When either method is called, OVOS adds the `PythonPerson` keyword to its context. If there is a match with `Length` but `PythonPerson` is missing, OVOS assumes the last mention of that keyword. The interaction can now become the one described at the top of the page.

> User: How tall is John Cleese?

OVOS detects the `Length` keyword and the `PythonPerson` keyword

> OVOS: 196 centimeters

John Cleese is added to the current context

> User: Where's he from?

OVOS detects the `WhereFrom` keyword but not any `PythonPerson` keyword. The Context Manager activates and returns the latest entry of `PythonPerson`, which is _John Cleese_

> OVOS: He's from England


## Cross Skill Context

The context is limited by the keywords provided by the **current** Skill. 

There is also `self.set_cross_skill_context` / `self.remove_cross_skill_context`, intended
to share a keyword with **other** Skills as well.

`set_cross_skill_context` emits the `mycroft.skill.set_cross_context` bus
message. Every loaded `OVOSSkill` subscribes to it (and to the matching
`mycroft.skill.remove_cross_context`) and re-applies the keyword under its
own namespace. This is how it becomes visible to other skills' context
gates.

```python
    @intent_handler(IntentBuilder().require('PythonPerson').require('WhereFrom'))
    def handle_from(self, message):
        # PythonPerson can be any of the Monty Python members
        python = message.data.get('PythonPerson')
        self.speak(f'He is from {from_dict[python]}')
        self.set_context('PythonPerson', python) # context for this skill only
        
        self.set_cross_skill_context('Location', from_dict[python])  # context for ALL skills

```


!!! warning "Generic shared names are effectively global"
    A shared-scope context entry is stored under its bare, un-namespaced key. A plain,
    generic name (`prev_dialog`, `date`, `person`, `sleeping_state`) can satisfy any
    other legacy skill's `require()`/`requires_context` gate of that same name, because
    the legacy (pre-CONTEXT-1) Adapt lookup also probes the plain, un-munged keyword
    alongside its own skill-munged one. Nothing stops a different skill from writing the
    same generic name for an unrelated purpose. Prefer a distinctive, skill-specific
    keyword (`WhereFromLocation` rather than `Location`) for anything you don't
    deliberately intend to share, or use the declarative `{"key": ..., "scope": "shared"}`
    form only when cross-skill visibility is exactly what you want.

In this example `Location` keyword is shared with the WeatherSkill

```text
User: Where is John Cleese from?
OVOS: He's from England
User: What's the weather like over there?
OVOS: Raining and 14 degrees...

```

## Hint Keyword contexts

Context does not need a value. Its presence alone can indicate a previous interaction happened.

In this case, context can also be implemented with decorators instead of calling `self.set_context`.

`.require('MilkContext')` below needs no matching `MilkContext.voc` file. A `require()`
keyword with no backing vocabulary is not matched against the utterance at all. It can
only ever be satisfied by a context entry of the same name, so it behaves as a pure
context gate: present in the current context, or the intent does not match.

```python
from ovos_workshop.decorators import adds_context, removes_context


class TeaSkill(OVOSSkill):
    @intent_handler(IntentBuilder('TeaIntent').require("TeaKeyword"))
    @adds_context('MilkContext')
    def handle_tea_intent(self, message):
        self.milk = False
        self.speak('Of course, would you like Milk with that?',
                   expect_response=True)

```

The full, worked-through version of this `TeaSkill`, with every handler, is in
[Using context to enable Intents](#using-context-to-enable-intents) below.

> **NOTE**: cross skill context is not yet exposed via decorators


## Using context to enable **Intents**

Context can create "bubbles" of available intent handlers, so certain **intents** can't trigger unless some previous stage in a conversation has occurred.

> This is the *idea* behind the **`requires_context`** gate of CONTEXT-1 §6, expressed through the legacy mechanism that works today: `MilkContext` is a private flag (the `@adds_context` decorator stores it under the skill's own prefix), and an intent that `.require('MilkContext')` declares it as an Adapt keyword precondition, so the `yes`/`no` intents are invisible except in the narrow window between the question and the reply, with no skill-side state machine. Note that `.require()` keyword matching and the declarative `requires_context=` / `excludes_context=` intent kwargs are **different code paths**: the declarative gate looks entries up under the resolved `<skill_id>:<key>` shape, which `set_context` / `@adds_context` also write (see "Both spellings are written, with one decay policy" below). The complementary `excludes_context` gate (CONTEXT-1 §6.1) handles fire-once intents (for example, "greet only once per session").

```text
User: Hey Mycroft, bring me some Tea
OVOS: Of course, would you like Milk with that?
User: No
OVOS: How about some Honey?
User: All right then
OVOS: Here you go, here's your Tea with Honey

```

```python
from ovos_workshop.decorators import adds_context, removes_context

class TeaSkill(OVOSSkill):
    @intent_handler(IntentBuilder('TeaIntent').require("TeaKeyword"))
    @adds_context('MilkContext')
    def handle_tea_intent(self, message):
        self.milk = False
        self.speak('Of course, would you like Milk with that?',
                   expect_response=True)

    @intent_handler(IntentBuilder('NoMilkIntent').require("NoKeyword").
                                  require('MilkContext').build())
    @removes_context('MilkContext')
    @adds_context('HoneyContext')
    def handle_no_milk_intent(self, message):
        self.speak('all right, any Honey?', expect_response=True)

    @intent_handler(IntentBuilder('YesMilkIntent').require("YesKeyword").
                                  require('MilkContext').build())
    @removes_context('MilkContext')
    @adds_context('HoneyContext')
    def handle_yes_milk_intent(self, message):
        self.milk = True
        self.speak('What about Honey?', expect_response=True)

    @intent_handler(IntentBuilder('NoHoneyIntent').require("NoKeyword").
                                  require('HoneyContext').build())
    @removes_context('HoneyContext')
    def handle_no_honey_intent(self, message):
        if self.milk:
            self.speak('Heres your Tea with a dash of Milk')
        else:
            self.speak('Heres your Tea, straight up')

    @intent_handler(IntentBuilder('YesHoneyIntent').require("YesKeyword").
                                require('HoneyContext').build())
    @removes_context('HoneyContext')
    def handle_yes_honey_intent(self, message):
        if self.milk:
            self.speak('Heres your Tea with Milk and Honey')
        else:
            self.speak('Heres your Tea with Honey')

```

At startup, only the `TeaIntent` is available. Once it triggers and adds _MilkContext_, the `MilkYesIntent` and `MilkNoIntent` become available, since _MilkContext_ is set. When a _yes_ or _no_ is received, _MilkContext_ is removed and can't be accessed. In its place, _HoneyContext_ is added, making the `YesHoneyIntent` and `NoHoneyIntent` available.

You can find an example [Tea Skill using conversational context on Github](https://github.com/krisgesling/tea-skill).

As you can see, Conversational Context lends itself well to implementing a [dialog tree or conversation tree](https://en.wikipedia.org/wiki/Dialog_tree).

## Under the hood

`set_context` / `remove_context` are thin wrappers. They prefix the keyword with the
skill id (the legacy Adapt dialect: `alphanumeric_skill_id + context`, no separator)
and emit bus messages that `ovos-core` handles on the active Session:

| Message | Effect |
|---|---|
| `add_context` | inject a keyword (and optional value) into `Session.context` |
| `remove_context` | drop a single keyword |
| `clear_context` | wipe all context for the session |

Alongside the legacy munged `context` field, `add_context` / `remove_context` also
carry the original, unmunged keyword as an additive `key` field on the message data.
This lets a consumer resolve the same call under either spelling: the legacy
Adapt dialect (`context`) or the colon-separated `<skill_id>:<key>` shape that
CONTEXT-1's declarative `requires_context` / `excludes_context` gate (above) expects.
`set_cross_skill_context` and the deprecated `set_adapt_context` /
`remove_adapt_context` shortcuts carry the same additive `key`.

!!! note "Both spellings are written, with one decay policy"
    `set_context` writes into the session per CONTEXT-1 §5.0: the mutation lands on the
    current handler's session directly, and the legacy `add_context` bus message is also
    emitted as a compat dual-write for pre-§5.0 cores. Because that write lands on the live
    session first, context set inside a handler is visible to the dispatch that immediately
    follows it, in the same handler invocation, with no race. The core writes **two** entries:
    the legacy munged `skillidkey` spelling and the resolved `<skill_id>:<key>` spelling
    the declarative gate looks up. One computed `expires_at` applies to both, so
    `set_context` entries decay normally (`context.timeout`, minutes, default `2`) and a
    re-set refreshes the expiry of both keys. The remaining gap is declaration-side only
    (see the warning near the top of this page).

!!! note "Writing a key replaces it wholesale; there is no read-back"
    Writing an entry under a key that already exists **replaces the whole entry**, value and
    decay timer both. It does not merge onto the old one. A re-set refreshes the decay
    window, which is what naptime-style "keep this alive while we talk" flows rely on.
    (Entries carry an explicit `expires_at` computed from the `context.timeout` config value
    in minutes, default `2`, which is where [Session](session.md)'s "~2 minutes" figure
    comes from; spec-shaped writes may instead carry `turns_remaining`.) There is no API
    to read a
    context entry's current value or remaining decay back out. A skill that wants to know
    "what did I set this to, and how long ago" must keep that in its own state, not rely on
    reading it back from context. A flag-style call with no explicit value,
    `self.set_context('MilkContext')`, still needs something to store: the underlying wire
    message stores the keyword name itself as the value (`{"value": word or context}`), not
    an empty or null value.

!!! note "Set context before speaking, not after"
    A context write only reaches anyone else once the handler emits a Message derived
    from the mutated session, `self.speak()`, `self.speak_dialog()`, or any other emit.
    Write the context first, then speak. A handler that speaks and only afterward writes
    context has nothing left to carry that write: on a named (remote) session, where the
    orchestrator holds no state between utterances, a write with no following emit is
    invisible to the next turn.

The decorators are equivalent to calling these methods:

- `@adds_context('MilkContext')` calls `set_context('MilkContext')` after the handler runs.
- `@removes_context('MilkContext')` calls `remove_context('MilkContext')`.

Because context is attached to the Session, each handler receives the message that triggered it.
The Adapt pipeline reads `Session.context` when scoring intents. This is why missing keywords
fall back to the most recent matching context entry.

---
**Read next:** [Intent Layers](layers.md)
**Related:** [Asking the User for Responses in OVOS Skills](prompts.md) · [Session Aware Skills](session.md) · [Intent Design](intents.md) · [Converse](converse.md)

