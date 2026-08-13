# Agent Tool Plugins

!!! abstract "In a nutshell"
    These plugins give an AI assistant real *abilities*, like fetching information or performing an action, instead of only talking. Each "tool" is described in a standard way. The AI can read this description to learn what the tool does and what information it needs. See [Agentic Loops](agentic-loop.md) for how an assistant decides to use them, and the [Glossary](glossary.md) for unfamiliar terms.

The OPM `ToolBox` framework provides a standardized mechanism for exposing discoverable, schema-validated functions to OVOS agents (persona solvers, agentic loops, MCP/UTCP clients). For full authoring documentation see the [Plugin Manager reference](plugin-manager.md).

---

## OPM ToolBox Interface

Every `ToolBox` plugin:

1. Declares its tools via `discover_tools()`, returning a list of `AgentTool` instances.
2. Each `AgentTool` carries Pydantic `argument_schema` and `output_schema` models — these are converted to JSON Schema for LLM tool-use / function-calling.
3. Registers messagebus handlers automatically when a bus is injected.

### Plugin entry point

```python
# pyproject.toml
[project.entry-points."opm.agents.toolbox"]
my-toolbox = "my_package:MyToolBox"
```

### Authoring a ToolBox plugin

A minimal `ToolBox` implementing a single `add` tool:

```python
from typing import List
from ovos_plugin_manager.templates.agent_tools import ToolBox, AgentTool, ToolArguments, ToolOutput

class AddArgs(ToolArguments):
    a: float
    b: float

class AddResult(ToolOutput):
    sum: float

def add(args: AddArgs) -> AddResult:
    return AddResult(sum=args.a + args.b)

class MathToolBox(ToolBox):
    def __init__(self, config=None, bus=None):
        # the plugin declares its own id, matching the entry-point name
        super().__init__(toolbox_id="my-toolbox", config=config, bus=bus)

    def discover_tools(self) -> List[AgentTool]:
        return [
            AgentTool(
                name="add",
                description="Add two numbers together.",
                argument_schema=AddArgs,
                output_schema=AddResult,
                tool_call=add,
            )
        ]
```

The base class signature is `ToolBox.__init__(self, toolbox_id, config=None, bus=None)` —
`toolbox_id` is required and positional. A plugin normally hides it, taking
`__init__(self, config=None, bus=None)` and passing its own identity up, as above, so that
callers do not have to know the name.

!!! warning "Loaders do not agree on how to construct a toolbox — accept all three arguments"
    The three loaders in the org each call this differently, and none of them matches the
    others:

    | Loader | Call |
    |---|---|
    | `ovos-persona-server` | `cls(toolbox_id=name)` |
    | `ovos-PHAL-plugin-tools` | `cls(config=..., bus=self.bus)` |
    | `ovos-agentic-loop` | `cls(config=..., bus=bus)` |

    The toolboxes shipped today (DuckDuckGo, Wikipedia, Wolfram Alpha, Wordnet) take
    `__init__(self, config=None)` and nothing else, so they raise `TypeError` under every one
    of those calls. Each loader catches it and logs a warning, so the toolbox is silently
    absent rather than failing loudly.

    Until that settles, take all three and give each a default:

    ```python
    def __init__(self, toolbox_id="my-toolbox", config=None, bus=None):
        super().__init__(toolbox_id=toolbox_id, config=config, bus=bus)
    ```

    A toolbox written this way loads under all three loaders. It also gets the per-instance id
    that an adapter fronting several external servers (the MCP and UTCP adapters) needs to keep
    one bus topic per instance — those two set `toolbox_id` as a class attribute instead, so
    they cannot currently run as more than one instance.

`ToolBox.__init__` calls `discover_tools()` immediately to populate `self.tools`, and `bind(bus)`
registers the messagebus handlers described below. The full authoring guide with more
`AgentTool`, `ToolArguments`, and `ToolOutput` examples is embedded in the
[Plugin Manager reference](plugin-manager.md).

