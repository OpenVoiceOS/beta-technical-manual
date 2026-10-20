# Connect a HiveMind Satellite to an A2A Agent

This page makes a HiveMind master send the questions of its clients to an A2A agent, in place of an OVOS brain.

## Who this is for

You run a HiveMind master. You want the questions of its clients to go to an agent that speaks A2A. The answers come back to the client that asked.

## What you get

The HiveMind agent protocol `hivemind-a2a-agent-plugin`. The HiveMind master loads it in place of the OVOS agent protocol. The plugin answers each `QUERY` and `CASCADE` message: it sends the question to the A2A agent and sends the reply back as `speak` messages.

!!! warning "The plugin answers `QUERY` and `CASCADE` messages"
    A voice satellite and `hivemind-client terminal` send `BUS` messages. The plugin does not answer them. A client must send the question in a `QUERY` or `CASCADE` message.

## Steps

1. Install the plugin next to `hivemind-core`:

    ```bash
    pip install --pre hivemind-a2a-agent-plugin
    ```

2. Set the agent protocol in `~/.config/hivemind-core/server.json`. `agent_protocol.module` names the plugin. The key with the plugin name holds its settings:

    ```json
    {
      "agent_protocol": {
        "module": "hivemind-a2a-agent-plugin",
        "hivemind-a2a-agent-plugin": {
          "agent_url": "http://localhost:8337/a2a",
          "auth_header": "Bearer secret",
          "timeout": 60,
          "streaming": false
        }
      }
    }
    ```

3. Restart `hivemind-core`. The log names the plugin:

    ```text
    INFO - Agent protocol: A2AAgentProtocol
    ```

The keys have the same meaning as for the [A2A solver](ai-agent-a2a-solver.md#steps). With `streaming` set to `true`, each chunk from the agent becomes one `speak` message.

## Which agents it can reach

The plugin uses the `a2a-sdk` client, the same as the [A2A solver](ai-agent-a2a-solver.md#which-agents-it-can-reach). It speaks A2A 1.0 and A2A 0.3, so the OVOS persona server is a valid agent. `hivemind-core` passes no session id, so each query starts its own A2A conversation.

## If it fails

When the agent cannot answer, the plugin sends an error sentence to the client, and then the end of the query.

| What you see | Cause | What to do |
|---|---|---|
| A voice satellite gets no answer | The satellite sends a `BUS` message, and the plugin answers `QUERY` and `CASCADE` messages | Send the question in a `QUERY` or `CASCADE` message. |
| `Error validating A2A agent ... (HTTP 404)` | `agent_url` is wrong, or the agent publishes only the A2A 0.2 card path | Make sure that `<agent_url>/.well-known/agent-card.json` answers. |
| `Error contacting A2A agent: Client Request timed out` | The agent took longer than `timeout` | Increase `timeout`. |
| `A2A agent not configured` | `agent_url` is not set | Set `agent_url`. |

## More information

- [Configuration](https://github.com/JarbasHiveMind/hivemind-a2a-agent-plugin#configuration) in the `hivemind-a2a-agent-plugin` README.
- [HiveMind Agents](hivemind-agents.md) for how HiveMind relates to OVOS.
- The [A2A specification](https://a2a-protocol.org/).

---
**Read next:** [AI Agents](ai-agents.md)
**Related:** [Answer through a remote A2A agent](ai-agent-a2a-solver.md) · [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md) · [HiveMind Agents](hivemind-agents.md)
