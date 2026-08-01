# Migrating Audio-Transformer Priority Values

!!! abstract "In a nutshell"
    Deployers running more than one audio-transformer plugin are affected.
    `ovos-dinkum-listener` fixed its transformer chain to run in ascending
    `priority` order, matching the spec, instead of the descending order
    it used before. Fix it by inverting any `priority` values you assigned
    under the old order.

### Audio-transformer chain-order flip

The transformer chain had been running in the opposite order from what
its own docstring claimed for some time: plugins sorted by `priority`
descending, highest number first, while the OVOS-TRANSFORM-1 spec and
`ovos-core`'s own transformer chains expected ascending order. Fixing it
meant a deployment with more than one active audio transformer plugin
could see its processing order silently invert after the upgrade, with no
error to signal the change, only a chain now running its stages in the
reverse sequence from before.

`ovos-dinkum-listener`'s `AudioTransformersService` sorted plugins by
`priority` **descending** (highest number ran first) with a docstring that
said the opposite of what the OVOS-TRANSFORM-1 spec expects. `1fd909f`
(#236, 2026-06-28) dropped `reverse=True`: the chain now runs in
**ascending** priority order (lowest number first, highest last), matching
`OVOS-TRANSFORM-1 §4` and the ordering `ovos-core` already used for its own
transformer chains.

```python
# old: priority=1 ran LAST (reverse=True)
# new: priority=1 runs FIRST (ascending)
```

If you assigned `priority` values assuming the old descending order,
invert them: old `priority=P` behaved like new `priority=(100-P)` in
relative terms. Any deployment with more than one active
`listener.audio_transformers` plugin where order matters can see a silent
behavior change after upgrading past this commit (ovos-dinkum-listener `1fd909f`, #236).

Lifecycle:

| Change | Active | Deprecated but functional | Dropped |
|---|---|---|---|
| Descending `priority` sort (`reverse=True`) | before `1fd909f` (2026-06-28) | n/a | `1fd909f` |

---
**Read next:** [Updating From Older OVOS](updating-from-older-ovos.md)
**Related:** [For Device & Fleet Operators](updating-deployers.md) · [Version-Compatible Skills & Plugins](version-compat-guide.md)
