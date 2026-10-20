# Use a Persona per Device

--8<-- "snippets/alpha-only.md"

This page gives each device its own persona on one OVOS install. You have more than one device, for example a speaker in the kitchen and one in the bedroom. You want a different persona in each room.

## What the setup includes

- A summon command, such as "talk to ada", sets `persona_id` on the session of the device that heard it.
- Other devices keep their own persona, or none.
- A release command, such as "stop talking to ada", clears `persona_id` on that session only.

## Steps

--8<-- "snippets/community-servers.md"

1. Install the packages:

    ```bash
    pip install --pre ovos-persona ovos-openai-plugin
    ```

2. Save two personas, `personas/ada.json` and `personas/bo.json`. This is `ada.json`:

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

3. Save this script as `devices.py` and run it from the directory that holds `personas`. It sends the voice commands of two devices through the persona intent matcher:

    ```python
    from ovos_bus_client.message import Message
    from ovos_bus_client.session import Session
    from ovos_persona import PersonaService
    from ovos_utils.fakebus import FakeBus

    svc = PersonaService(bus=FakeBus(), config={"personas_path": "personas"})


    def heard(text, sess):
        msg = Message("recognizer_loop:utterance", {"utterances": [text]}, {"session": sess.serialize()})
        match = svc.match_high([text], "en-US", msg)
        return match.updated_session if match else sess


    kitchen = heard("talk to ada", Session("kitchen"))
    bedroom = heard("talk to bo", Session("bedroom"))
    for sess in (kitchen, bedroom, Session("hall")):
        print(sess.session_id, "->", sess.persona_id)
    for sess in (kitchen, bedroom):
        print(sess.session_id, "says:", " ".join(svc.query("What is your name? Answer with your name only.",
                                                         sess.persona_id, sess)))
    kitchen = heard("stop talking to ada", kitchen)
    print("kitchen after release ->", kitchen.persona_id)
    ```

Output of a run:

```text
kitchen -> ada
bedroom -> bo
hall -> None
kitchen says: Ada.
bedroom says: Bo.
kitchen after release -> None
```

The persona is in the session, not in the service. A device that sends its session with each message, such as a HiveMind satellite, keeps its persona until a release command. A client can also set `persona_id` in the session that it sends, with no voice command.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| All devices change persona together | The devices share one session id | Give each device its own session id |
| The summon does nothing | The name does not match a loaded persona | Use the name from the persona file. Look in the log for `Failed to load` |

## Related pages

- [Personas and Memory](personas-and-memory.md)
- [Personas](personas.md)
- [Run several personas on one server](persona-several-on-one-server.md)
