# Converse

!!! info "Which page do you want?"
    This page covers the skill-side `converse()` API. [Converse Pipeline](converse-pipeline.md)
    covers the pipeline stage that dispatches to it. [Session](session.md) covers session
    state. [Layers](layers.md) covers intent layers. [Permissions](permissions.md) covers
    activation control. Just want to ask one blocking yes/no question and get the answer in
    the same handler? You don't need `converse()` at all — use `ask_yesno()` /
    `get_response()`, covered in [Statements and Prompts](prompts.md).

!!! abstract "In a nutshell"
    Normally a skill answers one request and then forgets about you. "Converse" lets a skill stay in the conversation for a little while after it has spoken, so it can catch a quick follow-up like "yes", "no", "thanks", or "the red one" that only makes sense as a reply. This is the difference between a one-off answer and a short back-and-forth chat. See [Converse Pipeline](converse-pipeline.md) for how this feature is implemented as a pipeline plugin inside `ovos-core`. New terms are explained in the [Glossary](glossary.md).

??? info "📐 Formal specification"
    Converse is specified by **[OVOS-CONVERSE-1 — Active Handlers & Interactive Response](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md)** (a formal [architecture spec](architecture-specs.md)). A skill that was recently active stays on the session's **converse-handler list** (`session.converse_handlers`, what this page calls the *Active Skills List*). The "wait for the next reply" feature (the response window) is the session field `session.response_mode`, delivered via the reserved `intent_name` **`response`**. Both `converse` and `response` are reserved names no skill may register. The list and the response window are **session-resident state** that rides every message. This is why session-aware skills behave correctly across satellites.

    ```mermaid
    sequenceDiagram
        participant U as User
        participant P as Converse pipeline plugin
        participant S as Skill (active)
        participant O as Orchestrator
        U->>P: new utterance
        P->>S: <skill_id>.converse.ping
        S-->>P: skill.converse.pong
        alt skill claims
            P->>O: Match(intent_name=converse)
            O->>S: dispatch match_type=converse:skill
        else no claim
            P->>O: fall through to intent pipeline
        end
    ```

    *Diagram:* The sequence starts with a new user utterance and ends with the orchestrator dispatching to the skill if it claims the turn, or falling through to the intent pipeline if not.

