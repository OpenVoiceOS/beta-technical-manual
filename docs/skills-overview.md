# Skill Development Overview

This tab is for developers building or maintaining an OVOS skill, the add-ons that teach the assistant to do things.

## Start here

1. [Your First Skill](first-skill.md): build a minimal working skill end to end.
2. [Anatomy of a Skill](skill-structure.md): what files a skill needs and what each one does.
3. [Intent Design](intents.md): how OVOS decides which skill handles an utterance.
4. [Test Your Skill](testing-your-skill.md): run and check your skill before shipping it.

## Tutorials

- [Skill Cookbook](skill-cookbook.md): worked recipes for common skill patterns.

## Guides

- [Design Guidelines](skill-design-guidelines.md): voice user interface design.
- [Best Practices](skill-best-practices.md): patterns that hold up in real deployments.
- [Migrating from Mycroft](migrating-from-mycroft.md): porting an existing `mycroft-core` skill.
- [Version-Compatible Skills & Plugins](version-compat-guide.md): supporting multiple OVOS versions at once.

## Logic & Intents

- [Adapt Intents](intents-adapt.md) and [Padatious Intents](intents-padatious.md): the two intent styles.
- [Asking the User](prompts.md), [Context](context.md), [Intent Layers](layers.md), [Permissions & Activation Control](permissions.md), [Continuous Conversation](converse.md), [Context & Sessions](session.md).
- [Dialog & Statements](statements.md), [SSML](ssml.md), [Customization](customization.md), [skill.json](skill-json.md).

## Skill APIs

- [ovos-workshop Overview](workshop-overview.md), [OVOSSkill API](ovos-skill.md), [Skill Base Classes](skill-classes.md), [Decorators](decorators.md).
- [Skill Settings](skill-settings.md), [Meta Settings](skill-settings-meta.md), [Filesystem](skill-filesystem.md), [Resource Files](resource-files.md).
- [GUI Support (legacy)](skill-gui.md), [Runtime Requirements (deprecated)](skill-runtime-requirements.md).

## Advanced Skill Types

- [Fallback Skills](fallbacks.md), [Common Query Skills](common-query.md), [Media Skills (OCP)](ocp-skills.md), [Universal Skills](universal-skills.md).

## More

- [Skill Dev F.A.Q.](skill-dev-faq.md): answers to common questions.
- [Testing Reference (ovoscope)](ovoscope-overview.md): the full testing toolkit.

Building an AI persona instead of a fixed skill? That's the Agents tab. Need the intent-matching internals? That's the Pipeline tab.
