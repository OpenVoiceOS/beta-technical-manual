# Fallback + LLM: delegating unmatched utterances to an agent engine

!!! abstract "In a nutshell"
    You build a `FallbackSkill` that hands an unmatched utterance to a `QuestionSolver` plugin as a last resort, using `register_fallback` at a deliberately low priority.

**When you'd want this:** every intent-matching skill has had its turn and none of them understood the utterance. Instead of a flat "sorry, I don't understand," hand it to a language-model-backed plugin and speak whatever it comes back with.

```python
from ovos_plugin_manager.templates.solvers import QuestionSolver
from ovos_workshop.skills.fallback import FallbackSkill


class LLMFallbackSkill(FallbackSkill):
    def initialize(self):
        # a specific solver plugin id, e.g. "ovos-solver-openai-persona-plugin";
        # find_question_solver_plugins lists everything registered under opm.solver.question
        from ovos_plugin_manager.solvers import find_question_solver_plugins
        plugin_id = self.settings.get("solver_plugin", "ovos-solver-openai-persona-plugin")
        plugins = find_question_solver_plugins()
        if plugin_id not in plugins:
            self.log.warning(f"solver plugin '{plugin_id}' not installed, "
                              "falling back to a plain 'I don't understand'")
            self.solver = None
        else:
            self.solver: QuestionSolver = plugins[plugin_id]()

        # broad catch-all: let every more specific fallback/skill go first
        self.register_fallback(self.handle_fallback, 90)

    def can_answer(self, message):
        # required abstract method: a cheap yes/no before handle_fallback runs
        return self.solver is not None

    def handle_fallback(self, message):
        utterance = message.data["utterance"]
        if self.solver is None:
            return False
        answer = self.solver.get_spoken_answer(utterance, lang=self.lang)
        if answer:
            self.speak(answer)
            return True
        return False
```

### Moving parts

- `can_answer(message)` is a **required** abstract method (enforced since ovos-workshop 9.3.9a1): a skill without it fails to load with a `TypeError`. It is a cheap capability check the service can ask before committing to your handler; returning whether the solver loaded is enough here.
- A `FallbackSkill` subclass calls `self.register_fallback(handler, priority)` in `initialize()`. `handler` must return `True` if it produced an answer (stopping the chain) or `False` to let the next-priority fallback try. Priority `90` is deliberately high (tried late) since an LLM should be the *last* resort, not the first. See [Fallback Skill](fallbacks.md) for the recommended priority tiers.
- `QuestionSolver.get_spoken_answer(query, lang=None, units=None)` is the common template every question-answering solver plugin implements. A plugin is just a Python entry point (`opm.solver.question`) you load by id, the same plugin-discovery pattern used everywhere else in OVOS.
- !!! warning "Upcoming: solver templates are being replaced"
      `ovos_plugin_manager.templates.solvers` (including `QuestionSolver`, used above because it is what ships and runs today) is deprecated in favor of `ovos_plugin_manager.templates.agents.AbstractAgentEngine` and the `opm.agents.*` entry point groups. New solver plugins should target the newer API. See [Deprecated Solver Types](agent-plugins.md#deprecated-solver-types) for the full migration table and what each new agent type replaces.
- `self.speak(text)` (a raw string) is used here instead of `self.speak_dialog(...)` because the LLM's answer is not a template. It is already the exact sentence to say.

!!! tip "Full production example"
    [`ovos-skill-wolfie`](https://github.com/OpenVoiceOS/ovos-skill-wolfie), [`ovos-skill-ddg`](https://github.com/OpenVoiceOS/ovos-skill-ddg), and [`ovos-skill-wordnet`](https://github.com/OpenVoiceOS/ovos-skill-wordnet) are real `FallbackSkill` skills that pair `register_fallback` with `@common_query`, so they can answer both as a last-resort fallback and as a ranked candidate earlier in the pipeline. [`ovos-skill-fallback-unknown`](https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown) is the canonical catch-all, registered at priority 100. Priority sets the order fallbacks are tried in: a lower number runs earlier and gets first refusal, and 100 is the terminal tier, tried only after everything else has passed.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Fallback Skill](fallbacks.md) · [Deprecated Solver Types](agent-plugins.md#deprecated-solver-types) · [Common Query Framework](common-query.md)
