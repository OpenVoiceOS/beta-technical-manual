# Make a Persona Remember What You Said

--8<-- "snippets/alpha-only.md"

This page makes a persona use what you said earlier. It also makes the persona keep facts about you after a restart. You talk to an OVOS persona. You want it to remember your name, where you parked, or the name of your cat.

## What the setup includes

- The default short-term memory. It keeps the last messages of each session in RAM.
- The `entity` memory. It keeps facts about each user in a file, so the facts survive a restart.

--8<-- "snippets/community-servers.md"

The examples use the public demo server `https://llama.smartgic.io/v1`. Change `api_url` to your own OpenAI-compatible server.

## Remember what you said a few turns ago

1. Install the packages:

    ```bash
    pip install --pre ovos-persona ovos-openai-plugin
    ```

2. Save the persona as `personas/helper.json`:

    ```json
    {
      "name": "helper",
      "handlers": ["ovos-chat-openai-plugin"],
      "ovos-chat-openai-plugin": {
        "api_url": "https://llama.smartgic.io/v1",
        "key": "sk-none",
        "model": "qwen2.5:7b",
        "system_prompt": "You are a home assistant. Answer in at most fifteen words."
      },
      "memory_module": "ovos-agents-short-term-memory-plugin",
      "ovos-agents-short-term-memory-plugin": {"max_history": 7}
    }
    ```

    `max_history` counts messages, not exchanges. The question that the persona is answering takes one slot of the window. A value of `7` gives the model the last three exchanges and the new question. An even value, such as `6`, starts the history with an answer that has no question.

3. Save this script as `remember.py` and run it from the directory that holds `personas`. The script sends the two bus events that `ovos-core` sends around each answer. The persona records the history from these events.

    ```python
    from ovos_bus_client.message import Message
    from ovos_bus_client.session import Session
    from ovos_persona import PersonaService
    from ovos_utils.fakebus import FakeBus

    bus = FakeBus()
    svc = PersonaService(bus=bus, config={"personas_path": "personas"})


    def say(text, device):
        sess = Session(device)
        sess.persona_id = "helper"
        ctx = {"session": sess.serialize()}
        # ovos-core emits these two events around every answer; the persona records both
        bus.emit(Message("recognizer_loop:utterance", {"utterances": [text]}, ctx))
        answer = " ".join(svc.query(text, "helper", sess))
        bus.emit(Message("speak", {"utterance": answer}, ctx))
        print(f"{device}> {text}\n  {answer}")


    say("My name is Rita. I parked on level 3.", "living-room")
    say("Which level did I park on? Answer with the number only.", "living-room")
    say("Where did I park? If you do not know, say UNKNOWN.", "garage")
    for topic in ("the weather", "music", "cooking"):
        say(f"Tell me one fact about {topic}.", "living-room")
    say("Where did I park? If you do not know, say UNKNOWN.", "living-room")
    ```

Output of a run:

```text
living-room> My name is Rita. I parked on level 3.
  Hello Rita, your car is parked on Level 3, parking attendant will assist you soon.
living-room> Which level did I park on? Answer with the number only.
  3
garage> Where did I park? If you do not know, say UNKNOWN.
  UNKNOWN. Can you provide more context or details about your vehicle and location?
living-room> Tell me one fact about the weather.
  Today's forecast shows a high chance of scattered showers in your area.
living-room> Tell me one fact about music.
  The Beatles released their iconic album "Sgt. Pepper's Lonely Hearts Club Band" in 1967.
living-room> Tell me one fact about cooking.
  Boiling water is a crucial step for cooking pasta, typically at 212°F (100°C).
living-room> Where did I park? If you do not know, say UNKNOWN.
  UNKNOWN
```

The living room recalls the level. The garage is a different session, so it has no history. After three more exchanges, the parking level is out of the window, and the living room forgets it.

## Keep facts after a restart

