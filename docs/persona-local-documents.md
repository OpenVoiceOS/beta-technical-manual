# Answer From Your Own Documents

--8<-- "snippets/alpha-only.md"

This page makes a persona answer from your own notes or manuals. The index stays on your machine, and no vector database is necessary. You have documents, such as a household manual or opening hours, and you want the assistant to answer from them.

## What the setup includes

- The `lexical` memory indexes your documents in a local SQLite full-text index (BM25).
- For each question, the memory adds the matching passages to the prompt.

The chat model in this example is the public demo server `https://llama.smartgic.io/v1`. For a fully local setup, set `api_url` to an OpenAI-compatible chat server on your own machine.

--8<-- "snippets/community-servers.md"

## Steps

1. Install the packages:

    ```bash
    pip install --pre ovos-persona ovos-memory-plugins ovos-openai-plugin
    ```

2. Save a document as `bakery.md`:

    ```markdown
    # Pixel Bakery opening hours
    The Pixel Bakery on Rua Augusta opens at 07:15 and closes at 14:30 from Monday to Saturday.
    It is closed on Sundays. The house speciality is the cardamom bun.
    ```

3. Save this script as `index_docs.py`:

    ```python
    import sys
    from ovos_memory_plugins.lexical import LexicalMemory

    mem = LexicalMemory(config={"db_path": sys.argv[1]})
    for path in sys.argv[2:]:
        mem.store(open(path).read(), session_id="docs", metadata={"source": path})
    mem.close()
    print(f"indexed {len(sys.argv) - 2} document(s)")
    ```

4. Index the document:

    ```bash
    python index_docs.py ~/docs.db bakery.md
    ```

5. Save the persona as `~/personas/librarian.json`. Replace `/home/me` with your home directory:

    ```json
    {
      "name": "librarian",
      "handlers": ["ovos-chat-openai-plugin"],
      "ovos-chat-openai-plugin": {
        "api_url": "https://llama.smartgic.io/v1",
        "key": "sk-none",
        "model": "qwen2.5:7b",
        "allow_system_prompts": true,
        "system_prompt": "Answer in at most twenty words."
      },
      "memory_module": "ovos-memory-plugin-lexical",
      "ovos-memory-plugin-lexical": {
        "db_path": "/home/me/docs.db",
        "retrieval": {"max_num_results": 3}
      }
    }
    ```

6. Ask questions:

    ```python
    import os
    from ovos_bus_client.session import Session
    from ovos_persona import PersonaService
    from ovos_utils.fakebus import FakeBus

    svc = PersonaService(bus=FakeBus(), config={"personas_path": os.path.expanduser("~/personas")})
    for q in ("When does the Pixel Bakery close on Saturday?",
              "What is the house speciality at the Pixel Bakery?"):
        print("Q", q)
        print("A", "".join(svc.query(q, "librarian", Session("kitchen"))))
    ```

Output of a run:

```text
Q When does the Pixel Bakery close on Saturday?
A The Pixel Bakery closes at 14:30 on Saturdays.
Q What is the house speciality at the Pixel Bakery?
A The house specialty at the Pixel Bakery is the cardamom bun.
```

## Documents shared by several users

The `lexical` memory also stores every exchange in the same index. With one user, that is harmless. With several users, set `scope` to `session` for the conversation, and keep shared documents in a vector store on `ovos-persona-server`. The `ovos-openai-rag-memory-plugin` reads that store and writes nothing to it. See [Persona Server](persona-server.md).

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| The answer ignores the document, and the log says `dropped 1 system message(s)` | `allow_system_prompts` is off | Set `"allow_system_prompts": true` |
| No passage is found | BM25 matches words, not meaning | Use the words of the document. Or add `ovos-memory-plugin-local-rag` in a composite memory |
| One user sees another user's exchanges | `scope` is `global` | Set `scope` to `session`. The search then finds only documents stored under the id of the caller's session. A document stored under another id, such as `docs` in step 3, is hidden. Store it with the `session_id` of each user who needs it |

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Persona Memory](persona-memory.md)
- [Give each person their own memory](persona-family-memory.md)
