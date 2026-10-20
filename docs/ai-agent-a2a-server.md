# Talk to an OVOS Persona over A2A

Publish an OVOS persona as an A2A agent, so that other agents can send it questions and get its answers. Use the A2A server when agents from other frameworks must use an OVOS persona. The other agent speaks the Agent-to-Agent (A2A) protocol, for example a LangGraph, CrewAI or Google ADK agent, or a client built on `a2a-sdk`.

## What you get

- An agent card at `http://localhost:8337/a2a/.well-known/agent-card.json`. The card names the persona, its skills, and the URL for questions.
- A JSON-RPC endpoint at `http://localhost:8337/a2a/` that accepts A2A 1.0 `SendMessage` and `SendStreamingMessage`. It also accepts the A2A 0.3 names `message/send` and `message/stream`.

## Start the server

!!! warning "Alpha channel only"
    The `a2a` extra is only in the prerelease channel. Install the server
    from that channel:

    ```bash
    pip install --pre "ovos-persona-server[a2a]" ovos-solver-rivescript-plugin
    ```

1. Write the persona file `helper.json`. This persona answers from RiveScript rules, so it needs no language model:

    ```json
    {
      "name": "helper",
      "description": "A small OVOS persona that answers from RiveScript rules",
      "handlers": ["ovos-solver-rivescript-plugin"]
    }
    ```

2. Start the server with `--a2a-base-url`. The URL goes into the agent card, so use the address that other agents can reach:

    ```bash
    ovos-persona-server --persona helper.json --a2a-base-url http://localhost:8337/a2a
    ```

3. Read the agent card:

    ```bash
    curl -s http://localhost:8337/a2a/.well-known/agent-card.json
    ```

    The card names the persona and two interfaces at the same URL, one for A2A 1.0 and one for A2A 0.3. The start of the card:

    ```text
    {"name":"helper","description":"A small OVOS persona that answers from RiveScript rules","supportedInterfaces":[{"url":"http://localhost:8337/a2a/","protocolBinding":"JSONRPC","protocolVersion":"1.0"},{"url":"http://localhost:8337/a2a/","protocolBinding":"JSONRPC","protocolVersion":"0.3"}],"version":"1.0","capabilities":{"streaming":true}, ...
    ```

## Ask the persona a question

This script uses the `a2a-sdk` client (`pip install "a2a-sdk[http-server]>=1.2.3"`). The client reads the agent card and sends the question to the URL in the card:

```python
import asyncio
import httpx
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.helpers.proto_helpers import get_artifact_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

async def main():
    async with httpx.AsyncClient(timeout=30) as http:
        client = await ClientFactory(ClientConfig(httpx_client=http, streaming=False)).create_from_url(
            "http://localhost:8337/a2a")
        request = SendMessageRequest(message=new_text_message("hello", role=Role.ROLE_USER))
        async for event in client.send_message(request):
            task = event.task
            print(TaskState.Name(task.status.state), [get_artifact_text(a) for a in task.artifacts])

asyncio.run(main())
```

```text
TASK_STATE_COMPLETED ['Hi. :)']
```

The RiveScript rules choose from several replies, so the text can be different.

## Serve several personas

Give `--persona` once for each persona. Each persona gets its own agent card at `/a2a/<persona name>/.well-known/agent-card.json`. The card at `/a2a/` belongs to the default persona.

## If it fails

| What you see | Cause | What to do |
|---|---|---|
| `/a2a/...` returns `404` | The server started without `--a2a-base-url`, or `a2a-sdk` is not installed | Install the `a2a` extra. Start the server with `--a2a-base-url`. |
| The client gets `-32601 Method not found` | The client sends a method name from an A2A draft, such as `tasks/send` | Use a client that sends `SendMessage`, or the A2A 0.3 name `message/send`. |
| A remote client cannot connect to the URL in the card | `--a2a-base-url` names an address that only the server can reach | Give the public address of the server, or the address of its reverse proxy. |

!!! danger "No authentication"
    The A2A endpoint answers every request. Bind the server to a trusted network, or put a reverse proxy with authentication in front of it.

## More information

- [A2A endpoint](https://github.com/OpenVoiceOS/ovos-persona-server#a2a-endpoint) in the `ovos-persona-server` README, and its [A2A page](https://github.com/OpenVoiceOS/ovos-persona-server/blob/dev/docs/a2a.md).
- [Persona Server](persona-server.md) for the other chat APIs of the server.
- The [A2A specification](https://a2a-protocol.org/).

---
**Read next:** [Write a tool plugin](ai-agent-tool-plugin.md)
**Related:** [AI Agents](ai-agents.md) · [Answer through a remote A2A agent](ai-agent-a2a-solver.md) · [Connect a HiveMind satellite to an A2A agent](ai-agent-hivemind-a2a.md)
