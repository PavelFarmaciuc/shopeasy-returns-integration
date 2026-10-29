# status_updater.py – consumer: keeps the return status in Program A up to date.
# For every status event it calls PATCH /returns/{id}/status on the REST API.
#   success          -> ack    (message is deleted)
#   business error   -> reject (message goes to the dead-letter queue; retrying won't help)
#   technical error  -> nack + requeue after a pause (message stays; retry when API is back)

import json
import time

import requests

from messaging.common import STATUS_UPDATER_QUEUE, connect, declare_topology
from rest_api.client import ApiError, MarketplaceClient

RETRY_DELAY_SECONDS = 5
client = MarketplaceClient()


def handle_message(channel, method, properties, body) -> None:
    """Called by pika for every message that arrives in our queue."""
    tag = method.delivery_tag

    # 1. Read the event – a broken message can never succeed -> dead letter
    try:
        event = json.loads(body)
        return_id, new_status = event["returnId"], event["newStatus"]
    except (json.JSONDecodeError, KeyError) as error:
        print(f"x  unreadable message ({error}) -> dead letter")
        channel.basic_reject(delivery_tag=tag, requeue=False)
        return

    # 2. Update the status in Program A
    try:
        result = client.update_status(return_id, new_status)
        print(f"ok {return_id}: status is now {result['status']}")
        channel.basic_ack(delivery_tag=tag)

    except ApiError as error:
        if 400 <= error.status_code < 500:
            # Business error (404 unknown, 409 forbidden, 422 invalid): the message itself is wrong
            print(f"x  {return_id} -> {new_status} rejected: {error} -> dead letter")
            channel.basic_reject(delivery_tag=tag, requeue=False)
        else:
            # Server error (5xx): try again later
            print(f"!  API error {error} -> retry in {RETRY_DELAY_SECONDS}s")
            time.sleep(RETRY_DELAY_SECONDS)
            channel.basic_nack(delivery_tag=tag, requeue=True)

    except requests.RequestException:
        # Technical error: API not reachable or timeout -> keep the message, retry later
        print(f"!  API not reachable -> {return_id} stays in queue, retry in {RETRY_DELAY_SECONDS}s")
        time.sleep(RETRY_DELAY_SECONDS)
        channel.basic_nack(delivery_tag=tag, requeue=True)


def main() -> None:
    connection = connect()
    channel = connection.channel()
    declare_topology(channel)
    channel.basic_qos(prefetch_count=1)    # take one message at a time
    channel.basic_consume(queue=STATUS_UPDATER_QUEUE, on_message_callback=handle_message)
    print(f"Status updater waiting for messages on '{STATUS_UPDATER_QUEUE}'. Stop with Ctrl+C.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == "__main__":
    main()