# Connect a HiveMind Satellite to an A2A Agent

This page makes a HiveMind master send the questions of its voice satellites to an A2A agent, in place of an OVOS brain.

## Who this is for

You run HiveMind voice satellites. You want their questions to go to an agent that speaks A2A. The answers come back to the satellite as speech.

## What you get

The HiveMind agent protocol `hivemind-a2a-agent-plugin`. The HiveMind master loads it in place of the OVOS agent protocol. The plugin sends each satellite query to the A2A agent and sends the reply back to the satellite that asked.

## Steps

1. Install the plugin next to `hivemind-core`. The plugin depends on `hivemind-bus-client` 1.2.11a1, which fails to import with `bitstring` 5. hivemind-a2a-agent-plugin 0.1.1a1 also needs `httpx` 0.x. Install `bitstring` 4 and `httpx` 0.x with it:

    ```bash
    pip install --pre hivemind-a2a-agent-plugin "bitstring<5" "httpx<1"
    ```

2. Set the agent protocol in the HiveMind configuration, usually `~/.config/hivemind/hivemind.conf`:

    ```json
    {
      "hivemind": {
        "agent_protocol": "hivemind-a2a-agent-plugin",
        "a2a_agent": {
          "agent_url": "http://localhost:9999",
          "auth_header": "Bearer secret",
          "timeout": 60,
          "streaming": false
        }
      }
    }
    ```

3. Restart `hivemind-core`.

The keys have the same meaning as for the [A2A solver](ai-agent-a2a-solver.md#steps).

## Which agents it can reach

The released plugin, `hivemind-a2a-agent-plugin` 0.1.1a1, uses the same early draft of A2A as the A2A solver. It sends `tasks/send` and `tasks/sendSubscribe` to `agent_url`. Agents that are built on `a2a-sdk` 1.x, the OVOS persona server among them, answer `-32601 Method not found`. A call from the plugin to the persona server stopped with:

```text
HTTPStatusError Redirect response '307 Temporary Redirect' for url 'http://localhost:8337/a2a'
```

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `ImportError: cannot import name 'BitStream' from 'bitstring'` | `bitstring` 5 is installed, and `hivemind-bus-client` 1.2.11a1 cannot import it | Install `bitstring<5`. |
| `TypeError: Client.__init__() got an unexpected keyword argument 'timeout'` | An `httpx` 1.0 prerelease is installed | Install `httpx<1`. |
| The satellite hears an error answer | The A2A agent rejected the call | Read the `hivemind-core` log. Make sure that the agent accepts `tasks/send`. |

## More information

- [Configuration](https://github.com/JarbasHiveMind/hivemind-a2a-agent-plugin#configuration) in the `hivemind-a2a-agent-plugin` README.
- [HiveMind Agents](hivemind-agents.md) for how HiveMind relates to OVOS.
- The [A2A specification](https://a2a-protocol.org/).

---
**Read next:** [AI Agents](ai-agents.md)
**Related:** [Answer through a remote A2A agent](ai-agent-a2a-solver.md) · [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md) · [HiveMind Agents](hivemind-agents.md)
