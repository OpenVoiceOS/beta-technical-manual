# Padatious Intents (Example-Based Intents)

!!! abstract "In a nutshell"
    Example-based intents (also called Padatious or template intents) match a whole phrase
    against a set of sample sentences you provide in `.intent` files. They are generally more
    accurate than keyword intents, and entities inside `{curly braces}` are extracted for you
    automatically. The trade-off is that you must cover the breadth of ways a user might
    phrase a request. See [Intent Design](intents.md) for how the two intent styles compare,
    and [Padatious Pipeline](padatious-pipeline.md) for how the plugin matches these intents
    at runtime. New terms are explained in the [Glossary](glossary.md).

Example-based parsers have several key benefits over other intent parsing technologies.

* Intents are easy to create.


* You can easily extract entities and use these in skills. For example, "Find the nearest gas station" becomes `{ "place":"gas station"}`.


* Disambiguation between intents is easier.


* It is harder to create a bad intent that throws the pipeline plugin off.

> NOTE: Padatious does not handle numbers well. Internally it sees all digits as "#". If you need to match digits, use [Adapt (keyword intents)](intents-adapt.md) instead.

## Creating Intents

Most example-based pipeline plugins use a series of example sentences to train a machine
learning model to identify an intent. Regex can also run behind the scenes, for example to
extract entities.

The examples are stored in a skill's `locale/<lang>/` directory, in files ending in `.intent`.
For example, if you were to create a _tomato_ skill to respond to questions about a _tomato_,
you would create the file

`locale/en-us/what.is.a.tomato.intent`

This file would contain examples of questions asking what a _tomato_ is.

```text
what would you say a tomato is
what is a tomato
describe a tomato
what defines a tomato

```

These sample phrases do not require punctuation like a question mark. We can also leave out
contractions such as "what's", since OVOS automatically expands this to "what is" before
parsing the utterance.

As a rule of thumb, aim for several examples per intent covering the different ways a user
might phrase the request. Too few examples gives the model little to generalize from.

The above example lets us map many phrases to a single intent. Often, though, we need to
extract specific data from an utterance. This might be a date, location, category, or some
other `entity`.

### Defining entities

Let's now find out OVOS's opinion on different types of tomatoes. To do this we will create a
new intent file: `locale/en-us/do.you.like.intent`

with examples of questions about mycroft's opinion about tomatoes:

```text
are you fond of tomatoes
do you like tomatoes
what are your thoughts on tomatoes
are you fond of {type} tomatoes
do you like {type} tomatoes
what are your thoughts on {type} tomatoes

```

Note the `{type}` in the above examples. These are wild cards where matching content is
forwarded to the skill's intent handler.

> **WARNING**: digits are not allowed in the entity name inside the `{}`. **Do NOT** use `{room1}`, use `{room_one}`.

### Specific Entities

In the above example, `{type}` matches anything. This makes the intent flexible, but it will
also match if we say something like "Do you like eating tomatoes?" It would think the type of
tomato is `"eating"`, which doesn't make much sense. Instead, we can specify what type of
things the `{type}` of tomato should be. We do this by defining the type entity file here:

`locale/en-us/type.entity`

which might contain something like:

```text
red
reddish
green
greenish
yellow
yellowish
ripe
unripe
pale

```

You must register this in the skill before use, most commonly in the `initialize()` method:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class TomatoSkill(OVOSSkill):
    def initialize(self):
        self.register_entity_file('type.entity')

```

Now, we can say things like "do you like greenish tomatoes?" and it will tag type as
`"greenish"`. However, if we say "do you like eating tomatoes?", the phrase will not match,
since `"eating"` is not included in our `type.entity` file.

### Number matching

> **Engine-specific:** the `#` digit token and the `:0` unknown-token shown below are **Padatious extensions**. They are **not** part of the [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) Sentence Template Grammar (which has no digit token and no wildcard), so they are not portable to other pipeline plugins. Use them only when you know your skill targets Padatious.

Let's say you are writing an intent to call a phone number. You can make it match only
specific formats of numbers by writing out possible arrangements using `#` where a number
would go. For example, with the following intent:

```text
Call {number}.
Call the phone number {number}.

```

the number.entity could be written as:

```text
+### (###) ###-####
+## (###) ###-####
+# (###) ###-####
(###) ###-####
###-####
###-###-####
###.###.####

### ### ####

```

### Entities with unknown tokens

Let's say you want to create an intent to match places:

