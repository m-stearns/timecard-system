from typing import Callable

import pika
from pika.adapters.select_connection import SelectConnection
from pika.channel import Channel
from pika.frame import Method
from pika.spec import BasicProperties
from timecardsystem.timecardservice import config

HOST, PORT = config.get_rabbitmq_host_and_port()


class Consumer:

    def __init__(self):
        self.channel: Channel = None
        self.connection: SelectConnection = None
        self.custom_callback: Callable = None

    def set_on_message_callback(self, callback_func: Callable):
        self.custom_callback = callback_func

    def connect(self):
        parameters = pika.ConnectionParameters(host=HOST, port=PORT)
        connection = pika.SelectConnection(
            parameters,
            on_open_callback=self.on_connected)
        self.connection = connection

    def on_connected(self, connection: SelectConnection):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, new_channel: Channel):
        self.channel = new_channel
        self.channel.queue_declare(
            queue="test",
            durable=True,
            exclusive=False,
            auto_delete=False,
            callback=self.on_queue_declared
        )

    def on_queue_declared(self, frame: Method):
        self.channel.basic_consume('test', self.handle_delivery)

    def handle_delivery(
        self,
        channel: Channel,
        method,
        header: BasicProperties,
        body: bytes
    ):
        """
        channel: pika.channel.Channel
        method: pika.spec.Basic.Deliver
        header: pika.spec.BasicProperties
        body: bytes
        """
        if self.custom_callback(channel, method, header, body):
            self.ack_message(method.delivery_tag)
        else:
            self.nack_message(method.delivery_tag)

    def ack_message(self, delivery_tag: int):
        self.channel.basic_ack(delivery_tag)

    def nack_message(self, delivery_tag: int):
        self.channel.basic_nack(delivery_tag)

    def start(self):
        self.connect()
        self.connection.ioloop.start()

    def stop(self):
        self.connection.ioloop.stop()
        self.connection.close()
