# Control an external device: publish to an MQTT broker

!!! abstract "In a nutshell"
    You build an `OVOSSkill` that controls a networked device over MQTT, publishing commands with `paho.mqtt.client.Client` behind the same timeout-plus-spoken-error safety pattern as an HTTP call.

**When you'd want this:** a device on the network, such as a smart plug or a relay board, listens for commands on an MQTT topic. The skill publishes to that topic on a voice command. It uses the same timeout-plus-spoken-error pattern as [Recipe 3](recipe-safe-api-call.md), applied to a broker connection instead of an HTTP call.

This recipe needs a broker client that OVOS does not ship. Declare it in your skill's
`pyproject.toml` (`dependencies = ["paho-mqtt"]`) and install it, or every run stops at
`ModuleNotFoundError: No module named 'paho'`.

```python
import paho.mqtt.client as mqtt
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler

BROKER_HOST = "192.168.1.50"
BROKER_PORT = 1883
TOPIC = "home/office/plug1/set"
CONNECT_TIMEOUT = 5


class MqttPlugSkill(OVOSSkill):
    def initialize(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id="ovos-mqtt-plug-skill")
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=CONNECT_TIMEOUT)
            self.client.loop_start()
        except (OSError, TimeoutError) as e:
            self.log.warning(f"MQTT broker unreachable at init: {e}")

    @intent_handler("turn_on_plug.intent")
    def handle_turn_on(self, message):
        self._publish("ON", "plug_turned_on", "plug_unreachable")

    @intent_handler("turn_off_plug.intent")
    def handle_turn_off(self, message):
        self._publish("OFF", "plug_turned_off", "plug_unreachable")

    def _publish(self, payload, ok_dialog, fail_dialog):
        try:
            info = self.client.publish(TOPIC, payload, qos=1)
            info.wait_for_publish(timeout=CONNECT_TIMEOUT)
            if not info.is_published():
                raise TimeoutError("publish did not confirm in time")
        except (OSError, TimeoutError, ValueError, RuntimeError) as e:
            self.log.warning(f"MQTT publish failed: {e}")
            self.speak_dialog(fail_dialog)
            return
        self.speak_dialog(ok_dialog)

    def shutdown(self):
        self.client.loop_stop()
        self.client.disconnect()
```

### Moving parts

- `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=...)` is the current, non-deprecated way to construct a client. Give each device a unique `client_id`, or the broker drops the duplicate session.
- `connect(host, port, keepalive=...)` is a blocking call. Wrap it, and any other use of the client, in a `try`/`except` for `OSError` and `TimeoutError`. Speak a dialog instead of letting the exception surface. This is the same safety pattern as [Calling an external API safely](recipe-safe-api-call.md).
- `loop_start()` runs the client's network loop on a background thread so `publish()` calls don't block waiting on broker I/O. Call `loop_stop()` in `shutdown()` to clean it up.
- `publish(topic, payload, qos=...)` returns an `MQTTMessageInfo`. `wait_for_publish(timeout=...)` blocks until the broker acknowledges it, or the timeout elapses. `is_published()` confirms it went through, so a network drop mid-call is caught instead of silently swallowed.
- `disconnect()` closes the connection cleanly. Pair it with `loop_stop()` in `shutdown()` so the skill doesn't leave a background thread or an open socket behind when unloaded.
- If the hardware is attached to the OVOS device itself, a [PHAL plugin](phal.md) is the intended home for device control. A skill and broker like this one suits a device reachable over the network instead.

---
**Read next:** [Skill Cookbook](skill-cookbook.md)
**Related:** [Calling an external API safely](recipe-safe-api-call.md) · [PHAL plugin](phal.md) · [Ambient bus-event behavior](recipe-ambient-bus-events.md)
