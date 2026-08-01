# Skill Development Overview

!!! abstract "In a nutshell"
    This tab covers building and maintaining an OVOS skill: the code that teaches the assistant to do a specific thing. It walks from a first minimal skill through intent design, testing, and the full skill API, and it covers porting an existing Mycroft skill. For LLM-backed conversational behavior instead of a fixed skill, see the Agents tab.

This tab is for developers building or maintaining an OVOS skill, the add-ons that teach the assistant to do things.

## Start here

1. [Your First Skill](first-skill.md): build a minimal working skill end to end.
2. [Anatomy of a Skill](skill-structure.md): what files a skill needs and what each one does.
3. [Intent Design](intents.md): how OVOS decides which skill handles an utterance.
4. [Test Your Skill](testing-your-skill.md): run and check your skill before shipping it.

## Tutorials

Worked, copyable examples of common skill patterns, once you've built the first-skill walkthrough above.

- [Skill Cookbook](skill-cookbook.md): worked recipes for common skill patterns.

## Guides

Longer-form guidance on design, deployment-tested practice, and keeping a skill working across OVOS versions or ported from Mycroft. Start with Best Practices if the skill already works and you want it to hold up in production.

- [Design Guidelines](skill-design-guidelines.md): voice user interface design.
- [Best Practices](skill-best-practices.md): patterns that hold up in real deployments.
- [Migrating from Mycroft](migrating-from-mycroft.md): porting an existing `mycroft-core` skill.
- [Version-Compatible Skills & Plugins](version-compat-guide.md): supporting multiple OVOS versions at once.
- [For Skill Maintainers](updating-skills.md) and [Updating from Older OVOS](updating-from-older-ovos.md): keeping an existing skill current.

## Logic & Intents

The mechanics of matching an utterance to a skill and handling it once matched: the two intent styles, session and context state, and how a skill talks back to the user.

- [Adapt Intents](intents-adapt.md) and [Padatious Intents](intents-padatious.md): the two intent styles.
- [Asking the User](prompts.md), [Context](context.md), [Intent Layers](layers.md), [Permissions & Activation Control](permissions.md), [Continuous Conversation](converse.md), [Context & Sessions](session.md).
- [Dialog & Statements](statements.md), [SSML](ssml.md), [Customization](customization.md), [skill.json](skill-json.md).

## Skill APIs

Reference pages for the base classes and helper APIs a skill can call. Start with the ovos-workshop overview to see how the pieces fit together.

- [ovos-workshop Overview](workshop-overview.md), [OVOSSkill API](ovos-skill.md), [Skill Base Classes](skill-classes.md), [Decorators](decorators.md).
- [Skill Settings](skill-settings.md), [Meta Settings](skill-settings-meta.md), [Filesystem](skill-filesystem.md), [Resource Files](resource-files.md).
- [GUI Support (legacy)](skill-gui.md), [Runtime Requirements (deprecated)](skill-runtime-requirements.md).

## Advanced Skill Types

Skill base classes for specific, non-default behavior: catching unmatched utterances, answering open questions, playing media, or running across multiple devices.

- [Fallback Skills](fallbacks.md), [Common Query Skills](common-query.md), [Media Skills (OCP)](ocp-skills.md), [Universal Skills](universal-skills.md).

## More

- [Skill Dev F.A.Q.](skill-dev-faq.md): answers to common questions.
- [Testing Reference (ovoscope)](ovoscope-overview.md): the full testing toolkit.

Building an AI persona instead of a fixed skill? That's the Agents tab. Need the intent-matching internals? That's the Pipeline tab.

---
**Read next:** [Your First Skill](first-skill.md)
**Related:** [Agents Overview](agents-overview.md) · [Pipeline Overview & Reference](pipelines-overview.md) · [Plugins Index & Overview](plugins-index.md) · [Reference Overview](reference-overview.md)
