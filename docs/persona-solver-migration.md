# Move From Solver Plugins to Agent Engines

--8<-- "snippets/alpha-only.md"

This page ports a solver plugin to the agent engine classes, and updates a persona file that lists solver plugins. You maintain a solver plugin, or a persona file that names solver plugins. Solver plugins still load and answer, and each solver class logs a deprecation warning. A `ChatEngine` gets the full message list and the session id, so it can use the persona memory. A `QuestionSolver` gets only the last question.

## Class mapping

| Solver base class | Agent base class | Method to implement |
|---|---|---|
| `QuestionSolver` | `ChatEngine` | `continue_chat(messages, session_id, lang, units, tools)` |
| `ChatMessageSolver` | `ChatEngine` | `continue_chat(messages, session_id, lang, units, tools)` |
| `CorpusSolver`, `QACorpusSolver` | `RetrievalEngine` | `query(query, lang, k)` |

The solver classes are in `ovos_plugin_manager.templates.solvers`. The agent classes are in `ovos_plugin_manager.templates.agents`.

## Port a solver

1. Install the packages:

    ```bash
    pip install --pre ovos-persona ovos-openai-plugin
    ```

2. Run this script. It runs a solver and its port side by side:

    ```python
    from typing import List, Optional

    from ovos_plugin_manager.templates.agents import AgentMessage, ChatEngine, MessageRole
    from ovos_plugin_manager.templates.solvers import QuestionSolver


    class EchoSolver(QuestionSolver):
        def get_spoken_answer(self, query, lang=None, units=None):
            return f"you said {query}"


    class EchoEngine(ChatEngine):
        def continue_chat(self, messages: List[AgentMessage], session_id: str = "default",
                          lang: Optional[str] = None, units: Optional[str] = None,
                          tools=None) -> AgentMessage:
            return AgentMessage(MessageRole.ASSISTANT, f"you said {messages[-1].content}")


    print("solver:", EchoSolver().spoken_answer("hello", lang="en-US"))
    reply = EchoEngine().continue_chat([AgentMessage(MessageRole.USER, "hello")], session_id="kitchen")
    print("engine:", reply.content)
    ```

Output of a run, with the log lines shortened:

```text
WARNING - Deprecation version=3.0.0. ... ovos_plugin_manager.templates.solvers has been deprecated and will be removed in the next major release.
WARNING - Deprecation version=3.0.0. ... QuestionSolver has been deprecated and will be removed in the next major release. Please migrate your code to use ChatEngine / RetrievalEngine
solver: you said hello
engine: you said hello
```

The `version` in the warning is the next major version of the installed `ovos-plugin-manager`. It does not state when the class goes away.

Register the engine class under an agent entry point group in `pyproject.toml`. A chat engine uses `opm.agents.chat`. A retrieval engine uses `opm.agents.retrieval`.

## Update a persona file

A persona file names plugins by their entry point names. These names belong to no package:

| Name that does not load | Entry point name |
|---|---|
| `ovos-solver-openai-plugin` | `ovos-chat-openai-plugin` |
| `ovos-solver-wikipedia-plugin` | `ovos-wikipedia-plugin` |
| `ovos-solver-ddg-plugin` | `ovos-ddg-plugin` |
| `ovos-solver-plugin-wolfram-alpha` | `ovos-wolfram-alpha-plugin` |
| `ovos-solver-wordnet-plugin` | `ovos-wordnet-plugin` |

A persona with one unknown or uninstalled name does not load. The log says:

```text
Failed to load '<persona>': '<name>' not installed
```

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Agent Engine Types](agent-plugins.md)
- [Building Agent Plugins](building-agent-plugins.md)
