import json

import pika
from timecardsystem.common.domain import events
from timecardsystem.common.dtos import message_dto
from timecardsystem.timecardservice import config

HOST, PORT = config.get_rabbitmq_host_and_port()


def publish_event(name, event: events.Event):
    dto = message_dto.MessagePublisherDTO()
    dto.set_serializer(json.dumps)
    dto.serialize_outgoing_message(event)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=HOST,
            port=PORT
        )
    )
    channel = connection.channel()

    channel.queue_declare(
        queue="test",
        durable=True,
        exclusive=False,
        auto_delete=False
    )

    channel.basic_publish(
        exchange='',
        routing_key="test",
        body=dto.serialized_message,
        properties=pika.BasicProperties(
            content_type=dto.message_properties
        )
    )
    connection.close()
