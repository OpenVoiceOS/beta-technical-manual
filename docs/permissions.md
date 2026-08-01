# Permissions & Activation Control

!!! abstract "In a nutshell"
    Not every skill should be allowed to join every conversation. This page covers the
    controls that decide which skills may participate: converse whitelists and blacklists,
    activation modes, and the global skill blacklist. For switching groups of *intents* on
    and off inside one skill, see [Intent Layers](layers.md). That page owns the layering
    mechanism.

??? info "📐 Formal specification"
    Converse participation rules are specified by **[OVOS-CONVERSE-1](https://github.com/OpenVoiceOS/architecture/blob/dev/converse.md)**; see the [spec index](architecture-specs.md).

!!! note "Routing/participation controls, not a security boundary"
    Converse and fallback permission settings decide which already-loaded skills get to
    *participate* in a given turn. They are not a security or sandboxing mechanism. A
    skill that is loaded has full code-execution rights regardless of its converse
    whitelist/blacklist status; these settings cannot contain a malicious skill, they can
    only stop it from being offered a turn. See
    [Privacy & Security: skills are not sandboxed](privacy-security.md#skills-are-not-sandboxed).

## Permissions

**Module:** `ovos_workshop.permissions`

Permission enums control how the converse and fallback systems select which skills may participate.

### ConverseMode

Controls which skills are allowed to participate in converse at all.

```python
from ovos_workshop.permissions import ConverseMode

```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any skill may converse (default) |
| `WHITELIST` | Only explicitly whitelisted skills may converse |
| `BLACKLIST` | All skills except blacklisted ones may converse |

Configure in `mycroft.conf`:

```json
{
  "skills": {
    "converse": {
      "converse_mode": "accept_all",
      "converse_whitelist": ["skill-id-1"],
      "converse_blacklist": ["skill-id-2"]
    }
  }
}

```

!!! warning "What you should see in the log when a whitelist blocks converse"
    `ConverseService` returns `False` from this check silently. There is no dedicated log
    line announcing "skill X blocked by whitelist". The observable symptom instead: run
    `ologs | grep converse` (see [RaspOVOS Troubleshooting](raspovos-troubleshooting.md#how-to-debug-intent-matching), "How to
    debug intent matching")
    while talking to the device, and the non-whitelisted skill's `skill_id` simply never
    shows up as a candidate. No `mycroft.skill.converse.request`/response pair for it appears
    at all, and its `converse()` method is never invoked. If a skill you expect to converse is
    silent, check `converse_mode` and `converse_whitelist` in your config before assuming the
    skill itself is broken.

### ConverseActivationMode

Controls when a skill is allowed to add itself to the active skills list (enabling converse).

```python
from ovos_workshop.permissions import ConverseActivationMode

```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any skill may activate itself (default) |
| `PRIORITY` | [Skill](skill-design-guidelines.md) may only activate if no higher-priority skill is already active |
| `WHITELIST` | Only explicitly whitelisted skills may self-activate |
| `BLACKLIST` | All skills except blacklisted ones may self-activate |

Configure in `mycroft.conf`. `WHITELIST`/`BLACKLIST` here reuse the same
`converse_whitelist`/`converse_blacklist` lists shown above. There is no separate
activation-specific list:

```json
{
  "skills": {
    "converse": {
      "converse_activation": "accept_all"
    }
  }
}

```

### FallbackMode

Controls which skills may register as fallback handlers.

```python
from ovos_workshop.permissions import FallbackMode

```

| Value | Meaning |
|---|---|
| `ACCEPT_ALL` | Any `FallbackSkill` may handle utterances (default) |
| `WHITELIST` | Only explicitly whitelisted fallback skills may respond |
| `BLACKLIST` | All fallback skills except blacklisted ones may respond |

Configure in `mycroft.conf`:

```json
{
  "skills": {
    "fallbacks": {
      "fallback_mode": "accept_all",
      "fallback_whitelist": [],
      "fallback_blacklist": []
    }
  }
}

```

### Utility Functions

```python
from ovos_workshop.permissions import blacklist_skill, whitelist_skill

# Add a skill to the global blacklist in mycroft.conf
blacklist_skill("my-unwanted-skill-id")

# Remove from the blacklist
whitelist_skill("my-unwanted-skill-id")

```

!!! note
    These functions manage a separate, broader kill-switch: `skills.blacklisted_skills` in
    `mycroft.conf`. A skill listed there is prevented from loading at all. It is unrelated
    to the `converse_blacklist`/`fallback_blacklist` keys above, which only restrict
    participation in converse/fallback while the skill still loads normally.

These functions directly modify `mycroft.conf` and take effect on the next skill manager reload.

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*

---
**Read next:** [Converse](converse.md)
**Related:** [Intent Layers](layers.md) · [Security & Trust Model](security-model.md) · [Decorators](decorators.md) · [Session Aware Skills](session.md)
