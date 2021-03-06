# Copyright (c) 2015 Nicolas JOUANIN
#
# See the file license.txt for copying permission.
import unittest
import asyncio

from hbmqtt.mqtt.connect import ConnectPacket, ConnectVariableHeader, ConnectPayload
from hbmqtt.mqtt.packet import MQTTFixedHeader, PacketType
from hbmqtt.errors import MQTTException

class ConnectPacketTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()

    def test_decode_ok(self):
        data = b'\x10\x3e\x00\x04MQTT\x04\xce\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage\x00\x04user\x00\x08password'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        message = self.loop.run_until_complete(ConnectPacket.from_stream(stream))
        self.assertEqual(message.variable_header.proto_name, "MQTT")
        self.assertEqual(message.variable_header.proto_level, 4)
        self.assertTrue(message.variable_header.username_flag)
        self.assertTrue(message.variable_header.password_flag)
        self.assertFalse(message.variable_header.will_retain_flag)
        self.assertEqual(message.variable_header.will_qos, 1)
        self.assertTrue(message.variable_header.will_flag)
        self.assertTrue(message.variable_header.clean_session_flag)
        self.assertFalse(message.variable_header.reserved_flag)
        self.assertEqual(message.payload.client_id, '0123456789')
        self.assertEqual(message.payload.will_topic, 'WillTopic')
        self.assertEqual(message.payload.will_message, 'WillMessage')
        self.assertEqual(message.payload.username, 'user')
        self.assertEqual(message.payload.password, 'password')

    def test_decode_fail_protocol_name(self):
        data = b'\x10\x3e\x00\x04TTQM\x04\xce\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage\x00\x04user\x00\x08password'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_decode_fail_reserved_flag(self):
        data = b'\x10\x3e\x00\x04MQTT\x04\xcf\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage\x00\x04user\x00\x08password'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_decode_fail_miss_clientId(self):
        data = b'\x10\x0a\x00\x04MQTT\x04\xce\x00\x00'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        stream.feed_eof()
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_decode_fail_miss_willtopic(self):
        data = b'\x10\x16\x00\x04MQTT\x04\xce\x00\x00\x00\x0a0123456789'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        stream.feed_eof()
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_decode_fail_miss_username(self):
        data = b'\x10\x2e\x00\x04MQTT\x04\xce\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        stream.feed_eof()
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_decode_fail_miss_password(self):
        data = b'\x10\x34\x00\x04MQTT\x04\xce\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage\x00\x04user'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(data)
        stream.feed_eof()
        with self.assertRaises(MQTTException):
            self.loop.run_until_complete(ConnectPacket.from_stream(stream))

    def test_encode(self):
        header = MQTTFixedHeader(PacketType.CONNECT, 0x00, 0)
        variable_header = ConnectVariableHeader(0xce, 0, 'MQTT', 4)
        payload = ConnectPayload('0123456789', 'WillTopic', 'WillMessage', 'user', 'password')
        message = ConnectPacket(header, variable_header, payload)
        encoded = message.to_bytes()
        self.assertEqual(encoded, b'\x10\x3e\x00\x04MQTT\x04\xce\x00\x00\x00\x0a0123456789\x00\x09WillTopic\x00\x0bWillMessage\x00\x04user\x00\x08password')
