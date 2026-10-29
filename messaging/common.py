# common.py – shared RabbitMQ settings and topology for all messaging programs.
# Topology = which exchanges and queues exist and how they are connected (bindings).

import os

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))

# Main topic exchange: every status event of a return is published here
EXCHANGE = "returns.events"
ROUTING_KEY_PREFIX = "return.status."          # e.g. "return.status.RECEIVED"

# Dead-letter setup: messages a consumer rejects end up in this queue
DEAD_LETTER_EXCHANGE = "returns.dead-letter"
DEAD_LETTER_QUEUE = "returns.dead-letter"

# One queue per consumer, with the routing-key patterns it is interested in
STATUS_UPDATER_QUEUE = "returns.status-updater"
NOTIFICATION_QUEUE = "returns.notification"

BINDINGS = {
    STATUS_UPDATER_QUEUE: ["return.status.*"],            # every status change
    NOTIFICATION_QUEUE: [                                  # only what the customer is told
        "return.status.RECEIVED",
        "return.status.REJECTED",
        "return.status.REFUNDED",
    ],
}


def routing_key(status: str) -> str:
    """Build the routing key for a status, e.g. 'RECEIVED' -> 'return.status.RECEIVED'."""
    return ROUTING_KEY_PREFIX + status


def connect() -> pika.BlockingConnection:
    """Open a connection to RabbitMQ (default user guest/guest, only allowed from localhost)."""
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))


def declare_topology(channel) -> None:
    """Create exchanges, queues and bindings. Safe to call many times (idempotent)."""
    # Dead-letter exchange + queue
    channel.exchange_declare(exchange=DEAD_LETTER_EXCHANGE, exchange_type="fanout", durable=True)
    channel.queue_declare(queue=DEAD_LETTER_QUEUE, durable=True)
    channel.queue_bind(queue=DEAD_LETTER_QUEUE, exchange=DEAD_LETTER_EXCHANGE)

    # Main exchange
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    # Consumer queues: rejected messages go to the dead-letter exchange
    for queue, patterns in BINDINGS.items():
        channel.queue_declare(
            queue=queue,
            durable=True,
            arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
        )
        for pattern in patterns:
            channel.queue_bind(queue=queue, exchange=EXCHANGE, routing_key=pattern)