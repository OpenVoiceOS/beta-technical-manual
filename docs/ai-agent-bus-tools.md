# Share Tools on the OVOS Messagebus (PHAL Tools Plugin)

The PHAL tools plugin shares every installed tool plugin on the OVOS messagebus, so that skills, services and other programs on the device can list and call the tools. Use the PHAL tools plugin when a skill, a GUI or a script on the messagebus of an OVOS device must use tool plugins, with no HTTP server and no MCP client.

## What you get

`ovos-PHAL-plugin-tools` loads every installed toolbox and answers four messages:

| Message | Data | Answer |
|---|---|---|
| `ovos.tools.list` | none | `{"tools": [{name, description, argument_schema, output_schema, toolbox_id}]}` |
| `ovos.tools.get` | `{"name": str}` | The schema of one tool, or `{"error": str}` |
| `ovos.tools.invoke` | `{"name": str, "args": dict}` | `{"name", "result": dict}` or `{"name", "error": str}` |
| `ovos.tools.reload` | none | `{"loaded": [str], "total_tools": int}` |

Each request gets an answer. An unknown tool, bad arguments, or an error in the tool come back in the `error` field.

## Steps

1. Install the plugin and your tool plugins in the environment of the PHAL service:

    ```bash
    pip install --pre ovos-PHAL-plugin-tools
    pip install -e ./my-math-tools
    ```

2. Restart the PHAL service. The service log shows the toolboxes that the plugin found:

    ```text
    [ovos-phal-plugin-tools] found 1 toolbox plugin(s): ['my-math-tools']
    PHAL plugin loaded: ovos-phal-plugin-tools
    ```

3. From any program that can connect to the messagebus, list, describe and call the tools:

    ```python
    from ovos_bus_client import MessageBusClient
    from ovos_bus_client.message import Message

    bus = MessageBusClient()
    bus.run_in_thread()
    bus.connected_event.wait(10)

    tools = bus.wait_for_response(Message("ovos.tools.list"))
    print(sorted(t["name"] for t in tools.data["tools"]))
    result = bus.wait_for_response(Message("ovos.tools.invoke", {"name": "add", "args": {"a": 2, "b": 3}}))
    print(result.data)
    bad = bus.wait_for_response(Message("ovos.tools.invoke", {"name": "nope", "args": {}}))
    print(bad.data)
    bus.close()
    ```

    ```text
    ['add']
    {'name': 'add', 'result': {'sum': 5.0}}
    {'name': 'nope', 'error': "Unknown tool: 'nope'"}
    ```

    The list holds the tools of every toolbox in the environment of the PHAL service. Here, only `my-math-tools` is installed.

## Call one toolbox directly

Each toolbox that the plugin loads also answers on its own topic, `ovos.persona.tools.<toolbox_id>.call`, with the data `{"name", "kwargs"}`:

```python
from ovos_bus_client import MessageBusClient
from ovos_bus_client.message import Message

bus = MessageBusClient()
bus.run_in_thread()
bus.connected_event.wait(10)

reply = bus.wait_for_response(Message("ovos.persona.tools.my-math-tools.call",
                                      {"name": "add", "kwargs": {"a": 2, "b": 3}}))
print(reply.data)
bus.close()
```

```text
{'result': {'sum': 5.0}, 'toolbox_id': 'my-math-tools'}
```

A toolbox answers only on its own topic. A call on the shared topic `ovos.persona.tools.call` gets no answer.

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `wait_for_response` returns `None` | The PHAL service did not load the plugin, or the request went to a topic that nobody answers | Read the PHAL log for `PHAL plugin loaded: ovos-phal-plugin-tools`. Use the topics in the table above. |
| A tool is not in `ovos.tools.list` | The tool plugin is in a different environment | Install it in the environment of the PHAL service. Send `ovos.tools.reload`, or restart the service. |
| The program waits and never stops | The messagebus was not reachable when `run_in_thread()` started | Start the messagebus service first. |

## More information

- [Bus API reference](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-tools#bus-api-reference) in the `ovos-PHAL-plugin-tools` README.
- [Agent Tool Plugins](tool-plugins.md#phal-bus-provider) for the place of the plugin among the other tool components.

---
**Read next:** [Give a persona MCP and UTCP tools](ai-agent-persona-uses-tools.md)
**Related:** [AI Agents](ai-agents.md) · [Write a tool plugin](ai-agent-tool-plugin.md) · [Use persona tools over MCP and UTCP](ai-agent-persona-tools.md)
