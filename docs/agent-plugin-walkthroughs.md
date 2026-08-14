# Agent Plugin Walkthroughs and Migration

!!! abstract "In a nutshell"
    This page gives two front-to-back worked examples for writing an agent engine plugin
    (a `DocumentIndexerEngine` and a `ChatEngine`), a guide for migrating an existing
    `QuestionSolver`-family plugin to the new agent engine API, and a pre-publish
    checklist. For picking the right base class and the rules every engine follows, see
    [Building Agent Plugins](building-agent-plugins.md).

---

## Walkthrough: a DocumentIndexerEngine

A minimal but real plugin, front to back. The example wraps a naive keyword index. Swap
the internals for embeddings and this structure does not change.

**Project layout:**

```
ovos-notes-retrieval-plugin/
├── pyproject.toml
└── ovos_notes_retrieval/
    └── __init__.py
```

**`ovos_notes_retrieval/__init__.py`:**

```python
from typing import Dict, List, Optional, Tuple

from ovos_plugin_manager.templates.agents import DocumentIndexerEngine


class NotesRetrieval(DocumentIndexerEngine):
    """Keyword search over an in-memory document corpus."""

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.documents: List[str] = []
        self.min_score: float = self.config.get("min_score", 0.0)

    def ingest_corpus(self, corpus: List[str]):
        self.documents += corpus

    def query(self, query: str, lang: Optional[str] = None,
              k: int = 3) -> List[Tuple[str, float]]:
        lang = lang or self.lang
        words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            hits = words & set(doc.lower().split())
            score = len(hits) / len(words) if words else 0.0
            if score > self.min_score:
                scored.append((doc, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]
```

**`pyproject.toml`**. The entry point is what makes it a plugin. The group must match
the base class, and the entry-point name (left of `=`) is the string users put in their
config:

```toml
[project]
name = "ovos-notes-retrieval-plugin"
version = "0.1.0"
dependencies = ["ovos-plugin-manager>=2.3.0a1,<3.0.0"]

[project.entry-points."opm.agents.retrieval.documents"]
ovos-notes-retrieval = "ovos_notes_retrieval:NotesRetrieval"
```

Every `opm.agents.*` group has a parallel `*.config` group (here
`opm.agents.retrieval.documents.config`) where a plugin can register a dict of
config metadata for installers and GUIs. It is optional. Add it once the plugin has
settings worth advertising.

**Test it without OVOS**. Engines are plain classes, so a unit test is just:

```python
from ovos_notes_retrieval import NotesRetrieval

engine = NotesRetrieval()
engine.ingest_corpus(["the mail server runs on port 25",
                      "backups run every night at 3am"])
results = engine.query("when do backups run?", k=1)
assert "backups" in results[0][0]
```

**Verify discovery** after `pip install -e .`:

```python
from ovos_plugin_manager.agents import find_document_indexer_plugins
print(find_document_indexer_plugins())
# {'ovos-notes-retrieval': <class 'ovos_notes_retrieval.NotesRetrieval'>}
```

Each group has a matching `find_*_plugins()` / `load_*_plugin(name)` pair in
`ovos_plugin_manager.agents`, such as `find_chat_plugins` and `find_reranker_plugins`.
`load_*` returns the uninstantiated class. You construct it with your config dict.

---

## Walkthrough: a ChatEngine

The same skeleton for a conversational engine, wrapping any backend that takes a message
list:

```python
from typing import Iterable, List, Optional

from ovos_plugin_manager.templates.agents import (AgentMessage, ChatEngine,
                                                  MessageRole, ToolsArg)


class MyChatEngine(ChatEngine):

    supports_tools = False  # set True only if you handle the tools arg

    def continue_chat(self, messages: List[AgentMessage],
                      session_id: str = "default",
                      lang: Optional[str] = None,
                      units: Optional[str] = None,
                      tools: ToolsArg = None) -> AgentMessage:
        lang = lang or self.lang
        # 1. filter roles your backend does not understand
        history = [m for m in messages
                   if m.role in (MessageRole.SYSTEM, MessageRole.USER,
                                 MessageRole.ASSISTANT)]
        # 2. call the backend
        reply: str = self._backend_generate(history, lang)
        # 3. wrap the reply
        return AgentMessage(role=MessageRole.ASSISTANT, content=reply)

    def stream_sentences(self, messages, session_id="default",
                         lang=None, units=None) -> Iterable[str]:
        # override only if the backend can really stream;
        # yield complete sentences, safe for TTS
        yield from self._backend_stream(messages, lang or self.lang)
```

