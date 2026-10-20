# OpenAI Chat and Function Calling

!!! abstract "In a nutshell"
    Code written for the OpenAI SDK can talk to an OVOS persona. Set `base_url` to `ovos-persona-server` and use the persona name as the model. Chat, streaming and function calling with `tools` work. Your code runs the functions, and the persona writes the answer from the result.

## What you can do

`ovos-persona-server` serves a persona at `/openai/v1`. The persona answers through the chat engine that its config names. When that chat engine supports tools, the OpenAI `tools` and `tool_calls` fields work in both directions.

## User stories

The recipes ran with `openai` 3.35.1 against `ovos-persona-server --persona llm.json`. The persona uses `ovos-chat-openai-plugin` with the `qwen2.5:7b` model on an Ollama host:

```json
{
  "name": "llm",
  "solvers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "https://<your-ollama-host>/v1",
    "key": "unused",
    "model": "qwen2.5:7b",
    "system_prompt": "You are a helpful assistant who gives short, factual answers."
  }
}
```

### I have code for OpenAI chat completions

Set `base_url` to the `/openai/v1` prefix. The `model` field is the persona name.

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://localhost:8337/openai/v1")
print([m.id for m in client.models.list().data])
reply = client.chat.completions.create(
    model="llm", messages=[{"role": "user", "content": "What is the capital of Portugal? One word."}])
print(reply.choices[0].message.content)
```

```text
['llm']
Lisbon.
```

With `stream=True`, the answer arrives in chunks, as the OpenAI API sends it.

### My code calls my own functions through `tools`

The model asks for a call. Your code runs the function and sends the result back. The model then writes the answer.

```python
import json

def get_weather(city):
    return {"city": city, "temp_c": 21, "sky": "sunny"}

tools = [{"type": "function", "function": {
    "name": "get_weather", "description": "Current weather for a city",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}]

messages = [{"role": "user", "content": "What's the weather in Lisbon right now?"}]
first = client.chat.completions.create(model="llm", messages=messages, tools=tools)
call = first.choices[0].message.tool_calls[0]
print(first.choices[0].finish_reason, call.function.name, call.function.arguments)

messages.append(first.choices[0].message.model_dump(exclude_none=True))
messages.append({"role": "tool", "tool_call_id": call.id,
                 "content": json.dumps(get_weather(**json.loads(call.function.arguments)))})
print(client.chat.completions.create(model="llm", messages=messages, tools=tools).choices[0].message.content)
```

```text
tool_calls get_weather {"city": "Lisbon"}
The current weather in Lisbon is sunny with a temperature of 21 degrees Celsius.
```

With `stream=True`, the tool call arrives as one `tool_calls` delta: `get_weather` with `{"city": "Porto"}` for the question "Weather in Porto?".

`tool_choice` controls the call:

| `tool_choice` | Result |
| :--- | :--- |
| not set, or `"auto"` | The model decides |
| `"none"` | The model answers in text, `finish_reason` is `stop` |
| `{"type": "function", "function": {"name": "get_time"}}` | The model calls `get_time` |
| `"required"` | The server answers 422. The OVOS chat engine contract cannot force a tool call |

## Endpoint status

| Call | Status |
| :--- | :--- |
| `models.list` | Works |
| `chat.completions.create`, plain and streaming | Works |
| `tools` and `tool_calls`, plain and streaming | Works when the chat engine supports tools |
| `tool_choice="required"` | 422 |

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| The SDK gets 404 | `base_url` does not end in `/openai/v1` | Use `http://<host>:8337/openai/v1` |
| The answer has no `tool_calls` | The chat engine of the persona does not support tools | Use a chat engine with tool support, such as `ovos-chat-openai-plugin` |
| The model name is not found | `model` is not the persona name | Read the names from `client.models.list()` |

---
**Read next:** [OpenAI files, embeddings and RAG](vendor-api-openai-rag.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [Persona Server](persona-server.md) · [Other LLM SDKs](vendor-api-llm-sdks.md)
