# Run Several Personas on One Server

--8<-- "snippets/alpha-only.md"

This page serves several personas from one `ovos-persona-server` process, with a separate memory for each user. You want to reach your personas over HTTP, from apps that speak the OpenAI or Ollama API.

## What the setup includes

- The `model` field of each request selects the persona.
- With `CHAT_MEMORY=transparent`, the `user` field selects the memory of one person.
- Each persona keeps its own memory, so a user has a separate history with each persona.

## Steps

--8<-- "snippets/community-servers.md"

1. Install the packages:

    ```bash
    pip install --pre ovos-persona-server ovos-openai-plugin
    ```

2. Save two personas, `~/personas/ada.json` and `~/personas/bo.json`. This is `ada.json`:

    ```json
    {
      "name": "ada",
      "handlers": ["ovos-chat-openai-plugin"],
      "ovos-chat-openai-plugin": {
        "api_url": "https://llama.smartgic.io/v1",
        "key": "sk-none",
        "model": "qwen2.5:7b",
        "system_prompt": "Your name is Ada. You answer in at most fifteen words. When asked your name, say Ada."
      }
    }
    ```

    For `bo.json`, change the name to `bo` and change the system prompt to the name Bo.

3. Start the server. It loads every `*.json` file in the directory:

    ```bash
    CHAT_MEMORY=transparent ovos-persona-server --personas-dir ~/personas
    ```

4. List the personas:

    ```bash
    curl -s localhost:8337/openai/v1/models | python3 -c 'import sys,json; print([m["id"] for m in json.load(sys.stdin)["data"]])'
    ```

5. Send requests to both personas for one user:

    ```bash
    ask() {
      curl -s localhost:8337/openai/v1/chat/completions \
        -H 'content-type: application/json' \
        -d "{\"model\":\"$1\",\"user\":\"$2\",\"messages\":[{\"role\":\"user\",\"content\":\"$3\"}]}" |
        python3 -c 'import sys,json; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
    }
    ask ada alice "What is your name? Answer with your name only."
    ask bo alice "What is your name? Answer with your name only."
    ask ada alice "Remember this: my cat is called Pixel. Reply only with OK."
    ask ada alice "What is my cat called? Answer with the name only."
    ask bo alice "What is my cat called? If you do not know, say UNKNOWN."
    ```

Output of a run:

```text
['ada', 'bo']
Ada.
Bo.
OK.
Pixel.
UNKNOWN.
```

`bo` does not see what Alice told `ada`. An unknown `model` value gets HTTP 404 with the list of available personas.

The server trusts the `user` value and does not check it, so this setup fits trusted clients only. On a server that untrusted clients share, keep `CHAT_MEMORY` off. See [Memory, RAG & embeddings](persona-server.md#memory-rag-embeddings).

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| The server does not start | Two persona files have the same name | Give each persona a unique `name` |
| All users share one history | The client sends no `user` field | Send a different `user` value for each person |
| The server forgets between requests | `CHAT_MEMORY` is not `transparent` | Start the server with `CHAT_MEMORY=transparent` |

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Persona Server](persona-server.md)
- [Give each person their own memory](persona-family-memory.md)
