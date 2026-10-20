# Write a Tool Plugin (OPM ToolBox)

Write a tool plugin: a Python package that gives AI agents a typed tool, which every OVOS agent component can find and call. Use a tool plugin when an AI agent must do a task of your own in Python, such as read a sensor or call a service. You write the tool one time, and three OVOS components use it. The persona server serves it over MCP and UTCP. The PHAL plugin shares it on the messagebus. The agentic loop gives it to a language model.

## What you get

A package with one `ToolBox` class. The class declares its tools with Pydantic models for the arguments and the result. OVOS turns those models into JSON Schema for the agent.

## Steps

1. Make this folder layout:

    ```text
    my-math-tools/
    ├── pyproject.toml
    └── my_math_tools/
        └── __init__.py
    ```

2. Write `my-math-tools/pyproject.toml`. The entry point in the `opm.agents.toolbox` group makes the plugin visible to OVOS:

    ```toml
    [build-system]
    requires = ["setuptools>=61"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "my-math-tools"
    version = "0.1.0"
    dependencies = ["ovos-plugin-manager"]

    [project.entry-points."opm.agents.toolbox"]
    my-math-tools = "my_math_tools:MathToolBox"
    ```

3. Write `my-math-tools/my_math_tools/__init__.py`:

    ```python
    from typing import List

    from ovos_plugin_manager.templates.agent_tools import AgentTool, ToolArguments, ToolBox, ToolOutput


    class AddArgs(ToolArguments):
        a: float
        b: float


    class AddResult(ToolOutput):
        sum: float


    def add(args: AddArgs) -> AddResult:
        return AddResult(sum=args.a + args.b)


    class MathToolBox(ToolBox):
        def __init__(self, config=None, bus=None):
            super().__init__(toolbox_id="my-math-tools", config=config, bus=bus)

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

    The `toolbox_id` must be the same as the entry-point name.

4. Install the package in the environment of the OVOS component that must use it:

    ```bash
    pip install -e ./my-math-tools
    ```

5. Find the plugin and call the tool:

    ```python
    from ovos_plugin_manager.persona import find_toolbox_plugins

    toolbox = find_toolbox_plugins()["my-math-tools"]()
    print(list(toolbox.tools))
    print(toolbox.call_tool("add", {"a": 2, "b": 3}))
    print(toolbox.openai_tools)
    ```

    ```text
    ['add']
    sum=5.0
    [{'type': 'function', 'function': {'name': 'add', 'description': 'Add two numbers together.', 'parameters': {'properties': {'a': {'title': 'A', 'type': 'number'}, 'b': {'title': 'B', 'type': 'number'}}, 'required': ['a', 'b'], 'title': 'AddArgs', 'type': 'object'}}}]
    ```

`call_tool` checks the arguments against `AddArgs` and the result against `AddResult`. `openai_tools` is the tool list in the function-calling format of OpenAI-compatible models.

## Where the tool shows up

| Component | How the tool appears | Task |
|---|---|---|
| `ovos-persona-server` | An MCP tool `add` and a UTCP tool `add` | [Use persona tools over MCP and UTCP](ai-agent-persona-tools.md) |
| `ovos-PHAL-plugin-tools` | `ovos.tools.invoke` with `{"name": "add"}` on the messagebus | [Share tools on the messagebus](ai-agent-bus-tools.md) |
| `ovos-agentic-loop` | A tool that the language model can call, when the persona lists `my-math-tools` in `toolboxes` | [Give a persona MCP and UTCP tools](ai-agent-persona-uses-tools.md) |

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `KeyError: 'my-math-tools'` from `find_toolbox_plugins()` | The package is not installed in this environment, or the entry-point group is wrong | Install the package in the same environment. Use the group `opm.agents.toolbox`. |
| `call_tool` raises `ValueError: Tool input validation failed` | The arguments do not match `AddArgs` | Send the fields and types that the argument model declares. |
| A component loads the plugin but shows no tools | `discover_tools()` raised an error | Read the log of the component for the error of the plugin. |

## More information

- [Agents](https://github.com/OpenVoiceOS/ovos-plugin-manager/blob/dev/docs/agents.md) in the `ovos-plugin-manager` docs.
- [Agent Tool Plugins](tool-plugins.md) for the full `ToolBox` contract and the list of toolboxes.

---
**Read next:** [Use persona tools over MCP and UTCP](ai-agent-persona-tools.md)
**Related:** [AI Agents](ai-agents.md) · [Share tools on the messagebus](ai-agent-bus-tools.md) · [Agent Tool Plugins](tool-plugins.md)