```text
Directions to {place}.
Navigate me to {place}.
Open maps to {place}.
Show me how to get to {place}.
How do I get to {place}?

```

This alone will work, but it will still get a high confidence with a phrase like "How do I get
to the boss in my game?" We can try creating a `.entity` file with things like:

```text
New York City

#### Georgia Street
San Francisco

```

The problem is that now anything that is not specifically a mix of New York City, San
Francisco, or something on Georgia Street won't match. Instead, we can specify an unknown word
with `:0`. This would be written as:

```text
:0 :0 City

#### :0 Street
:0 :0

```

Now, while this will still match quite a lot, it will match things like "Directions to
Baldwin City" more than "How do I get to the boss in my game?"

_NOTE: Currently, the number of `:0` words is not fully taken into account, so the above might
match quite liberally. This will change in the future._

### Parentheses Expansion

Sometimes you might find yourself writing many variations of the same thing. For example, to
write a skill that orders food, you might write the following intent:

```text
Order some {food}.
Order some {food} from {place}.
Grab some {food}.
Grab some {food} from {place}.

```

Rather than writing out all combinations of possibilities, you can embed them into one or more
lines by writing each possible option inside parentheses with `|` between each part. For
example, that same intent above could be written as:

```text
(Order | Grab) some {food}
(Order | Grab) some {food} from {place}

```

or even on a single-line:

```text
(Order | Grab) some {food} (from {place} | )

```

> The empty-branch trick `(from {place} | )` makes a segment optional. The portable [OVOS-INTENT-1](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-1.md) equivalent is the square-bracket optional `[from {place}]`. `[x]` is defined as exactly equivalent to `(x|)`. Prefer the bracket form when you want spec-conformant templates.

Nested parentheses are supported to create even more complex combinations, such as the following:

```text
(Look (at | for) | Find) {object}.

```

Which would expand to:

```text
Look at {object}
Look for {object}
Find {object}

```

There is no performance benefit to using parentheses expansion. When used appropriately, this
syntax can be much clearer to read. However, break more complex structures down into multiple
lines to aid readability and reduce false utterances in the model. Overuse can even cause the
model training to time out, making the skill unusable.

## Using it in a Skill

The `intent_handler()` decorator can create an examples-based intent handler by passing in the
filename of the `.intent` file as a string.

You may also see the `@intent_file_handler` decorator used in skills. This is deprecated. You
can now replace any instance of this with the simpler `@intent_handler` decorator.

From our first example above, we created a file `locale/en-us/what.is.a.tomato.intent`. To
register an intent using this file we can use the following decorator, shown on its own.
Place it above a handler method inside your skill class:

```python
@intent_handler('what.is.a.tomato.intent')

```

This _decorator_ must be imported before it is used:

```python
from ovos_workshop.decorators import intent_handler

```

[Learn more about _decorators_ in Python](https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators).

Now we can create our Tomato Skill:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

class TomatoSkill(OVOSSkill):

    def initialize(self):
        self.register_entity_file('type.entity')

    @intent_handler('what.is.a.tomato.intent')
    def handle_what_is(self, message):
        self.speak_dialog('tomato.description')

    @intent_handler('do.you.like.intent')
    def handle_do_you_like(self, message):
        tomato_type = message.data.get('type')
        if tomato_type is not None:
            self.speak_dialog('like.tomato.type',
                              {'type': tomato_type})
        else:
            self.speak_dialog('like.tomato.generic')

```

See [Your First Skill](first-skill.md) for a complete, minimal example of a template-intent skill from scratch.

## Common Problems

See [I am unable to match against the utterance string](intents-adapt.md#i-am-unable-to-match-against-the-utterance-string) in the Adapt intents page. The same lowercase-normalization note applies to template-based intent handlers.

### My intent is defined correctly but never matches

If the `.intent`/`.entity` files look right and the utterance still doesn't match anything, check
whether the intent has actually been **disabled** rather than badly written. A skill can turn
individual intents off with `disable_intent()`, and whitelist/blacklist controls can also gate
off a skill or its converse participation entirely. See [Intent Layers](layers.md) for
per-skill intent enable/disable state and [Permissions & Activation Control](permissions.md) for
the coarser skill-level gates.

---
**Read next:** [Context](context.md) · [Intent Layers](layers.md)
**Related:** [Intent Design](intents.md) · [Adapt Intents (Keyword Intents)](intents-adapt.md) · [Padatious Pipeline](padatious-pipeline.md) · [Test Your Skill](testing-your-skill.md)
