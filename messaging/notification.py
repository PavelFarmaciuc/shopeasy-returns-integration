# notification.py – second consumer: customer notifications (simulated).
# Receives only RECEIVED, REJECTED and REFUNDED events (see BINDINGS in common.py)
# and prints the message that would be emailed to the customer.

import json

from messaging.common import NOTIFICATION_QUEUE, connect, declare_topology

TEXTS = {
    "RECEIVED": "We have received your return and will check it shortly.",
    "REJECTED": "Unfortunately your return could not be accepted. The item is on its way back to you.",
    "REFUNDED": "Your refund has been paid out.",
}


def handle_message(channel, method, properties, body) -> None:
    event = json.loads(body)
    text = TEXTS.get(event["newStatus"], "Your return status has changed.")
    print(f"[email] {event['returnId']}: {text}")
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    connection = connect()
    channel = connection.channel()
    declare_topology(channel)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=NOTIFICATION_QUEUE, on_message_callback=handle_message)
    print(f"Notification service waiting for messages on '{NOTIFICATION_QUEUE}'. Stop with Ctrl+C.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == "__main__":
    main()