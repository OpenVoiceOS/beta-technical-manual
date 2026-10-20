# Answer Through a Remote A2A Agent (A2A Solver)

This page makes an OVOS persona hand each question to an agent on another server, over the A2A protocol.

## Who this is for

You have an agent that speaks A2A, for example one built with LangGraph, CrewAI or Google ADK. You want OVOS to use that agent as the brain of a persona. A voice question then gets the answer of the remote agent.

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

The released plugin, `ovos-a2a-solver-plugin` 0.0.2a3, uses an early draft of A2A:

- It reads the agent card from `/.well-known/agent.json`.
- It sends the JSON-RPC method `tasks/send`, or `tasks/sendSubscribe` for streaming.
- It posts to `agent_url` without a slash at the end.

An agent that is built on `a2a-sdk` 1.x does not accept `tasks/send`. This includes the OVOS persona server from [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md). With the persona server as the remote agent, the persona gives no answer, and the log shows:

```text
A2AChatEngine: task failed: Redirect response '307 Temporary Redirect' for url 'http://localhost:8337/a2a'
```

The same endpoint answers `tasks/send` with:

```json
{"error":{"code":-32601,"message":"Method not found"},"id":1,"jsonrpc":"2.0"}
```

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `produced no answer: no handler in its chain returned a response` | The remote agent rejected the call | Read the log line that starts with `A2AChatEngine: task failed`. |
| `-32601 Method not found` | The agent does not accept `tasks/send` | Use an agent that accepts the early A2A method names. |
| `307 Temporary Redirect` | The agent serves its endpoint at a URL that ends with `/` | Use an agent that accepts the URL without the slash. |

## More information

- [Configuration](https://github.com/OpenVoiceOS/ovos-a2a-agent-plugin#configuration) in the `ovos-a2a-agent-plugin` README.
- [Personas](personas.md) for persona files and handlers.
- The [A2A specification](https://a2a-protocol.org/).

---
**Read next:** [Connect a HiveMind satellite to an A2A agent](ai-agent-hivemind-a2a.md)
**Related:** [AI Agents](ai-agents.md) · [Talk to an OVOS persona over A2A](ai-agent-a2a-server.md) · [Personas](personas.md)
