# Adapt Intents (Keyword Intents)

!!! abstract "In a nutshell"
    Keyword intents (also called Adapt intents) match an utterance by looking for required
    and optional keywords, not whole phrases. You define the keywords in `.voc` files and,
    optionally, capture free-form entities with `.rx` regex files. Keyword intents are more
    flexible than template intents and integrate tightly with
    [conversational context](context.md), but a badly designed one can produce false
    matches. See [Intent Design](intents.md) for how the two intent styles compare, and
    [Adapt Pipeline](adapt-pipeline.md) for how the plugin matches these intents at runtime.
    New terms are explained in the [Glossary](glossary.md).

Keyword-based pipeline plugins determine user intent from a list of keywords or entities
contained in a user's utterance.

## Defining keywords and entities

### Vocab (.voc) Files

Vocab files define keywords that the pipeline plugin looks for in a user's utterance to
determine their intent.

These files live in the skill's `locale/<lang>/` directory (e.g. `locale/en-us/Potato.voc`).
They can have one or more lines listing synonyms or terms with the same meaning in the
context of this skill. OVOS matches _any_ of these keywords with the intent.

> Language directories are named with BCP-47 tags and compared case-insensitively, so `en-us` and `en-US` denote the same language (OVOS-INTENT-2 §3). The older split layout (`vocab/<lang>/`, `regex/<lang>/`, `dialog/<lang>/`) is still supported for legacy skills, but new skills should use a single `locale/<lang>/` folder per language.

Consider a simple `Potato.voc`. Within this file we might include:

```text
potato
potatoes
spud

```

If the User speaks _either_:

> potato

or

> potatoes

or

> spud

OVOS matches this to any keyword intents that use the `Potato` keyword.

### Regular Expression (.rx) Files

Regular expressions (or regex) let us capture entities based on the structure of an utterance.

We strongly recommend you avoid regex. It is hard to make portable across languages, hard to
translate, and the reported confidence of the intents is not great.

We suggest using template intents (`.intent` files) instead if you find yourself needing regex.
See [Padatious Intents](intents-padatious.md).

