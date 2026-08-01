# Building Agent Plugins

!!! abstract "In a nutshell"
    This page teaches you how to write your own agent engine plugin: which base class to
    subclass, what each method contract expects, how to register the entry point, and how
    to test the result. If you only want to *use* existing plugins, read
    [Agent Engine Types](agent-plugins.md) and [Agents & Personas](personas.md) instead.

Every agent engine is a normal Python class that subclasses one abstract base from
`ovos_plugin_manager.templates.agents` (or `ovos_plugin_manager.templates.agent_tools` for
toolboxes) and registers under one `opm.agents.*` entry-point group. OVOS discovers it
through the entry point. There is no registration API to call and no framework to inherit
beyond the one base class.

!!! note "Version requirement"
    The `opm.agents.*` groups need **`ovos-plugin-manager >= 2.3.0a1`** (cap below
    `<3.0.0`). The legacy `QuestionSolver` family (`opm.solver.*`) is deprecated. See the
    migration map in [Specialized Agent Engine Types](advanced-solvers.md#deprecated-solver-types).

---

## Which base class do I need?

Start from the question your plugin answers, not from the technology it wraps:

| Your plugin... | Base class | Group |
|---|---|---|
| holds a conversation and generates replies | `ChatEngine` | `opm.agents.chat` |
| also accepts images, audio, or files | `MultimodalChatEngine` | `opm.agents.chat.multimodal` |
| describes an image/audio/file as text for a text-only engine | `MultimodalAdapter` | `opm.agents.multimodal_adapter` |
| looks up knowledge somewhere else (an API, a database) | `RetrievalEngine` | `opm.agents.retrieval` |
| indexes documents you give it, then searches them | `DocumentIndexerEngine` | `opm.agents.retrieval.documents` |
| indexes question/answer pairs, then matches new questions | `QAIndexerEngine` | `opm.agents.retrieval.qa` |
| pulls the exact answering sentence out of a text you already have | `ExtractiveQAEngine` | `opm.agents.extractive_qa` |
| scores candidate answers against a query | `ReRankerEngine` | `opm.agents.reranker` |
| maps what the user said to one of the options a skill offered | `OptionMatcherEngine` | `opm.agents.option_matcher` |
| decides if a reply means yes, no, or neither | `YesNoEngine` | `opm.agents.yesno` |
| decides if a statement follows from another statement | `NaturalLanguageInferenceEngine` | `opm.agents.nli` |
| replaces pronouns with the entities they refer to | `CoreferenceEngine` | `opm.agents.coref` |
| stores and rebuilds conversation history between turns | `AgentContextManager` | `opm.agents.memory` |
| condenses one long text into a short one | `SummarizerEngine` | `opm.agents.summarizer` |
| condenses a chat transcript into a short text | `ChatSummarizerEngine` | `opm.agents.summarizer.chat` |
| exposes callable functions (tools) to chat engines | `ToolBox` | `opm.agents.toolbox` |

Two rules of thumb when the table is not enough:

- **Does the plugin generate text, or does it select text?** Generators are chat engines
  or summarizers. Selectors are rerankers, matchers, classifiers, or extractive QA.
- **Does the plugin bring its own knowledge, or does it work on text you hand it?**
  Engines that bring knowledge belong in the retrieval family. Engines that only
  transform their input (extract, rank, classify, summarize) do not.

### The retrieval family, disambiguated

Developers most often reach for the wrong class here, so this deserves its own section.
The family has one parent and two children, plus a neighbor that looks similar but is not
retrieval at all.

**`RetrievalEngine`** is the parent contract: one method,
`query(query, lang, k) -> List[Tuple[str, float]]`, which returns up to `k`
`(content, score)` pairs. Subclass it directly when the knowledge lives somewhere the
plugin does **not** manage: a web API (Wikipedia, Wolfram Alpha, DuckDuckGo), a company
wiki, a database another service maintains. Your plugin translates a query into a lookup
and normalizes the results. There is no ingestion step because there is nothing to ingest.

**`DocumentIndexerEngine`** adds `ingest_corpus(corpus: List[str])`. Subclass it when the
plugin **owns a local index over free-text documents**: the caller feeds it texts, the
plugin embeds or indexes them (BM25, a vector store, whatever you choose), and `query`
searches that index. This is the base class for the retrieval half of a RAG pipeline.

**`QAIndexerEngine`** adds `ingest_corpus(corpus: Dict[str, str])`, where keys are
questions and values are answers. Subclass it for FAQ-style data: `query` matches the
user's question against the *indexed questions* and returns the paired *answers*. Use it
instead of `DocumentIndexerEngine` when your data is already question-shaped. Matching
question-to-question is much more accurate than matching a question against raw prose.

**`ExtractiveQAEngine` is not retrieval.** It never searches anything. Its single method,
`get_best_passage(evidence, question, lang)`, receives the evidence text as an argument
and returns the span inside it that answers the question. It is the *last* step of a
pipeline whose earlier steps (often a `RetrievalEngine`) already found the evidence.
[ovos-wikipedia-solver](https://github.com/OpenVoiceOS/ovos-wikipedia-solver) shows the
combination: retrieval fetches a Wikipedia summary, then an extractive QA engine pulls
out the one sentence worth speaking aloud.

A worked example. You want your assistant to answer questions from a folder of markdown
notes:

1. `DocumentIndexerEngine`: ingest the notes, retrieve the top 3 relevant chunks.
2. `ExtractiveQAEngine` (optional): reduce the best chunk to the answering sentence.
3. `ReRankerEngine` (optional): if several chunks disagree, score them against the
   question and keep the winner.

Each stage is a separate, swappable plugin. Resist the urge to build one plugin that does
all three: personas compose engines by config, and a monolith cannot be recombined.

### ReRanker vs OptionMatcher

Both take a string plus a list of strings. They solve different problems:

- `ReRankerEngine.rerank(query, options)` asks "**which candidate best answers this
  query?**". This is semantic relevance. It scores every option and returns the full sorted
  list. Use it to pick between parallel answers (the Common Query pipeline does exactly
  this).
- `OptionMatcherEngine.match_option(utterance, options)` asks "**which of the options I
  offered did the user just pick?**". This is reference resolution, not relevance. The utterance
  may be an ordinal ("the second one"), a synonym, or a paraphrase, and `None` is a valid
  result when the user said something unrelated. `OVOSSkill.ask_selection` uses this
  engine.

If your model scores semantic similarity, it is a reranker. If your logic understands
"the last one", it is an option matcher.

### Chat engines and their satellites

`ChatEngine` is the right base whenever the output is a free-form assistant reply. The
one abstract method is `continue_chat(messages, session_id, lang, units, tools)`, which
takes the full message list (`AgentMessage` objects with `role` and `content`) and returns
one `AgentMessage` with `role=MessageRole.ASSISTANT`. Three points trip people up:

- **The engine is stateless.** History arrives in `messages` on every call. Do not store
  conversation state inside the engine. That is what `AgentContextManager` plugins are
  for. `session_id` exists so engines that front stateful backends can route, not so you
  can build a history cache.
- **Filter unsupported roles.** The message list can contain `SYSTEM`, `DEVELOPER`,
  `USER`, `ASSISTANT`, and `TOOL` roles. If your backend only understands some of them,
  drop or merge the rest inside the plugin.
- **Streaming is opt-in.** Override `stream_tokens` (partial text, not TTS-safe) and
  `stream_sentences` (complete sentences, safe to feed TTS) if the backend can stream.
  The defaults fake it by splitting the full `continue_chat` response, which works but
  gives no latency benefit.

Set the class attribute `supports_tools = True` only if the engine really consumes the
`tools` argument and can return `tool_calls` on its response message. Call
`ToolBox.normalize_tools(tools)` on the argument to get a flat list of OpenAI-spec tool
dicts, whatever mix of `ToolBox` objects and raw dicts the caller passed.

`MultimodalChatEngine` is the same contract over `MultimodalAgentMessage`, which adds
base64-encoded `image_content`, `audio_content`, and `file_content` lists. It is a
separate class on purpose: a persona can check `isinstance` and know whether media
survives or gets dropped. If your backend is text-only but you still want media in, do
not fake multimodality. Pair a plain `ChatEngine` with a `MultimodalAdapter`, whose
single method `convert(MultimodalAgentMessage) -> AgentMessage` renders the media as text
(image captioning, audio transcription, file summarization).

`AgentContextManager` is the memory contract: `get_history(session_id)`,
`update_history(new_messages, session_id)`, and
`build_conversation_context(utterance, session_id)`. The last one is where the
interesting work happens: it returns the message list the chat engine will actually see,
so it is the hook for history trimming, summarization of old turns, long-term memory
lookups, and RAG injection. Two contract rules: the first returned message *may* be a
system message (start from `self.system_prompt`), and the last returned message *must* be
a user message with the current utterance.

### Classifiers: YesNo, NLI, Coreference

`YesNoEngine.yes_or_no(question, response, lang)` returns `True`, `False`, or `None`
(neutral/invalid). It gets the *question* as well as the response because polarity
depends on it: "not at all" confirms "are you sure you want to cancel?" differently than
"do you want more?".

`NaturalLanguageInferenceEngine.predict_entailment(premise, hypothesis, lang)` returns a
bool: does the premise support the hypothesis? Use it as a guardrail, for example to
check that a generated answer is actually supported by the retrieved evidence before
speaking it.

`CoreferenceEngine` is unusual: the base class already implements the memory (a TTL-pruned
`pronoun -> entity` store, `set_context`, `reset_context`, and the public `resolve`
entry point). You implement only two methods: `contains_corefs(text, lang)`, a cheap
check that gates the expensive call, and `solve_corefs(text, lang)`, the actual
resolution ("It was running" → "The dog was running"). Do not reimplement the state
handling.

### Summarizers

`SummarizerEngine.summarize(document, lang)` condenses one plain text.
`ChatSummarizerEngine.summarize(messages, lang)` condenses a `List[AgentMessage]`. It
knows who said what, so it can produce "the user asked for X and the assistant suggested
Y". Memory plugins use chat summarizers to compress old history. Document summarizers
serve skills that read long content aloud. Pick by input type, not by output style.

### ToolBox

`ToolBox` (in `ovos_plugin_manager.templates.agent_tools`) is the only base class that is
not an engine: it *provides* functions for chat engines to call. You implement one
method, `discover_tools() -> List[AgentTool]`, where each `AgentTool` bundles a name, a
description, a Pydantic `ToolArguments` schema, a Pydantic `ToolOutput` schema, and the
callable itself. The base class handles everything else: input/output validation
(`call_tool`), messagebus discovery and remote calls, and export to the OpenAI tool spec
(`openai_tools`). See [Agent Tool Plugins](tool-plugins.md) for the full walkthrough and
[Interoperability](agent-interop.md) for how toolboxes map to MCP.

---

## Rules that apply to every engine

- **Constructor**: `__init__(self, config: Optional[dict] = None)`. Store nothing but
  config at construction time. Load heavy models lazily on first use if startup cost
  matters.
- **Language**: every public method takes an optional BCP-47 `lang`. When it is `None`,
  fall back to `self.lang`, which reads `config["lang"]` and then the active OVOS
  session. **Engines do not auto-translate.** The old solver family translated inputs
  behind your back. Agent engines must either support the language or fail honestly.
- **No bus access**: engines are plain classes with no messagebus connection (only
  `ToolBox` binds to the bus, and only when asked). Keep them importable and testable
  without a running OVOS stack.
- **Return contracts are exact**: a `RetrievalEngine` returns `(content, score)` tuples,
  not bare strings. A `ChatEngine` returns an `AgentMessage`, not a string. An
  `OptionMatcherEngine` returns `None` for no-match rather than guessing. Downstream
  consumers (personas, pipelines, skills) rely on these shapes.

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
lives in [Specialized Agent Engine Types](advanced-solvers.md#deprecated-solver-types).
This section covers the code changes, which are small but not mechanical.

**1. Pick the new base class.** `QuestionSolver` and `ChatMessageSolver` both become
`ChatEngine`. `TldrSolver` becomes `SummarizerEngine`. `EvidenceSolver` becomes
`ExtractiveQAEngine`. `MultipleChoiceSolver` becomes `ReRankerEngine`.
`EntailmentSolver` becomes `NaturalLanguageInferenceEngine`. One exception: if your
`QuestionSolver` was really a knowledge lookup (Wikipedia, Wolfram Alpha, a database),
migrate it to `RetrievalEngine` instead of `ChatEngine`. The solver API had no retrieval
type, so lookups were forced into the Q&A shape. The new API separates them.

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
translated the input and output behind the scenes. **Agent engines never translate.**
After migration your engine receives the user's language as-is. Either handle it or
return nothing for languages you do not support. If the old plugin leaned on `enable_tx`,
that behavior now belongs to explicit translation plugins in the pipeline, not to your
engine.

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
`ovos-plugin-manager` older than 2.3.0a1 the `opm.agents.*` registries do not exist, and
ovos-persona stubs them out so solver-only personas keep working. None of this
back-compat is permanent. The solver classes stay loadable until the next major OPM
release, and new plugins must not use them.

---

## Checklist before you publish

1. The class subclasses exactly one agent base class and implements all its abstract
   methods with the documented signatures and return types.
2. The entry-point group in `pyproject.toml` matches that base class (table above).
3. `__init__` accepts `config=None` and works with an empty config.
4. `lang=None` falls back to `self.lang`, and unsupported languages fail clearly instead of
   silently degrading.
5. Unit tests exercise the engine directly, with no OVOS services running.
6. `find_*_plugins()` discovers the installed plugin under the expected name.

## Related pages

- [Agent Engine Types](agent-plugins.md): group/base-class reference and plugin catalog
- [Specialized Agent Engine Types](advanced-solvers.md): per-engine API details, config
  examples, and the solver migration map
- [Agents & Personas](personas.md): how personas compose the engines you build
- [Agent Tool Plugins](tool-plugins.md): the `ToolBox` walkthrough
- [Agentic Loops](agentic-loop.md): orchestrating engines and tools in a loop
