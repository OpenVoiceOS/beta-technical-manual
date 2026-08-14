# Common Query Framework

!!! abstract "In a nutshell"
    When you ask a general-knowledge question like "how old is John Cleese?", several skills might each think they can answer. The Common Query Framework asks all of them at once. Each skill returns an answer with a confidence score, and the framework speaks only the single best one. This mirrors how the [OCP](ocp-skills.md) framework picks who plays your music. See the [Glossary](glossary.md) for related terms.

??? info "📐 Formal specification"
    The Common Query Framework is specified by **[OVOS-COMMON-QUERY-1 — Common Query Pipeline Plugin](https://github.com/OpenVoiceOS/architecture/blob/dev/common-query.md)** (a formal [architecture spec](architecture-specs.md)). A **pipeline plugin** runs a timed scatter-gather contest. It broadcasts `ovos.common_query.ping`, collects `pong` claims from skills that believe they can answer, and requests full answers (`answer` + `conf`) from the claimants. It then ranks them. Only answers at or above the minimum self-reported confidence (default **`0.5`**) survive. If a winner clears the bar, the plugin speaks it (reserved `intent_name` **`common_query`** in the spec — note the shipped plugin still dispatches on the legacy `question:action[.{skill_id}]` topics, not the spec name). Otherwise `match` returns `None` and the pipeline falls through to [fallback](fallbacks.md). This mirrors how [OCP](ocp-skills.md) picks a media provider.

    **The winner may be re-ranked, not just highest-confidence.** If a re-ranker plugin (`ovos-flashrank-reranker-plugin` by default) is installed, the pipeline ignores the skills' self-reported confidence when it picks the winner among answers that cleared the `0.5` bar. Instead it asks the re-ranker to pick the best answer for the phrase. Confidence still gates which answers are eligible. It just isn't the tie-breaker when a re-ranker is present. Without a re-ranker installed, the highest-confidence answer wins (ties are broken arbitrarily).

The Common Query Framework handles general information questions, such as "what is X" or "when did Y". Many skills may implement handlers for the same kind of question. The Common Query Framework queries all of them and selects a single best answer to speak. This works like the [OCP](ocp-skills.md) framework, which handles the common case of "playing" music or other media.

**What / why (beginners):** If your skill can answer free-form questions ("how old is X", "what is Y"), you do not register a `.intent` file for every phrasing. Instead, mark one method with the `@common_query` decorator. The Common Query pipeline detects question-shaped utterances and asks every common-query skill in parallel. Only the winner gets to speak. You return an answer plus a confidence score, and the framework handles the arbitration.

## The `@common_query` decorator

A common-query handler is a regular method on an `OVOSSkill` decorated with `@common_query`. It receives the question phrase and the language, and returns a `(answer, confidence)` tuple — or `None` if it cannot answer.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query


class MyQuestionSkill(OVOSSkill):

    @common_query()
    def handle_query(self, phrase: str, lang: str):
        # return None if you can't answer
        # otherwise return (answer_string, confidence)  where 0.0 <= confidence <= 1.0
        return "the answer", 0.8
```

The handler contract:

- **Input:** `phrase` (the question string) and `lang` (a BCP-47 code).
- **Output:** a `(answer: str, confidence: float)` tuple, or `None`.
- **Confidence** is a float between `0.0` and `1.0`. The pipeline ignores answers with confidence below `0.5`. The highest-confidence answer across all skills is the one spoken to the user.

> The classic `CommonQuerySkill` / `UniversalCommonQuerySkill` base classes and the `CQS_match_query_phrase()` / `CQSMatchLevel` API have been **removed**. Use the `@common_query` decorator on a plain `OVOSSkill` instead. The pipeline still selects a single best answer the same way. Only the skill-side API changed.

## An Example

This example builds a simple skill that tells the age of various Monty Python members.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query

# Dict mapping python members to their age and whether they're alive or dead
PYTHONS = {
    'eric idle': (77, 'alive'),
    'michael palin': (77, 'alive'),
    'john cleese': (80, 'alive'),
    'graham chapman': (48, 'dead'),
    'terry gilliam': (79, 'alive'),
    'terry jones': (77, 'dead')
}


def python_in_utt(utterance):
    """Find a monty python member in the utterance, or return None."""
    for key in PYTHONS:
        if key in utterance.lower():
            return key
    return None


class PythonAgeSkill(OVOSSkill):
    """A Skill for checking the age of the python crew."""

    def format_answer(self, python):
        """Create the answer string for the specified "python" person."""
        age, status = PYTHONS[python]
        key = 'age_alive' if status == 'alive' else 'age_dead'
        return self.dialog_renderer.render(key, {'person': python, 'age': age})

    @common_query()
    def match_age_query(self, phrase, lang):
        # Check if this is an age query and a python is mentioned
        age_query = self.voc_match(phrase, 'age')
        python = python_in_utt(phrase)

        if age_query and python:
            confidence = 1.0 if 'monty python' in phrase.lower() else 0.7
            return self.format_answer(python), confidence
        # can't answer -> return None
        return None
```

`match_age_query()` checks whether this is an age-related question that also names a Monty Python member. If both are true, it returns the rendered answer plus a confidence. Otherwise it returns `None`, to signal it cannot answer.

This provides answers to queries such as

> "how old is Graham Chapman"
>
> "what's Eric Idle's age"

Several toolkits can parse the question itself, including [Adapt](https://pypi.org/project/adapt-parser/), [little questions](https://pypi.org/project/little-questions/), and [padaos](https://pypi.org/project/padaos/). In most cases, `self.voc_match` against a `.voc` file is enough.

## Match Confidence

Confidence is a single float in `[0.0, 1.0]`. Use a higher value when you are more certain you have the exact answer the user wants. Use a lower value when your skill is a general fallback for a category of questions. In the example above, an explicit "monty python" mention bumps confidence to `1.0`, making this skill very likely to be chosen.

Only answers with confidence `>= 0.5` are considered. The pipeline collects all qualifying answers and speaks the single highest-confidence one.

## Selection Callback

In some cases the skill should do extra work only when its answer was the one selected and spoken, for example preparing for follow-up questions or showing an image. Pass a callback to the decorator. It runs after your answer is spoken.

The callback signature is `(phrase, answer, lang)` for a plain function, or `(self, phrase, answer, lang)` for an instance method. The framework inspects the signature and passes `self` only when the first parameter is named `self`.

```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import common_query


def on_selected(self, phrase, answer, lang):
    self.log.info(f"I was selected to answer: {phrase}")
    self.gui.show_text(answer)


class PythonAgeSkill(OVOSSkill):

    @common_query(callback=on_selected)
    def match_age_query(self, phrase, lang):
        ...
        return answer, confidence
```

> The framework speaks the selected answer automatically. Do **not** call `self.speak()` inside the common-query handler. The callback is only for side effects, such as visuals, follow-up state, or logging.

---
**Read next:** [OCP Skills](ocp-skills.md)
**Related:** [Fallback Skill](fallbacks.md) · [Common Query Pipeline](cq-pipeline.md) · [Skill Classes](skill-classes.md) · [Persona Pipeline](persona-pipeline.md)
