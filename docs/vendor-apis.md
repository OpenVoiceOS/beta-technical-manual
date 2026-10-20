# Drop-in Vendor APIs

!!! abstract "In a nutshell"
    You have code that calls OpenAI, ElevenLabs, DeepL or another cloud API. The OVOS servers answer the same requests with your own plugins. Change one URL in your code, and the speech, the translation or the answer comes from your machine. The SDK, the request and the response stay the same.

## What you can do

Each OVOS server mounts the API of several vendors, each under its own URL prefix. All prefixes answer at the same time. The servers accept any API key and ignore it, so put authentication in a reverse proxy.

| You have code for | Point it at | Read |
| :--- | :--- | :--- |
| OpenAI chat completions, with or without `tools` | `ovos-persona-server`, `/openai/v1` | [OpenAI chat and function calling](vendor-api-openai-chat.md) |
| OpenAI files, embeddings and vector stores | `ovos-persona-server`, `/openai/v1` | [OpenAI files, embeddings and RAG](vendor-api-openai-rag.md) |
| Anthropic, Ollama, Gemini, Cohere, Bedrock or Hugging Face TGI | `ovos-persona-server` | [Other LLM SDKs](vendor-api-llm-sdks.md) |
| OpenAI `audio.speech`, MaryTTS, ElevenLabs or Amazon Polly | `ovos-tts-server` | [Text-to-speech vendor APIs](vendor-api-tts.md) |
| OpenAI `audio.transcriptions`, Groq, Deepgram, ElevenLabs Scribe, IBM Watson or AssemblyAI | `ovos-stt-server` | [Speech-to-text vendor APIs](vendor-api-stt.md) |
| DeepL, Amazon Translate, LibreTranslate, Azure Translator or Google Cloud Translation | `ovos-translate-server` | [Translation vendor APIs](vendor-api-translate.md) |

## How the recipes were measured

Each page shows a recipe for each vendor. The recipe uses the vendor's official SDK, and the output under it is the real output of that SDK against a running OVOS server. The page names the SDK version and the OVOS plugin that gave the output. Another plugin gives another voice, transcript or answer.

## What stays different

A matching request and response shape does not make the service the same. The OVOS plugin decides the quality, the languages and the speed. Model names and voice names from the vendor are accepted and ignored. Each page lists the calls that the server does not support.

## Reference

The full list of prefixes for each server is on [Server Compatibility Layers](server-compat-layers.md). Install and run each server from its own page: [STT Server](stt-server.md), [TTS Server](tts-server.md), [Translate Server](translate-server.md) and [Persona Server](persona-server.md).

---
**Read next:** [OpenAI chat and function calling](vendor-api-openai-chat.md)
**Related:** [Server Compatibility Layers](server-compat-layers.md) · [Persona Server](persona-server.md) · [Public Server Stack](public-server-stack.md)