### Walkthrough: your own tool, wired in

This mirrors the [Personas](personas.md) 3-step pattern, applied to a tool instead of a
persona. A skeleton toolbox with one tool, a script call, and a persona entry are enough.

**1. Define the ToolBox.** One tool, `check_disk_space`, shells out to a home script:

```python
# my_ops_tools/toolbox.py
import subprocess
from typing import List
from ovos_plugin_manager.templates.agent_tools import ToolBox, AgentTool, ToolArguments, ToolOutput

class DiskSpaceArgs(ToolArguments):
    path: str = "/"

class DiskSpaceResult(ToolOutput):
    output: str

def check_disk_space(args: DiskSpaceArgs) -> DiskSpaceResult:
    result = subprocess.run(
        ["/home/user/scripts/disk_report.sh", args.path],
        capture_output=True, text=True, timeout=10
    )
    return DiskSpaceResult(output=result.stdout.strip())

class OpsToolBox(ToolBox):
    def __init__(self, config=None, bus=None):
        super().__init__(toolbox_id="my-ops-tools", config=config, bus=bus)

    def discover_tools(self) -> List[AgentTool]:
        return [
            AgentTool(
                name="check_disk_space",
                description="Report free disk space for a given path by running a local script.",
                argument_schema=DiskSpaceArgs,
                output_schema=DiskSpaceResult,
                tool_call=check_disk_space,
            )
        ]
```

**2. Register the entry point:**

```toml
# pyproject.toml
[project.entry-points."opm.agents.toolbox"]
my-ops-tools = "my_ops_tools.toolbox:OpsToolBox"
```

**3. Wire it into a persona** alongside an LLM handler that can call it:

```json
{
  "name": "OpsAssistant",
  "handlers": ["ovos-react-loop"],
  "ovos-react-loop": {
    "brain": "ovos-chat-openai-plugin",
    "ovos-chat-openai-plugin": {
      "api_url": "http://localhost:11434/v1"
    },
    "toolboxes": ["my-ops-tools"]
  }
}
```

The persona names the loop as its handler, the loop's `brain` does the reasoning, and
`toolboxes` lists the entry-point name from step 2 so the loop loads `OpsToolBox` and
offers `check_disk_space` to the brain.

---

### Static vs instance members

| Member | Kind | Why |
|---|---|---|
| `tool_json_list` | `@property` | Reads `self.tools`, so it needs the instance's discovered tools. |
| `openai_tools` | `@property` | Calls `self.tools_to_openai_spec(self.tool_json_list)` on this instance's own tools. |
| `tools_to_openai_spec` | `@staticmethod` | Converts a plain `tool_json_list`-shaped list to the OpenAI tools spec. It takes no `self`, so a caller can hand it a list merged from **several** toolboxes at once, not just one instance's tools. |
| `normalize_tools` | `@staticmethod` | Coerces a `ToolBox`, an OpenAI tool dict, or a list mixing either, into one flat OpenAI tools list. It has to work before an instance is chosen, since one of its inputs is a whole list of toolboxes. |
| `validate_input` / `validate_output` | `@staticmethod` | Validate a given `AgentTool`'s schema against raw arguments/results; the tool being validated is passed in, so no instance state is needed. |

`ovos-agentic-loop`'s `NativeToolCallEngine` is the concrete case that needs `tools_to_openai_spec`
to be static: it merges `tool_json_list` output from several toolboxes into one list before
converting the merged list to the OpenAI spec in a single call.

---

## PHAL Bus Provider

[OpenVoiceOS/ovos-PHAL-plugin-tools](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-tools) is a PHAL plugin that loads all installed `ToolBox` plugins and registers them on the messagebus. Any component that can emit bus messages can then use them.

```bash
pip install ovos-PHAL-plugin-tools
```

Entry point group: `opm.phal`; plugin name `ovos-phal-plugin-tools`.

