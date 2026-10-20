# Give Each Person Their Own Memory

--8<-- "snippets/alpha-only.md"

This page sets up one assistant for several people, with a separate history and separate recalled facts for each person. Several people in a home or a team share one assistant.

## What the setup includes

- A separate history for each session. On `ovos-persona-server`, the OpenAI `user` field selects the session.
- Retrieval memories that recall only the caller's own exchanges, with `scope` set to `session`.

## Separate histories on the persona server

--8<-- "snippets/community-servers.md"

1. Install the packages:

    ```bash
    pip install --pre ovos-persona-server ovos-openai-plugin
    ```

2. Save a persona as `~/personas/ada.json`:

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

3. Start the server with server-side memory:

    ```bash
    CHAT_MEMORY=transparent ovos-persona-server --personas-dir ~/personas
    ```

4. Send requests for two users:

    ```bash
    ask() {
      curl -s localhost:8337/openai/v1/chat/completions \
        -H 'content-type: application/json' \
        -d "{\"model\":\"$1\",\"user\":\"$2\",\"messages\":[{\"role\":\"user\",\"content\":\"$3\"}]}" |
        python3 -c 'import sys,json; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
    }
    ask ada alice "Remember this: my cat is called Pixel. Reply only with OK."
    ask ada bob "Remember this: my favourite colour is green. Reply only with OK."
    ask ada alice "What is my cat called? Answer with the name only."
    ask ada bob "What is my cat called? If you do not know, say UNKNOWN."
    ```

Output of a run:

```text
OK
OK.
Pixel
UNKNOWN.
```

Alice gets her answer. Bob does not get Alice's answer. A request with no `user` field uses one shared default session, so send a `user` value for each person.

The server trusts the `user` value and does not check it, so this setup fits trusted clients only. On a server that untrusted clients share, keep `CHAT_MEMORY` off. See [Memory, RAG & embeddings](persona-server.md#memory-rag-embeddings).

## Keep recalled facts private

The `lexical` and `local-rag` memories store the exchanges of all sessions in one index. Their default `scope` is `global`, which recalls documents from every session. Set `scope` to `session` when several people share the assistant.

This script needs no chat server. It shows the difference between the two values:

```bash
pip install --pre ovos-memory-plugins
```

```python
from ovos_plugin_manager.templates.agents import AgentMessage, MessageRole
from ovos_memory_plugins.lexical import LexicalMemory

def remember(mem, user, said, answer):
    mem.update_history([AgentMessage(MessageRole.USER, said),
                        AgentMessage(MessageRole.ASSISTANT, answer)], user)

for scope in ("global", "session"):
    mem = LexicalMemory(config={"db_path": ":memory:", "scope": scope})
    remember(mem, "alice", "my door code is 4711", "noted, the door code is 4711")
    remember(mem, "bob", "what time is it", "it is noon")
    print(scope, "bob:", [h.content for h in mem.search("door code", session_id="bob")])
    print(scope, "alice:", [h.content for h in mem.search("door code", session_id="alice")])
    mem.close()
```

Output:

```text
global bob: ['Q: my door code is 4711\nA: noted, the door code is 4711']
global alice: ['Q: my door code is 4711\nA: noted, the door code is 4711']
session bob: []
session alice: ['Q: my door code is 4711\nA: noted, the door code is 4711']
```

With `global`, Bob's search finds Alice's door code. With `session`, it does not.

In a persona file, set the key in the memory block:

```json
{
  "memory_module": "ovos-memory-plugin-lexical",
  "ovos-memory-plugin-lexical": {"db_path": "~/.local/share/ovos/family.db", "scope": "session"}
}
```

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| One user hears another user's facts | A retrieval memory runs with `scope: global` | Set `scope` to `session` |
| All users share one history | The client sends no `user` field | Send a different `user` value for each person |
| The server forgets between requests | `CHAT_MEMORY` is not `transparent` | Start the server with `CHAT_MEMORY=transparent` |

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Make a persona remember](persona-remember.md)
- [Answer from your own documents](persona-local-documents.md)
