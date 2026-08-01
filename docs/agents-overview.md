# Agents Overview

This tab is for anyone adding conversational AI or LLM-backed behavior to OVOS, instead of (or alongside) fixed skills.

## Start here

1. [Personas & PersonaService](personas.md): the entry concept, a persona is a configured AI agent OVOS can talk to.
2. [Agent Engine Types](agent-plugins.md): the different kinds of engine a persona can run on.
3. [Choosing an engine](agent-plugins.md#agent-engine-types): specialized agent engines beyond the basics.
4. [Building Agent Plugins](building-agent-plugins.md): write your own engine when the built-in ones don't fit.

## Personas

- [Persona Memory](persona-memory.md): giving a persona recall across a conversation
- [Persona Server](persona-server.md): hosting personas as a standalone service

## Loops, tools, interoperability

- [Agentic Loop Architectures](agentic-loop.md): how an agent plans and acts over multiple steps.
- [Agent Tool Plugins](tool-plugins.md): giving an agent actions it can call.
- [Interoperability (MCP/UTCP/A2A)](agent-interop.md): connecting to tools and agents outside OVOS.

## LLM Backends

- [OpenAI-compatible](openai-plugin.md): hosted or self-hosted OpenAI-style APIs.
- [GGUF / Local LLM](gguf-plugin.md): running a model locally.
- [LLM Transformers](llm-transformers.md): using an LLM as a pipeline transformer rather than a persona.

Want a fixed, deterministic skill instead of an open-ended agent? That's the Skills tab. Deploying a persona remotely over HiveMind? See [Remote Agents with HiveMind](hivemind-agents.md) in the Production tab.