Registered under:

```toml
[project.entry-points."opm.agents.chat"]
my-chat-engine = "my_chat_plugin:MyChatEngine"
```

Once installed, a persona can select it by entry-point name, with no code changes anywhere
else in the stack. See [Agents & Personas](personas.md) for the persona JSON format.

---

## Migrating a solver plugin to an agent engine

The old `QuestionSolver` family (`opm.solver.*` entry points, classes in
`ovos_plugin_manager.templates.solvers`) is deprecated. The entry-point-to-class mapping
lives in [Deprecated Solver Types](agent-plugins.md#deprecated-solver-types).
This section covers the code changes, which are small but not mechanical.

**1. Pick the new base class.**

| Old solver class | New base class |
|---|---|
| `QuestionSolver` | `ChatEngine` (or `RetrievalEngine` — see exception below) |
| `ChatMessageSolver` | `ChatEngine` |
| `TldrSolver` | `SummarizerEngine` |
| `EvidenceSolver` | `ExtractiveQAEngine` |
| `MultipleChoiceSolver` | `ReRankerEngine` |
| `EntailmentSolver` | `NaturalLanguageInferenceEngine` |

One exception: if your `QuestionSolver` was really a knowledge lookup (Wikipedia, Wolfram
Alpha, a database), migrate it to `RetrievalEngine` instead of `ChatEngine`. The solver API
had no retrieval type, so lookups were forced into the Q&A shape. The new API separates them.

**2. Rename the methods.** For a `QuestionSolver` moving to `ChatEngine`, the core
change is from string-in/string-out to messages-in/message-out:

```python
# before (QuestionSolver)
def get_spoken_answer(self, query: str, lang=None, units=None) -> str:
    return self._answer(query)

# after (ChatEngine)
def continue_chat(self, messages, session_id="default",
                  lang=None, units=None, tools=None) -> AgentMessage:
    query = messages[-1].content  # last message is the user turn
    return AgentMessage(role=MessageRole.ASSISTANT,
                        content=self._answer(query))
```

`ChatMessageSolver.get_chat_completion` maps almost one-to-one to `continue_chat`. Wrap
the returned string in an `AgentMessage` and update the dict-style messages to
`AgentMessage` dataclasses. `stream_utterances` becomes `stream_sentences`.

**3. Drop the auto-translation assumptions.** This is the trap. `QuestionSolver` had
`enable_tx` and bidirectional auto-translation: a solver could declare
`supported_langs = ["en"]` and still receive every language, because the base class
translated the input and output behind the scenes.

**Agent engines never translate.** After migration your engine receives the user's
language as-is. Either handle it or return nothing for languages you do not support.

Translation is still the recommended strategy for engines whose backend is inherently
monolingual (Wolfram Alpha and most web APIs only speak English). What changed is who
does it: the base class no longer translates for you, so the plugin re-implements it
explicitly. Use the translation plugin system instead of hardcoding one translator.
`OVOSLangTranslationFactory.create()` (in `ovos_plugin_manager.language`) returns the
`LanguageTranslator` the user configured in the central `"language"` section of
`mycroft.conf`, so every plugin honors one shared translation config:

```python
from ovos_plugin_manager.language import OVOSLangTranslationFactory

class WolframEngine(RetrievalEngine):
    def __init__(self, config=None):
        super().__init__(config)
        self.translator = OVOSLangTranslationFactory.create()

    def query(self, query, lang=None, k=3):
        lang = lang or self.lang
        if lang != "en":
            query = self.translator.translate(query, target="en", source=lang)
        answer = self._ask_wolfram(query)
        if lang != "en":
            answer = self.translator.translate(answer, target=lang, source="en")
        return [(answer, 1.0)]
```

One warning about local translation models: several OVOS components can each load
translation plugins, and each `create()` call builds its own instance. With a heavy
local model such as NLLB, that means the same weights in memory once per component.
On such setups configure a remote translation plugin (a translate server) so the model
loads once, in one process, and everything else calls it over HTTP.

**4. Drop solver-specific plumbing.** There is no `priority` attribute, no internal
cache, and no `spoken_answer` convenience wrapper. Persona config order replaces
priority. `ChatEngine.get_response(utterance)` replaces `spoken_answer` for quick tests.

**5. Swap the entry point.** Change the group in `pyproject.toml`, keep the entry-point
name if you can. Users reference plugins by that name in persona files, so keeping it
makes the migration invisible to them:

```toml
# before
[project.entry-points."opm.solver.question"]
my-plugin = "my_plugin:MySolver"

# after
[project.entry-points."opm.agents.chat"]
my-plugin = "my_plugin:MyChatEngine"
```

During a transition period a plugin may register under **both** groups, with the old
class delegating to the new one. Ship the dual registration in a minor release, then
drop the solver entry point in the next major.

### How ovos-persona keeps old solvers working

You do not need to migrate everything at once, because
[ovos-persona](https://github.com/OpenVoiceOS/ovos-persona) loads both generations side
by side. Its `QuestionSolversService` merges the plugin registries into a single handler
pool: legacy `opm.solver.question` and `opm.solver.chat` plugins load right next to
`opm.agents.chat`, `opm.agents.chat.multimodal`, and the three retrieval groups.

At answer time the service walks the persona's handler list in config order and
dispatches on type:

- `ChatEngine` / `MultimodalChatEngine` → `continue_chat` (or `stream_sentences` when
  streaming), full history passed through.
- `RetrievalEngine` / `DocumentIndexerEngine` / `QAIndexerEngine` → `query(last_utterance, k=1)`,
  and the top document becomes the answer.
- `ChatMessageSolver` (legacy) → `get_chat_completion` with the full message list.
- `QuestionSolver` (legacy) → `spoken_answer(last_utterance)`. **Chat history is
  silently dropped**, because the old contract is single-turn. This is the main
  functional reason to migrate conversational plugins: under a persona, a
  `QuestionSolver` answers every turn as if it were the first.

The first handler that returns a non-empty answer wins. A persona JSON can therefore mix
generations freely during migration:

```json
{
  "name": "MixedPersona",
  "solvers": [
    "my-new-chat-engine",
    "ovos-solver-failure-plugin"
  ]
}
```

The `"solvers"` key is itself legacy naming. Newer configs use `"handlers"`, and
ovos-persona accepts both. One more back-compat layer sits below all this: with
an `ovos-plugin-manager` from before the early 2.2.x alphas the `opm.agents.*` registries
do not exist (they landed piecemeal across 2.2.x; the example pin of `>=2.3.0a1` above is
the safe floor that has all of them), and
ovos-persona stubs them out so solver-only personas keep working. None of this
back-compat is permanent. The solver classes stay loadable until the next major OPM
release, and new plugins must not use them.

---

## Checklist before you publish

1. The class subclasses exactly one agent base class and implements all its abstract
   methods with the documented signatures and return types.
2. The entry-point group in `pyproject.toml` matches that base class (see the table in
   [Building Agent Plugins](building-agent-plugins.md#which-base-class-do-i-need)).
3. `__init__` accepts `config=None` and works with an empty config.
4. `lang=None` falls back to `self.lang`, and unsupported languages fail clearly instead of
   silently degrading.
5. Unit tests exercise the engine directly, with no OVOS services running.
6. `find_*_plugins()` discovers the installed plugin under the expected name.

---
**Read next:** [Agentic Loop Architectures](agentic-loop.md)
**Related:** [Building Agent Plugins](building-agent-plugins.md) · [Agent Engine Types](agent-plugins.md) · [Agent Tool Plugins](tool-plugins.md) · [Personas & PersonaService](personas.md)