!!! note "`stop` is a reserved name too"
    `stop` is a reserved `intent_name` alongside `converse` and `response`
    ([ovos-core#778](https://github.com/OpenVoiceOS/ovos-core/pull/778), STOP-1 §4). A match
    produced by the stop pipeline plugin also suppresses the `session.active_handlers` push,
    but through a different switch: converse, fallback, and common-query suppress it because
    the orchestrator knows those pipelines produce reserved names, while a stop match carries
    `IntentHandlerMatch.suppress_activation`, which additionally skips the `{skill_id}.activate`
    emit. See [Life of an Utterance](life-of-an-utterance.md) for the two mechanisms and
    [Intent Service](intent-service.md) for the pipeline-plugin side.

**What / why (beginners):** `converse()` lets a skill keep listening after it has just spoken, without registering a new intent for every possible follow-up. Once your skill runs, it goes onto the **Active Skills List** for a few minutes. While it is there, every new utterance is offered to its `converse()` method before normal intent parsing. This is how you handle "yes / no / thanks / the red one" replies that only make sense right after your skill acted.

Each [Skill](skill-design-guidelines.md) may define a `converse()` method. This method is called any time the skill has been recently active and a new utterance is processed.

The converse method expects a single argument, a standard `Message` object, the same object an intent handler receives.

Converse methods must return a Boolean: `True` if the utterance was handled (it is consumed and intent parsing is skipped), otherwise `False`.

!!! warning "Requires `ConversationalSkill`"
    `converse()`, `activate()`, `deactivate()`, `handle_activate()`/`handle_deactivate()`, and
    `@conversational_intent` are **not** available on the plain `OVOSSkill` base class. Subclass
    `ConversationalSkill` (`from ovos_workshop.skills.converse import ConversationalSkill`) instead
    to use any of the features on this page.

!!! note "A second gate sits in front of `converse()`"
    Being on the Active Skills List is necessary but not sufficient. Whether a skill is allowed
    to converse **at all** is a separate, coarser control — `ConverseMode` and the converse
    whitelist/blacklist — covered on [Permissions & Activation Control](permissions.md). If
    `converse()` never fires even though your skill is active, check that gate first.

## Basic usage

This example extends the Ice Cream Skill built up earlier, adding a converse method to catch any brief statement of thanks that might directly follow an order.

```python
from ovos_workshop.skills.converse import ConversationalSkill
from ovos_workshop.decorators import intent_handler


class IceCreamSkill(ConversationalSkill):
    def initialize(self):
        self.flavors = ['vanilla', 'chocolate', 'mint']

    @intent_handler('request.icecream.intent')
    def handle_request_icecream(self, message):
        self.speak_dialog('welcome')
        selection = self.ask_selection(self.flavors, 'what.flavor')
        self.speak_dialog('coming_right_up', {'flavor': selection})

    def converse(self, message):
        if self.voc_match(message.data['utterances'][0], 'Thankyou'):
            self.speak_dialog("you-are-welcome")
            return True

```

In this example:

1. A user might request an ice cream, which `handle_request_icecream()` handles.


2. The skill is added to the system Active Skill list for up to 5 minutes.


3. Any utterance OVOS receives triggers this skill's converse system while it is considered active.


4. If the user follows up with a pleasantry such as "Hey Mycroft, thanks", the converse method matches this vocab against the `Thankyou.voc` file in the skill and speaks the contents of the `you-are-welcome.dialog` file. The method returns `True` and the utterance is consumed, so the intent parsing service never triggers.


5. Any utterance that does not match is silently ignored and continues on to other converse methods, and finally to the intent parsing service.


!!! warning
    Skills that are not [Session](session.md) aware may behave unpredictably with voice satellites. See the [parrot skill](https://github.com/OpenVoiceOS/ovos-skill-parrot/) for an example.


## Active Skill List

A Skill is considered active if it has been called in the last 5 minutes. This window is the
`skills.converse.timeout` config value (default `300` seconds) and can be changed in
`mycroft.conf`:

```jsonc
{
  "skills": {
    "converse": {
      "timeout": 300
    }
  }
}
```

Note the nesting. `ConverseService` reads its config from `Configuration()["skills"]["converse"]`,
so a `converse` block at the top level of `mycroft.conf` is never read. Per-skill overrides go
in the sibling `skill_timeouts` mapping.

Skills are called in order of when they were last active. For example, if a user speaks the following commands:

> Hey Mycroft, set a timer for 10 minutes
>
> Hey Mycroft, what's the weather

The utterance "what's the weather" is first sent to the Timer Skill's `converse()` method, then to the intent service for normal handling, where the Weather Skill is called.

Because the Weather Skill was called, it is now added to the front of the Active Skills List. The next utterance received is directed to:

1. `WeatherSkill.converse()`


2. `TimerSkill.converse()`


3. Normal intent parsing service

When does a skill become active?

1. **Before** an intent is called, the skill is **activated**.


2. If a fallback **returns True** (to consume the utterance), the skill is **activated** right **after** the fallback.


3. If converse **returns True** (to consume the utterance), the skill is **reactivated** right **after** converse.


4. A skill can activate or deactivate itself at any time.

## Making a Skill Active

There are occasions where a user has not triggered a skill, but it should still be considered "Active".

In the case of our Ice Cream Skill, we might have a function that runs when the customer's order is ready.
At this point, we also want to be responsive to the customer's thanks, so we call `self.activate()` to manually add our skill to the front of the Active Skills List.

```python
from ovos_bus_client.message import Message
from ovos_workshop.skills.converse import ConversationalSkill


class IceCreamSkill(ConversationalSkill):
    def on_order_ready(self, message):
        self.activate()
        
    def handle_activate(self, message: Message):
        """
        Called when this skill is considered active by the intent service;
        converse method will be called with every utterance.
        Override this method to do any optional preparation.
        @param message: `{self.skill_id}.activate` Message
        """
        self.log.info("Skill has been activated")

```

## Deactivating a Skill

`ovos-core` prunes the active skill list. Any skill not interacted with for longer than 5 minutes is deactivated.

Individual skills may react to this event, to clean up state or, in some rare cases, to reactivate themselves.

```python
from ovos_bus_client.message import Message
from ovos_workshop.skills.converse import ConversationalSkill


class AlwaysActiveSkill(ConversationalSkill):

    def handle_deactivate(self, message: Message):
        """
        Called when this skill is no longer considered active by the intent
        service; converse method will not be called until skill is active again.
        Override this method to do any optional cleanup.
        @param message: `{self.skill_id}.deactivate` Message
        """
        self.activate()

```

A skill can also deactivate itself at any time.

```python
from ovos_bus_client.message import Message
from ovos_workshop.skills.converse import ConversationalSkill


class LazySkill(ConversationalSkill):

    def handle_intent(self, message: Message):
        self.speak("leave me alone")
        self.deactivate()

```

## Conversational Intents

Skills can have extra intents valid while they are active. Those intents are internal and not part of the main intent system. For an active skill, its `@conversational_intent`-decorated handlers are checked first. Only if none of them match does the skill's own `converse()` method get a chance to run. Both happen before the utterance falls through to the normal Adapt/Padatious intent pipeline.

The `@conversational_intent` decorator defines converse intent handlers.

These intents only trigger after an initial interaction. They are essentially follow-up questions.

```python
from ovos_workshop.skills.converse import ConversationalSkill
from ovos_workshop.decorators import intent_handler, conversational_intent


class DogFactsSkill(ConversationalSkill):

    @intent_handler("dog_facts.intent")
    def handle_intent(self, message):
        fact = "Dogs sense of smell is estimated to be 100,000 times more sensitive than humans"
        self.speak(fact)

    @conversational_intent("another_one.intent")
    def handle_followup_question(self, message):
        fact2 = "Dogs have a unique nose print,  making each one distinct and identifiable."
        self.speak(fact2)

```
> **NOTE**: Only works with `.intent` files. [Adapt](adapt-pipeline.md)/keyword intents are NOT supported.

A more complex example: a game skill that allows saving or exiting the game only during playback.

```python
class MyGameSkill(ConversationalSkill):

    @intent_handler("play.intent")
    def handle_play(self, message):
        self.start_game(load_save=True)

    @conversational_intent("exit.intent")
    def handle_exit(self, message):
        self.exit_game()

    @conversational_intent("save.intent")
    def handle_save(self, message):
        self.save_game()
        
    def handle_deactivate(self, message):
        self.game_over() # user abandoned interaction
        
    def converse(self, message):
        if self.playing:
            # do some game stuff with the utterance
            return True
        return False

```

> **NOTE**: If these intents trigger, they are called **INSTEAD** of `converse`.

---
**Read next:** [Session Aware Skills](session.md)
**Related:** [Permissions & Activation Control](permissions.md) · [Context](context.md) · [Asking the User for Responses in OVOS Skills](prompts.md) · [Fallback Skill](fallbacks.md)

