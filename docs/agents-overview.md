# Agents Overview

!!! abstract "In a nutshell"
    This tab covers adding conversational AI or LLM-backed behavior to OVOS through personas, instead of (or alongside) fixed skills. It walks from the persona concept through engine choice, memory, tools, and the LLM backends a persona can run on. For a fixed, deterministic skill instead, see the Skills tab.

This tab is for anyone adding conversational AI or LLM-backed behavior to OVOS, instead of (or alongside) fixed skills.

## Start here

1. [Personas & PersonaService](personas.md): the entry concept, a persona is a configured AI agent OVOS can talk to.
2. [Agent Engine Types](agent-plugins.md): the different kinds of engine a persona can run on.
3. [Choosing an engine](agent-plugins.md#agent-engine-types): specialized agent engines beyond the basics.
4. [Building Agent Plugins](building-agent-plugins.md): write your own engine when the built-in ones don't fit.

## Personas

Two ways to extend a persona past a single-turn reply: give it memory across a conversation, or run it as its own service other clients can reach.

- [Persona Memory](persona-memory.md): giving a persona recall across a conversation
- [Persona Server](persona-server.md): hosting personas as a standalone service

## Loops, tools, interoperability

Once a persona can talk, it can also act. This group covers how an agent plans over multiple steps, how it calls out to tools, and how it reaches (or is reached by) agents and tools outside OVOS. Start with the loop architectures page.

- [Agentic Loop Architectures](agentic-loop.md): how an agent plans and acts over multiple steps.
- [Agent Tool Plugins](tool-plugins.md): giving an agent actions it can call.
- [Interoperability (MCP/UTCP/A2A)](agent-interop.md): connecting to tools and agents outside OVOS.

## LLM Backends

The engines a persona can run its language model on: a hosted or self-hosted OpenAI-style API, a local GGUF model, or an LLM used as a pipeline transformer instead of a persona.

- [OpenAI-compatible](openai-plugin.md): hosted or self-hosted OpenAI-style APIs.
- [GGUF / Local LLM](gguf-plugin.md): running a model locally.
- [LLM Transformers](llm-transformers.md): using an LLM as a pipeline transformer rather than a persona.

Want a fixed, deterministic skill instead of an open-ended agent? That's the Skills tab. Deploying a persona remotely over HiveMind? See [Remote Agents with HiveMind](hivemind-agents.md) in the Production tab.

---
**Read next:** [Personas & PersonaService](personas.md)
**Related:** [Skill Development Overview](skills-overview.md) · [Pipeline Overview & Reference](pipelines-overview.md) · [Production Overview](production-overview.md)
