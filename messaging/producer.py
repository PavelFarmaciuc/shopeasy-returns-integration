# producer.py – publishes return status events to RabbitMQ.
# Stands in for the systems that learn something new about a return
# (carrier, warehouse/WMS, payment provider).
#
# Usage:
#   python -m messaging.producer                          -> runs the demo scenario
#   python -m messaging.producer RET-2026-00457 RECEIVED  -> sends one single event

import json
import sys
import time
import uuid
from datetime import datetime, timezone

import pika

from messaging.common import EXCHANGE, connect, declare_topology, routing_key


def build_event(return_id: str, new_status: str, source: str) -> dict:
    """Create the event message as a Python dict."""
    return {
        "messageId": str(uuid.uuid4()),
        "returnId": return_id,
        "newStatus": new_status,
        "source": source,
        "occurredAt": datetime.now(timezone.utc).isoformat(),
    }


def publish(channel, event: dict) -> None:
    """Send one event to the exchange; the routing key tells RabbitMQ which queues get a copy."""
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key(event["newStatus"]),
        body=json.dumps(event),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=pika.DeliveryMode.Persistent,   # survives a broker restart
            message_id=event["messageId"],
        ),
    )
    print(f"-> published {event['returnId']} -> {event['newStatus']} (from {event['source']})")


# Demo: the full life of one return, plus a duplicate and three faulty events
DEMO_EVENTS = [
    ("RET-2026-00457", "APPROVED", "RETURN_PLATFORM"),
    ("RET-2026-00457", "LABEL_SENT", "RETURN_PLATFORM"),
    ("RET-2026-00457", "IN_TRANSIT", "CARRIER"),
    ("RET-2026-00457", "RECEIVED", "WAREHOUSE"),
    ("RET-2026-00457", "RECEIVED", "WAREHOUSE"),        # duplicate -> harmless (idempotent)
    ("RET-2026-00457", "INSPECTED", "WAREHOUSE"),
    ("RET-2026-00457", "ACCEPTED", "CONDITION_SERVICE"),
    ("RET-2026-00457", "REFUNDED", "PAYMENT_PROVIDER"),
    ("RET-2026-00457", "CLOSED", "RETURN_PLATFORM"),
    ("RET-2026-00462", "NEW", "WAREHOUSE"),             # forbidden transition -> 409 -> dead letter
    ("RET-9999", "RECEIVED", "WAREHOUSE"),              # unknown return -> 404 -> dead letter
    ("RET-2026-00457", "BANANA", "WAREHOUSE"),          # invalid status -> 422 -> dead letter
]


def main() -> None:
    connection = connect()
    channel = connection.channel()
    declare_topology(channel)   # make sure queues exist, so no message is lost

    if len(sys.argv) == 3:      # single event from the command line
        publish(channel, build_event(sys.argv[1], sys.argv[2], "MANUAL"))
    else:
        for return_id, status, source in DEMO_EVENTS:
            publish(channel, build_event(return_id, status, source))
            time.sleep(0.5)     # slow down so you can follow it in the consumer terminals

    connection.close()


if __name__ == "__main__":
    main()