> Regex (`.rx`) is **not** a resource role in the [OVOS-INTENT-2](https://github.com/OpenVoiceOS/architecture/blob/dev/intent-2.md) specification. It is an Adapt-specific extension. Prefer `.entity` slot constraints or template intents for portability.

These files live in the skill's `locale/<lang>/` directory. They can have one or more lines
providing different ways an entity may be referenced. OVOS executes these lines in the order
they appear and returns the first result as an entity to the intent handler.

Let's consider a `type.rx` file to extract the type of potato we are interested in. Within this file we might include:

```text
.* about (?P<Type>.*) potatoes
.* (make|like) (?P<Type>.*) potato

```

**What is this regex doing?** `.*` matches zero, one, or more of any single character.
`(?P<Type>.*)` is known as a named capturing group. The variable name is defined between the
"<>", and what is captured is defined after this name. In this case we use `.*` to capture
anything.

[Learn more about Regular Expressions](https://github.com/ziishaned/learn-regex/blob/master/README.md).


So our first line would match an utterance such as:

> Tell me about _sweet potatoes_

The second line will match either:

> Do you like _deep fried potato_

or

> How do I make _mashed potato_

From these three utterances, what will the extracted `Type` be:\
1\. `sweet`\
2\. `deep fried`\
3\. `mashed`

This `Type` will be available to use in your Skill's Intent Handler on the `message` object. We can access this using:

```text
message.data.get('Type')

```

## Using Keyword Intents in a Skill

Now that we have a vocab and a regular expression defined, let's look at how to use these in a
simple skill.

For the following example we will use the two files we outlined above:

* `Potato.voc`


* `type.rx`

We will also add some new `.voc` files:

* `Like.voc`: containing a single line "like"


* `You.voc`: containing a single line "you"


* `I.voc`: containing a single line "I"

### Creating the Intent Handler

To construct a keyword intent, we use the `intent_handler()` decorator and pass in the `IntentBuilder` helper class.

[Learn more about _decorators_ in Python](https://en.wikipedia.org/wiki/Python\_syntax\_and\_semantics#Decorators).

Both of these must be imported before we can use them:

```python
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.decorators import intent_handler

```

The `IntentBuilder` is then passed the name of the intent as a string, followed by one or more
parameters that correspond with one of our `.voc` or `.rx` files.

*Excerpt: the decorator on its own. A complete skill using it appears further below.*

```python
@intent_handler(IntentBuilder('IntentName')
                              .require('Potato')
                              .require('Like')
                              .optionally('Type')
                              .one_of('You', 'I'))

```

In this example:

* the `Potato` and `Like` keywords are required. Each must be present for the intent to match.


* the `Type` entity is optional. A stronger match happens if this is found, but it is not required.


* we require at least one of the `You` or `I` keywords.

What are some utterances that would match this intent?

> Do you like potato? Do you like fried potato? Will I like mashed potato? Do you think I would like potato?

What are some utterances that would _not_ match the intent?

> How do I make mashed potato?

_The required `Like` keyword is missing._

> Is it like a potato?

_Neither the `You` nor `I` keyword is found._

### Including it in a Skill

Now we can create our Potato Skill:

```python
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler


class PotatoSkill(OVOSSkill):

    @intent_handler(IntentBuilder('WhatIsPotato').require('What')
                    .require('Potato'))
    def handle_what_is(self, message):
        self.speak_dialog('potato.description')

    @intent_handler(IntentBuilder('DoYouLikePotato').require('Potato')
                    .require('Like').optionally('Type').one_of('You', 'I'))
    def handle_do_you_like(self, message):
        potato_type = message.data.get('Type')
        if potato_type is not None:
            self.speak_dialog('like.potato.type',
                              {'type': potato_type})
        else:
            self.speak_dialog('like.potato.generic')

```

See [Skill Examples](skill-examples.md) for real, working skills that use keyword intents this way.


## Common Problems

### More vocab!

One of the most common mistakes when getting started with skills is that the vocab file
doesn't include all the keywords or terms a user might use to trigger the intent. Map out
your skill and test the interactions with others to see how they might ask questions
differently.

### I have added new phrases in the .voc file, but Mycroft isn't recognizing them

1. OVOS normalizes compound words like "don't", "won't", and "shouldn't", so they become "do not", "will not", "should not". Use the normalized words in your `.voc` files. `ovos-utterance-normalizer` can also strip definite/indefinite articles via its `remove_articles` config option, but this is off by default, so "the"/"a"/"an" reach the matcher unchanged on a stock install — no need to avoid them in your `.voc` or `.rx` files.


2. A tab is not 4 spaces. Sometimes your text editor or IDE automatically replaces tabs with spaces or vice versa. This may lead to an indentation error. Make sure there are no extra tabs and that your editor doesn't replace your spaces.


3. Wrong order of file directories is a common mistake. You have to make a language sub-folder inside the dialog, vocab, or locale folders, such as `skill-dir/locale/en-us/somefile.dialog`. Make sure your `.voc` files and `.dialog` files sit inside a language subfolder.

### I am unable to match against the utterance string

The speech-to-text engine returns the utterance string all lowercase. Convert any string
matching you do to lowercase as well. For example, here is a method excerpt from inside a
skill class:

```python
    @intent_handler(IntentBuilder('Example').require('Example').require('Intent'))
    def handle_example(self, message):
        utterance = message.data.get('utterance')
        if 'Proper Noun'.lower() in utterance:
            self.speak('Found it')

```

### My intent is defined correctly but never matches

If the `.voc`/`.rx` files look right and the utterance still doesn't match anything, check
whether the intent has actually been **disabled** rather than badly written. A skill can turn
individual intents off with `disable_intent()`, and whitelist/blacklist controls can also gate
off a skill or its converse participation entirely. See [Intent Layers](layers.md) for
per-skill intent enable/disable state and [Permissions & Activation Control](permissions.md) for
the coarser skill-level gates.

---
**Read next:** [Padatious Intents (Example-Based Intents)](intents-padatious.md)
**Related:** [Intent Design](intents.md) · [Intent Layers](layers.md) · [Adapt Pipeline Plugin](adapt-pipeline.md) · [Context](context.md)