### messagebus event table

| Message type | Direction | Payload |
|---|---|---|
| `ovos.tools.list` | → plugin | *(none)* |
| `ovos.tools.list.response` | plugin → | `{tools: [{name, description, argument_schema, output_schema, toolbox_id}]}` |
| `ovos.tools.get` | → plugin | `{name: str}` |
| `ovos.tools.get.response` | plugin → | Full schema dict or `{error: str}` |
| `ovos.tools.invoke` | → plugin | `{name: str, args: dict}` |
| `ovos.tools.invoke.response` | plugin → | `{name, result: dict}` or `{name, error: str}` |
| `ovos.tools.reload` | → plugin | *(none)* |
| `ovos.tools.reload.response` | plugin → | `{loaded: [str, ...], total_tools: int}` |

Every request gets an answer. Unknown tools, bad arguments, and tool exceptions
come back as an `error` field. The plugin never stays silent.

### Third-party usage

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()

tools = bus.wait_for_response(Message("ovos.tools.list"))
schema = bus.wait_for_response(Message("ovos.tools.get", {"name": "add"}))
result = bus.wait_for_response(Message("ovos.tools.invoke",
                                       {"name": "add", "args": {"a": 1, "b": 2}}))
```

---

## ovos-agentic-loop Toolboxes

The built-in toolboxes are listed on [Agentic Loops](agentic-loop.md#built-in-toolboxes).

Wire them into a persona:

```json
{
  "name": "researcher",
  "handlers": ["ovos-react-loop"],
  "ovos-react-loop": {
    "brain": "ovos-chat-openai-plugin",
    "toolboxes": ["ovos-math-tools", "ovos-web-search-tools"]
  }
}
```

---

## Exposing Tools over MCP / UTCP

The Persona Server can bridge any installed ToolBox plugin to MCP and UTCP clients. See [agent-interop.md#persona-server-tool-plugins-via-mcp-utcp](agent-interop.md#persona-server-tool-plugins-via-mcp-utcp).

### Function calling: client-side vs server-side tools

The [Persona Server](persona-server.md#function-calling-who-executes-what) can offer a model two
different kinds of tools in the same request, and only one of them is a `ToolBox`:

- **Client-side tools** are whatever the API caller put in the request's `tools` field. The
  caller executes them itself; the server only relays the model's `tool_calls`.
- **Server-side tools** are the persona's own `ToolBox` plugins (documented on this page). The
  server executes these in a bounded agentic loop and the client never sees the call.

If a client tool shares a name with one of the persona's `ToolBox` tools, the persona's tool
wins — the duplicate is dropped before the model ever sees it. Give tools specific names
(`search_local_docs`, not `search`) to avoid the collision.

### Consuming an external MCP or UTCP server as a ToolBox

`ovos-tool-adapters` ships two `opm.agents.toolbox` plugins that bridge an *external* tool server
into the `ToolBox` interface, so a persona can call it like any native toolbox:

| Plugin ID | Package | Bridges |
|---|---|---|
| `ovos-mcp-toolbox` | `ovos-tool-adapters` | An MCP server, over the `stdio`, `sse`, or `http` transport |
| `ovos-utcp-toolbox` | `ovos-tool-adapters` | A UTCP-manual-advertising HTTP server |

```bash
pip install ovos-tool-adapters
```

Each takes its own config section, keyed by plugin name in the persona JSON exactly like a
handler plugin. For `ovos-mcp-toolbox`, `transport` selects the connection kind: `stdio` needs
`command` (and `args`), `sse` and `http` need a `url`:

```json
{
  "name": "researcher",
  "handlers": ["ovos-react-loop"],
  "ovos-react-loop": {
    "brain": "ovos-chat-openai-plugin",
    "toolboxes": ["ovos-mcp-toolbox"]
  },
  "ovos-mcp-toolbox": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  }
}
```

!!! warning "A ToolBox that fails to connect serves zero tools, silently"
    If the bridged server cannot be reached, or its config is wrong, the failure surfaces during
    plugin discovery as a logged warning, not an error the caller sees. The persona keeps
    running and answers normally — it just offers no tools at all. If a persona that should have
    tools behaves as if it has none, check the server log for a `ToolBox` warning before assuming
    the model is refusing to call anything.

---

## Available ToolBoxes

These `opm.agents.toolbox` plugins each wrap one external service as a set of callable
`AgentTool` functions. Call them directly with `ToolBox.call_tool(name, kwargs)`, or over the
bus via `ovos.persona.tools.{toolbox_id}.call`.

| Plugin ID | Tools | Package | API key |
|---|---|---|---|
| `ovos-wikipedia-tool` | `search_wikipedia`, `get_wikipedia_sections`, `get_wikipedia_page` | `ovos-wikipedia-plugin` | None, public Wikipedia REST API |
| `ovos-ddg-tools` | `search_duckduckgo`, `get_duckduckgo_infobox` | `ovos-ddg-plugin` | None, DuckDuckGo Instant Answer API |
| `ovos-wolfram-alpha-tools` | `compute`, `compute_full` | `ovos-wolfram-alpha-plugin` | Optional, free key at developer.wolframalpha.com; a demo key ships in the plugin |
| `ovos-wordnet-tool` | `lookup_word`, `define_word` | `ovos-wordnet-plugin` | None, local NLTK corpus |

Note the two singular `-tool` IDs. They are the entry-point names the plugins actually
register, not typos.

Skills are a natural place for more of these — weather, date and time, the ISS tracker — but
none of those skills registers an `opm.agents.toolbox` entry point yet. Only the four above
exist in the OVOS org.

The [agentic loop](agentic-loop.md) bundles its own toolboxes (`ovos-filesystem-tools`,
`ovos-shell-tools`, `ovos-web-search-tools`, `ovos-clock-tools`, `ovos-skill-md-toolbox`).
See that page for those.

## Available Chat Engines

`opm.agents.chat` plugins beyond the ones documented in the [Agent Plugins catalog](agent-plugins.md#plugin-catalog)
(`ovos-openai-plugin`, `ovos-gguf-plugin`) are not currently shipped by an OpenVoiceOS-org
repository. This manual only documents plugins backed by an OpenVoiceOS-org repo.

## Testing Tool Calling Without a GPU

Reviewing tool-calling code needs a model that reliably *emits* tool calls, not necessarily a
smart one. A small CPU-only model under [llama.cpp](https://github.com/ggml-org/llama.cpp)'s
own OpenAI-compatible server is enough to exercise the whole path — server discovers tools,
model requests one, caller or server executes it — without a GPU:

```bash
llama-server -m Qwen3-0.6B-Q4_K_M.gguf --jinja -c 8192
```

Qwen3-0.6B at Q4_K_M quantization is a roughly 380 MB download. The `--jinja` flag is not
optional: without it, `llama.cpp` skips the chat template that actually produces `tool_calls`,
and every tool-calling test silently degrades into an ordinary plain-text conversation instead
of failing loudly.

Point a persona at the running server with the OpenAI-compatible chat engine:

```json
{
  "name": "tool-test",
  "handlers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "http://localhost:8080/v1"
  }
}
```

!!! warning "Entry-point name vs. package name"
    The entry point is **`ovos-chat-openai-plugin`**, not the package name
    (`ovos-openai-plugin`, `pip install ovos-openai-plugin`). Writing the package name into
    `handlers` instead of the entry-point name raises `ImportError: 'ovos-openai-plugin' not
    installed` — which reads like the package genuinely isn't installed, when the actual problem
    is the wrong key.

---
**Read next:** [Interoperability (MCP/UTCP/A2A)](agent-interop.md)
**Related:** [Agentic Loop Architectures](agentic-loop.md) · [Agent Engine Types](agent-plugins.md)