The short-term memory is in RAM, so a restart clears it. After each exchange, the `entity` memory asks the chat model for facts about the user. It writes the facts to a file.

1. Install the packages:

    ```bash
    pip install --pre ovos-persona-server ovos-memory-plugins ovos-openai-plugin
    ```

2. Save the persona as `assistant.json`:

    ```json
    {
      "name": "assistant",
      "handlers": ["ovos-chat-openai-plugin"],
      "ovos-chat-openai-plugin": {
        "api_url": "https://llama.smartgic.io/v1",
        "key": "sk-none",
        "model": "qwen2.5:7b",
        "allow_system_prompts": true,
        "system_prompt": "You are a home assistant. Answer in at most fifteen words."
      },
      "memory_module": "ovos-memory-plugin-entity",
      "ovos-memory-plugin-entity": {
        "api_url": "https://llama.smartgic.io/v1",
        "model": "qwen2.5:7b",
        "backend": "json",
        "db_path": "~/.local/share/ovos/assistant_facts.json"
      }
    }
    ```

3. Start the server with server-side memory:

    ```bash
    CHAT_MEMORY=transparent ovos-persona-server --persona assistant.json --port 8337
    ```

4. Tell it something. The `user` field selects your memory. The server trusts the `user` value and does not check it, so this setup fits trusted clients only. On a server that untrusted clients share, keep `CHAT_MEMORY` off. See [Memory, RAG & embeddings](persona-server.md#memory-rag-embeddings).

    ```bash
    ask() {
      curl -s localhost:8337/openai/v1/chat/completions \
        -H 'content-type: application/json' \
        -d "{\"model\":\"assistant\",\"user\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"$2\"}]}" |
        python3 -c 'import sys,json; print(json.load(sys.stdin)["choices"][0]["message"]["content"])'
    }
    ask alice "My cat is called Pixel and I live in Lisbon."
    ```

5. Stop the server. Start it again with the command of step 3.

The facts file survives the restart. Its content after a run with the small demo model:

```json
{
  "alice": {
    "facts": [
      "Name: Pixel",
      "Location: Lisbon"
    ]
  }
}
```

After the restart, the persona adds these facts to every prompt for `alice`, as a system message. It adds nothing to the prompts of a user who has told it nothing. This script prints the context that the memory builds for each user:

```python
from ovos_memory_plugins.entity import EntityMemory
mem = EntityMemory(config={"backend": "json", "db_path": "~/.local/share/ovos/assistant_facts.json"})
for user in ("alice", "bob"):
    print(user, [(m.role.value, m.content) for m in mem.build_conversation_context("What is my cat called?", user)])
```

```text
alice [('system', 'Known facts about the user:\n- Name: Pixel\n- Location: Lisbon'), ('user', 'What is my cat called?')]
bob [('user', 'What is my cat called?')]
```

The memory stores and recalls the facts. The chat model decides which facts to extract. The small demo model stored the cat's name as `Name: Pixel`, which reads like the name of the user. The persona answered `I don't have that information, can you tell me about your pet's name?` to "What is my cat called?". Use a larger model for fact extraction.

The `longterm` memory keeps a rolling summary instead of facts. The chat model decides what a summary keeps, so a summary can drop a detail. Use `entity` for facts that must survive.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| The persona forgets after one or two turns | `max_history` is too small | Increase `max_history`. It counts messages, two for each exchange |
| The persona forgets everything after a restart | The default memory is in RAM | Use `ovos-memory-plugin-entity` |
| The server forgets between requests | `CHAT_MEMORY` is not `transparent` | Start the server with `CHAT_MEMORY=transparent` |
| The log says `dropped 1 system message(s)` | `allow_system_prompts` is off | Set `"allow_system_prompts": true` |
| The facts file holds wrong facts | The chat model is too small | Use a larger model, or set `extraction_prompt` |

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Persona Memory](persona-memory.md)
- [Give each person their own memory](persona-family-memory.md)
