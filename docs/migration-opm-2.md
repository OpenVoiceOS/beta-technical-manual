# Migrating Wake-word Plugins to opm 2.0

!!! abstract "In a nutshell"
    Wake-word plugin maintainers are affected. opm 2.0 split the old
    single-call `found_wake_word(audio_data)` contract into a separate
    `update(chunk)` feed step and a zero-argument poll. Fix it by
    implementing both methods on the new contract.

### Wake-word plugin `found_wake_word()` signature change (opm 2.0)

opm 2.0 pulled apart what had been a single call into two steps: audio is
fed to the plugin separately now, and detection is polled with no
arguments at all. A wake-word plugin written for the one-argument form
still loads and still gets called after the caller-side change lands in a
listener service, but the call itself throws, since `found_wake_word()`
now runs with zero arguments where it used to expect the audio chunk.

`ovos-plugin-manager` 2.0 changed the `HotWordEngine` contract: audio is
fed separately, then detection is polled with no arguments.

```python
# old (pre-opm-2.0)
class MyWakeWordPlugin(HotWordEngine):
    def found_wake_word(self, audio_data) -> bool:
        ...

# new (opm 2.0+)
class MyWakeWordPlugin(HotWordEngine):
    def update(self, chunk: bytes) -> None:
        ...  # feed audio incrementally
    def found_wake_word(self) -> bool:
        ...  # poll with no arguments
```

Both listener services in the org landed the caller-side half of this
change on the same underlying opm bump: `mycroft-classic-listener`
`19d9961` (#12, 2026-01-09) and `ovos-simple-listener` `34e2219` (#20,
2026-01-23, commit message: "opm 2.0.0 introduced breaking change"). If
your wake-word plugin still implements the one-argument form, it will be
called with zero arguments and raise a `TypeError` on any listener service
updated past these commits.

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| `found_wake_word(audio_data)` one-arg form | before opm `2.0.0` | unverified | opm `2.0.0` · caller-side landed in `19d9961` / `34e2219` |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Plugin Maintainers](updating-plugins.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
