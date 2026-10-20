# Answer Through a Remote A2A Agent (A2A Solver)

The A2A solver makes an OVOS persona hand each question to an agent on another server, over the A2A protocol. Use the A2A solver when OVOS must use an agent that speaks A2A as the brain of a persona, for example an agent built with LangGraph, CrewAI or Google ADK. A voice question then gets the answer of the remote agent.

## What you get

The persona handler `ovos-a2a-solver` from the `ovos-a2a-solver-plugin` package. It sends each user message to the remote agent and returns the reply as the answer of the persona.

## Steps

1. Install the plugin:

    ```bash
    pip install --pre ovos-a2a-solver-plugin
    ```

2. Write the persona file. `agent_url` is the base URL of the remote agent:

    ```json
    {
      "name": "remote-helper",
      "handlers": ["ovos-a2a-solver"],
      "ovos-a2a-solver": {
        "agent_url": "https://my-a2a-agent.example.com",
        "auth_header": "Bearer <token>",
        "timeout": 60,
        "streaming": false
      }
    }
    ```

| Key | Default | Description |
|---|---|---|
| `agent_url` | none | Base URL of the A2A agent. Required. |
| `auth_header` | none | The value of the `Authorization` header, for example `Bearer <token>`. |
| `timeout` | `60` | Seconds for each call. |
| `streaming` | `false` | Use the streaming call of the agent. |

## Which agents it can reach

The plugin uses the `a2a-sdk` client. It reads the agent card from `/.well-known/agent-card.json` under `agent_url`, and it uses the transport that the card names. It speaks A2A 1.0 and A2A 0.3. An agent that publishes only `/.well-known/agent.json`, the path of A2A 0.2, is not supported.

The OVOS persona server from [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md) is a valid remote agent. Set `agent_url` to the value of its `--a2a-base-url` flag, for example `http://localhost:8337/a2a`. A persona that sent "what is the speed of light?" to a persona server with a RiveScript persona gave this answer:

```text
Are such questions much on your mind?
```

The plugin sends only the newest user message. The remote agent keeps the conversation for each OVOS session.

## If it fails

The persona speaks one line of its error dialog when the remote agent cannot answer. The log line that starts with `A2AChatEngine: task failed` gives the cause.

| What you see in the log | Cause | What to do |
|---|---|---|
| `Network communication error fetching agent card` | The agent is not running, or `agent_url` is wrong | Make sure that `<agent_url>/.well-known/agent-card.json` answers. |
| `Client Request timed out` | The agent took longer than `timeout` | Increase `timeout`. |
| `A2A task ended in TASK_STATE_FAILED` | The agent failed the task | Read the log of the agent. |

## More information

- [Configuration](https://github.com/OpenVoiceOS/ovos-a2a-agent-plugin#configuration) in the `ovos-a2a-agent-plugin` README.
- [Personas](personas.md) for persona files and handlers.
- The [A2A specification](https://a2a-protocol.org/).

---
**Read next:** [Connect a HiveMind satellite to an A2A agent](ai-agent-hivemind-a2a.md)
**Related:** [AI Agents](ai-agents.md) · [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md) · [Personas](personas.md)
