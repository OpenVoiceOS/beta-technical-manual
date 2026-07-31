# Skill Structure

!!! abstract "In a nutshell"
    A skill is just a folder of files, organized in a predictable way so OVOS knows where to find everything. Some files hold the words your skill listens for and the phrases it says back, grouped by language so the skill can be translated. Another file holds the actual instructions for what the skill does. This page walks through that layout piece by piece, so you can recognize each part when you open a skill. New terms are explained in the [Glossary](glossary.md).

## Anatomy of a [Skill](skill-design-guidelines.md)

### `vocab`, `dialog`, and `locale` directories

The `dialog`, `vocab`, and `locale` directories contain subdirectories for each spoken language the skill supports.
The subdirectories are named using the [IETF language tag](https://en.wikipedia.org/wiki/IETF\_language\_tag) for the
language.
For example, Brazilian Portuguese is 'pt-br', German is 'de-de', and Australian English is 'en-au'.

`dialog` and `vocab` are **deprecated**. They are still supported, but we strongly recommend you use `locale` for new
skills.

!!! note "If both layouts exist for the same resource, `locale` wins"
    Resource lookup (`find_resource`/`load_data_files` in `ovos_workshop/resource_files.py`)
    checks the `locale/<lang>/` layout before falling back to the legacy `dialog/<lang>/`,
    `vocab/<lang>/`, `regex/<lang>/` layout. If a skill somehow ships the same filename in both
    places, the `locale` copy is what gets loaded.

Inside the `locale` folder you will find subfolders for each language (e.g. `en-us`). Often all you need to do
to translate a skill is add a new folder for your language here.

Each language folder can have the structure it wants. You may see files grouped by type in a subfolder, or all in the base
folder.

You will find several unfamiliar file extensions in this folder, but these are simple text files.

* `.dialog` files used for defining speech responses


* `.intent` files define **template (example-based) intents** — whole sample phrases
  (matched by [Padatious](padatious-pipeline.md))


* `.voc` files define the keywords used by **keyword (rule-based) intents**
  (matched by [Adapt](adapt-pipeline.md))


* `.entity` files define a named entity used by template intents

### __init__.py

The `__init__.py` file is where most of the Skill is defined using Python code.

#### Importing libraries

```python
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

```

This section of code imports the required _libraries_. Some libraries will be required on every Skill, and your skill
may need to import additional libraries.

#### Class definition

The `class` definition extends the `OVOSSkill` class:

```python
class HelloWorldSkill(OVOSSkill):

```

The class should be named logically, for example "TimeSkill", "WeatherSkill", "NewsSkill", "IPaddressSkill". If you
would like guidance on what to call your Skill, please join
the [skills Channel on OVOS Chat](https://matrix.to/#/#openvoiceos-skills:matrix.org).

Inside the class, methods are then defined.

#### __init__()

This method is the _constructor_. It is called when the Skill is first constructed. It is often used to declare state
variables or perform setup actions. It cannot fully use `OVOSSkill` methods, since the skill is not fully initialized yet at this point.

**You usually don't have to include the constructor.**

An example `__init__` method might be:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.already_said_hello = False
    self.be_friendly = True


```

The `__init__` method must accept at least `skill_id` and `bus` kwargs and pass them to `super()`. We recommend passing `*args, **kwargs` instead, as in the example above.

**NOTE**: `self.skill_id`, `self.file_system`, `self.settings`, and `self.bus` are only available after the call to `super()`. If you need them earlier, consider using `initialize` instead.


#### initialize()

This method is called during `__init__`. If you implemented `__init__` in your skill, it is called during `super()`.

Perform any final setup needed for the skill here. This function is invoked after the skill is fully constructed and
registered with the system. Intents are registered and Skill settings are available.

See the property-availability note above (`__init__()`). This is where you should access `self.skill_id`, `self.bus`, `self.settings`, and `self.file_system` if you cannot wait until they are set.

```python
def initialize(self):
    my_setting = self.settings.get('my_setting')

```

#### @intent_handler

We can use the `initialize` function to manually register intents. The `@intent_handler` decorator is a
cleaner way to do this. We cover the different [Intents](intents.md) shortly.

In skills we can see the two different intent styles.

1. A **keyword (rule-based) intent**, triggered by a keyword defined in a `ThankYouKeyword.voc`
   file (matched by Adapt).

```python
   @intent_handler(IntentBuilder('ThankYouIntent').require('ThankYouKeyword'))
   def handle_thank_you_intent(self, message):
       self.speak_dialog("welcome")

```

2. A **template (example-based) intent**, triggered by a list of sample phrases (matched by
   Padatious).

```python
   @intent_handler('HowAreYou.intent')
   def handle_how_are_you_intent(self, message):
       self.speak_dialog("how.are.you")

```

In both cases, the function receives two _parameters_:

* `self` - a reference to the HelloWorldSkill object itself


* `message` - an incoming message from the `messagebus`.

Both intents call the `self.speak_dialog()` method, passing the name of a dialog file to it. In this
case `welcome.dialog` and `how.are.you.dialog`.

#### stop()

You will usually also have a `stop()` method.

The `stop` method is called anytime a User says "Stop" or a similar command. It is useful for stopping any output or process that a User might want to end without needing to issue a Skill specific utterance such as media playback or an expired alarm notification.

In the following example, we call a method `stop_beeping` to end a notification that our Skill has created.

If the skill "consumed" the stop signal, it should return True. Otherwise it should return False.

```python
    def stop(self):
        if self.beeping:
            self.stop_beeping()
            return True
        return False

```

If a Skill has any active functionality, the stop() method should terminate the functionality, leaving the Skill in a known good state.

When the skill returns True, no other skill is stopped. When it returns False, the next active skill attempts to stop, and so on until something consumes the stop signal.

#### shutdown()

The `shutdown` method is called during Skill process termination.
It performs any final actions to ensure all running processes and operations stop safely.
This is useful for Skills that have scheduled future events, are writing to a file or database, or have started other processes.

In the following example we cancel a scheduled event and call a method in our Skill to stop a subprocess we initiated.

```python
    def shutdown(self):
        self.cancel_scheduled_event('my_event')
        self.stop_my_subprocess()

```

### settingsmeta.yaml *(optional, legacy)*

This optional file describes a settings UI for the skill. It is a **legacy format from the old
Mycroft backend** that OVOS does not run, so it is **usually absent**. Skills handle their settings
without it, and only some community config tools still read it.

Jump to [Skill Settings Meta](skill-settings-meta.md) for the format, and [Skill Settings](skill-settings.md) for how skills actually read and write settings.


### Packaging and Distribution

Modern OVOS skills use `pyproject.toml` for packaging. This allows your skill to be installed as a standard Python package and registered as a plugin via entry points.

#### `pyproject.toml` Example

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ovos-skill-hello-world"
version = "0.1.0"
description = "A simple hello world skill for OpenVoiceOS"
readme = "README.md"
authors = [{ name = "Your Name", email = "you@example.com" }]
license = { text = "Apache-2.0" }
dependencies = [
    "ovos-workshop>=0.0.1"
]

[project.entry-points."opm.skill"]
"ovos-skill-hello-world.yourname" = "ovos_skill_hello_world:HelloWorldSkill"

[tool.setuptools.package-data]
"*" = ["locale/**/*", "ui/**/*", "*.json"]

```

#### `skill.json`

This is an optional, per-language file. It lives alongside your dialog and intent
files (e.g. `locale/en-us/skill.json`). At runtime it is read for exactly one purpose:
registering example utterances with the homescreen, so the launcher can show sample things
to say for that language.

!!! note "Same filename, two roles"
    The `locale/<lang>/skill.json` shown here carries only the runtime `examples`. The **store
    metadata** file of the same name, carrying `source`, `package_name`, `pip_spec`,
    `extra_plugins`, `tags`, `icon`, etc. for the skills marketplace and installer, is a
    separate, broader schema documented in full on the [Skill Metadata File](skill-json.md) page.
    `ovos-workshop` never installs anything from either file.

```json
{
    "examples": ["hello", "say hello"]
}

```

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*
