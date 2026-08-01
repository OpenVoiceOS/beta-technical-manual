# Migrating to ovos-config 2.0.0

!!! abstract "In a nutshell"
    Device and fleet operators with a customized `core.pipeline` list are
    affected, plus anyone comparing the `lang` config value as a literal
    string. `ovos-config` 2.0.0 renamed every pipeline stage ID to a
    plugin-id form and changed the default `lang` casing. Fix it by
    updating `core.pipeline` to the new plugin IDs and comparing `lang`
    case-insensitively.

### ovos-config 2.0.0: pipeline renames and `en-US` casing

This is the single largest deployer-facing config break the ecosystem
shipped: every short pipeline stage ID a deployer might have hand-listed
in `core.pipeline` was replaced by a plugin-id form in one commit, and the
old spellings were not rejected, just silently ignored. A customized
pipeline written against the old IDs did not error after upgrading; it
just quietly stopped registering some of its stages, with `adapt_low` and
`common_qa` dropped from the default list entirely. The same commit also
flipped the default `lang` casing from `"en-us"` to `"en-US"`, breaking
any code doing an exact string comparison against the old default.

`ovos-config` `2.0.0` (`e24e9ce`, #228, 2025-06-16) is the single largest
deployer-facing config break in the ecosystem. If you have a customized
`core.pipeline` list in your `mycroft.conf`, every stage ID in it is now
unregistered and will be silently skipped rather than erroring.

```json
// old core.pipeline (pre-2.0.0)
["stop_high", "converse", "ocp_high", "padatious_high", "adapt_high",
 "ocp_medium", "fallback_high", "stop_medium", "adapt_medium",
 "fallback_medium", "adapt_low", "common_qa", "fallback_low"]

// new core.pipeline (2.0.0+)
["ovos-stop-pipeline-plugin-high", "ovos-converse-pipeline-plugin",
 "ovos-ocp-pipeline-plugin-high", "ovos-padatious-pipeline-plugin-high",
 "ovos-adapt-pipeline-plugin-high", "ovos-ocp-pipeline-plugin-medium",
 "ovos-fallback-pipeline-plugin-high", "ovos-stop-pipeline-plugin-medium",
 "ovos-adapt-pipeline-plugin-medium", "ovos-fallback-pipeline-plugin-medium",
 "ovos-m2v-pipeline-high", "ovos-fallback-pipeline-plugin-low"]
// note: adapt_low and common_qa are dropped from the default list entirely
// (now standalone opt-in plugins); add "ovos-adapt-pipeline-plugin-low" and
// the common-query plugin id back explicitly if you still want them.
```

These are the same pipeline stages as the current default, just written in the old
short-name notation instead of full plugin IDs. See [Pipelines Overview](pipelines-overview.md)
for the current stage list and how the pipeline matcher chain works.

The same commit changed the default `"lang"` value in `mycroft.conf` from
`"en-us"` to `"en-US"`. Any code doing an exact string comparison against
the lowercase default breaks. Compare case-insensitively or update the
literal.

Also in this commit: `skills.directory` dropped from shipped defaults,
`gui.idle_display_skill` renamed `skill-ovos-homescreen.openvoiceos` →
`ovos-skill-homescreen.openvoiceos`, and the entire NLP-plugin config block
(`tokenization`, `segmentation`, `keyword_extract`, `coref`, `postag`) was
removed from `mycroft.conf` (no longer core-config-driven).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Short pipeline stage IDs (`stop_high`, `converse`, ...) | before `2.0.0` (2025-06-16) | unverified | `2.0.0` |
| `lang` default `"en-us"` | before `2.0.0` | n/a | `2.0.0` (now `"en-US"`) |
| `skills.directory` default key | before `2.0.0` | unverified | `2.0.0` |
| NLP plugin config block | before `2.0.0` | unverified | `2.0.0` |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Device & Fleet Operators](updating-deployers.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
