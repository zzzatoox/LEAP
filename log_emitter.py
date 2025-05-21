import time
import random
from fluent import sender, event

fluent_logger = sender.FluentSender(tag="log", host="localhost", port=24224)

services = ["auth", "payment", "orders", "notification"]
levels = ["info", "warning", "error", "critical"]

messages = {
    "info": "Service is running smoothly.",
    "warning": "Service responded with latency.",
    "error": "Failed to connect to database.",
    "critical": "Service is down!",
}


def generate_log():
    service = random.choice(services)
    level = random.choices(levels, weights=[0.6, 0.2, 0.15, 0.05])[0]
    msg = messages[level]
    log = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "service": service,
        "level": level,
        "message": msg,
        "correlation_id": f"req-{random.randint(1000, 9999)}",
    }
    return log


while True:
    log_entry = generate_log()
    print("Sent log:", log_entry)
    fluent_logger.emit("event", log_entry)
    time.sleep(random.uniform(0.5, 2.0))
