# `dig_for_message`

!!! abstract "In a nutshell"
    A lot of OVOS code seems to know which message it is responding to without ever being
    told. `self.speak("hello")` reaches the right satellite. `self.lang` returns the
    language of the person who is talking, not the device default. The mechanism behind
    that is `dig_for_message`, which walks the Python call stack and finds the `Message`
    your handler was called with. It is powerful, and it fails in ways that are hard to
    guess. This page is for developers who need to rely on it, extend it, or work out why
    it returned `None`.

`dig_for_message` lives in `ovos_bus_client.message`. It takes no required arguments and
returns the `Message` currently being handled, or `None`.

```python
from ovos_bus_client.message import dig_for_message

def some_helper():
    message = dig_for_message()   # nobody passed it in
```

---

## The problem it solves

Almost everything in OVOS is per-session. The language to answer in, the satellite to
speak to, and the intent context to read all come from the `Message` that triggered the
current work. Threading that message through every function that might need it would put
a `message` parameter on most of the skill API.

Instead, the framework reaches up the call stack and finds it. That is why these work
with no message argument:

| Call | What it digs the message for |
|---|---|
| `self.speak(...)` | Forwards from the triggering message, so the reply routes back to the same client |
| `self.lang` | Reads the session language of the current speaker |
| `self.get_response(...)` | Binds the follow-up prompt to the originating session |
| `SessionManager.get()` | Resolves the session off the current message's carrier |

## How it works

`dig_for_message` calls `inspect.stack()`, then walks the frames from the most recent
outward. In each frame it inspects the **named parameters** of that function. It returns
the value of the first parameter that is a `Message` instance.

The scan stops after `max_records` frames, which defaults to **10**.

## The rules it actually follows

These are the behaviors that surprise people. Each one follows from "named parameters of
frames on the current stack, nearest first".

| Case | Found? | Why |
|---|:---:|---|
| `def handler(message)` | yes | A named parameter holding a `Message` |
| `def handler(self, message)` | yes | `self` is inspected, is not a `Message`, and the scan continues |
| `def handler(*, message=None)` | yes | Keyword-only parameters are still named parameters |
| A `Message` in a local variable | **no** | Only parameters are inspected, never other locals |
| A `Message` passed into `*args` | **no** | Variadic arguments are not named parameters |
| A `Message` passed into `**kwargs` | **no** | Same reason |
| A handler more than 10 frames down | **no** | Past the `max_records` limit |
| Anything on a different thread | **no** | A new thread has its own stack |

Two more that matter when the result is wrong rather than missing:

- **The nearest frame wins.** If a helper is itself called with a different `Message`,
  that inner message shadows the outer one.
- **Within one frame, declaration order wins.** For `def f(a, b)` called with two
  messages, `a` is returned. This is parameter order, not "the first argument that
  happens to be a message".

## Where it breaks

!!! warning "Threads and callbacks lose the message"
    The stack is per-thread. Work handed to a `Thread`, an executor, a timer callback, or
    an event loop runs on a stack that never contained your handler, so
    `dig_for_message()` returns `None` there. Capture the message in the calling frame and
    pass it in explicitly:

    ```python
    def handle_intent(self, message):
        # wrong: the worker digs an empty stack
        Thread(target=self._work).start()

        # right: hand the message across the boundary
        Thread(target=self._work, args=(message,)).start()

    def _work(self, message):
        ...
    ```

The depth limit bites for the same reason in long call chains. Raise it with
`dig_for_message(max_records=50)` if you genuinely need to reach further, but treat that
as a sign the message should have been a parameter.

## Guidance

Use `dig_for_message` when you are writing framework or plugin code that cannot change
its own signature, and the caller reasonably has a message on the stack.

Prefer an explicit `message` parameter everywhere else. Explicit passing survives thread
boundaries, deep call chains, and refactoring that inserts a frame in the middle. It also
makes the dependency visible to whoever reads the function next.

When a helper can be called both ways, accept the message and fall back:

```python
def helper(message=None):
    message = message or dig_for_message()
```

That is the pattern the framework itself uses, and it lets a caller who has the message be
explicit while a caller who does not still works.

---
**Read next:** [Bus Recipes](bus-recipes.md)
**Related:** [Session Aware Skills](session.md) · [MessageBus Service](bus-service.md) · [Conversational Context](context.md)
