# Other LLM SDKs

!!! abstract "In a nutshell"
    Code written for the Anthropic, Ollama, Gemini, Cohere, Bedrock or Hugging Face TGI clients can talk to an OVOS persona. Change the base URL in the client to the prefix of that vendor on `ovos-persona-server`. The persona answers in the shape that the client expects.

## What you can do

`ovos-persona-server` mounts the chat API of each vendor under its own prefix. The persona name is the model name. Every prefix sends the request to the same persona.

## User stories

These SDKs asked the persona of [OpenAI chat and function calling](vendor-api-openai-chat.md) "What is the capital of Portugal? One word.". Each line is the answer that the SDK returned.

| SDK | Setting | Call | Output |
| :--- | :--- | :--- | :--- |
| `anthropic` 1.15.0 | `Anthropic(base_url="http://localhost:8337/anthropic")` | `messages.create(model="llm", max_tokens=50, messages=[...])` | `Lisbon.` |
| `ollama` 0.6.3 | `ollama.Client(host="http://localhost:8337/ollama")` | `chat(model="llm", messages=[...])` | `Lisbon.` |
| `google-genai` 2.31.0 | `genai.Client(http_options=types.HttpOptions(base_url="http://localhost:8337/gemini"))` | `models.generate_content(model="llm", contents=...)` | `Lisbon.` |
| `cohere` 7.2.0 | `cohere.Client(base_url="http://localhost:8337/cohere")` | `chat(model="llm", message=...)` | `Lisbon.` |
| `boto3` 1.43.115 | `boto3.client("bedrock-runtime", endpoint_url="http://localhost:8337/bedrock")` | `converse(modelId="llm", messages=[...])` | `Lisbon.` |
| `huggingface_hub` 2.2.0 | `InferenceClient(model="http://localhost:8337/tgi")` | `text_generation(...)` | `Lisbon.` |

### I have code for the Anthropic SDK

```python
from anthropic import Anthropic

client = Anthropic(api_key="unused", base_url="http://localhost:8337/anthropic")
reply = client.messages.create(model="llm", max_tokens=50,
                               messages=[{"role": "user", "content": "What is the capital of Portugal? One word."}])
print(reply.content[0].text)
```

```text
Lisbon.
```

### I have code for Ollama

```python
import ollama

client = ollama.Client(host="http://localhost:8337/ollama")
reply = client.chat(model="llm", messages=[{"role": "user", "content": "What is the capital of Portugal? One word."}])
print(reply.message.content)
```

```text
Lisbon.
```

## Endpoint status

| Client | Call | Status |
| :--- | :--- | :--- |
| Anthropic | `messages.create` | Works |
| Ollama | `chat` | Works |
| Gemini | `models.generate_content` | Works |
| Cohere | `chat` | Works |
| AWS Bedrock | `converse` | Works |
| Hugging Face TGI | `text_generation` | Works |
| Hugging Face TGI | `chat_completion` | Not served. The server answers 404 at `/tgi/v1/chat/completions`. Use the OpenAI prefix for chat completions |

---
**Read next:** [Text-to-speech vendor APIs](vendor-api-tts.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [OpenAI chat and function calling](vendor-api-openai-chat.md) · [Persona Server](persona-server.md)
