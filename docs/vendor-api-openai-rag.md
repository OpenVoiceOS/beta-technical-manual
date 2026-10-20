# OpenAI Files, Embeddings and RAG

!!! abstract "In a nutshell"
    Code written for the OpenAI files, embeddings and vector stores calls works against `ovos-persona-server`. The server stores the files, embeds them with a local embeddings plugin and searches them. A persona can then answer from those files through the `ovos-openai-rag-memory-plugin`. Nothing leaves your machine.

## What you can do

The `/openai/v1` prefix of `ovos-persona-server` serves the OpenAI `embeddings`, `files` and `vector_stores` calls. These calls give an OpenAI client one way to add documents to a persona and to check what the persona can find. They are not a full document platform: they hold enough to test and use retrieval with the OpenAI shapes.

## User stories

The recipes ran with `openai` 3.35.1 against `ovos-persona-server`, with the persona of [OpenAI chat and function calling](vendor-api-openai-chat.md). The embeddings plugin gives vectors with 384 values.

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://localhost:8337/openai/v1")
```

### I need embeddings

```python
result = client.embeddings.create(model="x", input=["cats purr", "the moon"])
print(len(result.data), len(result.data[0].embedding))
```

```text
2 384
```

`encoding_format="base64"` also works. The embeddings plugin decides the size of the vector and ignores `model`.

### I search my own documents with files and vector stores

Upload the files, attach them to a vector store and search it. The server cuts each file into chunks and embeds them.

```python
cats = client.files.create(file=("cats.txt", b"the cat sat on the mat. cats are fluffy animals that purr."),
                           purpose="assistants")
moon = client.files.create(file=("moon.txt", b"the moon orbits the earth and affects ocean tides."),
                           purpose="assistants")
store = client.vector_stores.create(name="kb")
for f in (cats, moon):
    client.vector_stores.files.create(vector_store_id=store.id, file_id=f.id)
hits = client.vector_stores.search(vector_store_id=store.id, query="fluffy animal on a mat").data
print([h.filename for h in hits])
```

```text
['cats.txt', 'moon.txt']
```

The search returns the best match first. `files.list`, `files.retrieve`, `files.content`, `vector_stores.list` and `vector_stores.retrieve` return the same shapes as the OpenAI API.

To remove a document, detach it from each vector store with `client.vector_stores.files.delete(vector_store_id=..., file_id=...)`, then delete the file with `client.files.delete(file_id)`.

### My persona answers from my documents

`ovos-openai-rag-memory-plugin` comes with `ovos-openai-plugin`. Before each turn, it searches a vector store and gives the hits to the chat engine of the persona. Set it as the `memory_module` of the persona. `vector_store_id` is the id from the store that you made above.

```json
{
  "name": "kb",
  "solvers": ["ovos-chat-openai-plugin"],
  "ovos-chat-openai-plugin": {
    "api_url": "https://<your-ollama-host>/v1",
    "key": "unused",
    "model": "qwen2.5:7b"
  },
  "memory_module": "ovos-openai-rag-memory-plugin",
  "ovos-openai-rag-memory-plugin": {
    "api_url": "http://localhost:8337/openai/v1",
    "vector_store_id": "vs_...",
    "inject_mode": "user"
  }
}
```

A file in the store said that the office cat is called Bartolomeu. The persona was asked "What is the name of the office cat?":

| Config | Answer |
| :--- | :--- |
| `inject_mode` not set (`"system"`) | `I don't have any information about an office cat. ...` |
| `inject_mode: "user"` | `The name of the office cat is Bartolomeu.` |
| `inject_mode: "system"` and `allow_system_prompts: true` in the chat engine config | `The name of the office cat is Bartolomeu.` |

`ovos-chat-openai-plugin` drops system messages that it did not write, unless `allow_system_prompts` is `true`. The default `inject_mode` puts the hits in a system message, so this chat engine does not see them. Use `inject_mode: "user"` with this chat engine.

The plugin can also search a hosted OpenAI vector store: set `api_url` to that server and `key` to its token.

## Endpoint status

| Call | Status |
| :--- | :--- |
| `embeddings.create`, float and base64 | Works |
| `files` create, list, retrieve, content, delete | Works |
| `vector_stores` create, list, retrieve, search | Works |
| `vector_stores.files` create, list, delete | Works |

## Troubleshooting

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| The persona does not use the documents | The chat engine drops the system message that holds the hits | Set `inject_mode: "user"`, or `allow_system_prompts: true` in the chat engine |
| The persona does not use the documents, and the log has `RAG search failed` | The search call failed. The persona answers without the documents | Check `api_url` and `vector_store_id` |
| Two uploads give the same file id | The server keeps one copy of identical bytes | Upload changed content as a changed file |

---
**Read next:** [Other LLM SDKs](vendor-api-llm-sdks.md)
**Related:** [Drop-in Vendor APIs](vendor-apis.md) · [OpenAI chat and function calling](vendor-api-openai-chat.md) · [Persona Server](persona-server.md)
