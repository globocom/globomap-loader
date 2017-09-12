"""
   Copyright 2017 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import unittest
from mock import patch, Mock
from driver.generic import GenericDriver
from tests.util import open_json


class TestGenericDriver(unittest.TestCase):

    def test_get_updates_returning_empty_updates(self):
        self._mock_rabbitmq_client([])
        self.assertEqual([], GenericDriver().updates())

    def test_get_updates_returning_list_of_updates(self):
        updates = [open_json('tests/json/globomap/vip.json')]
        self._mock_rabbitmq_client(updates)
        self.assertEqual(updates, GenericDriver().updates())

    def _mock_rabbitmq_client(self, messages):
        rabbit_mq_mock = patch("driver.generic.RabbitMQClient").start()
        rabbit_mq = Mock()
        rabbit_mq_mock.return_value = rabbit_mq
        read_messages_mock = Mock()
        read_messages_mock.next.return_value = messages
        rabbit_mq.read_messages.return_value = read_messages_mock
        return rabbit_mq_mock
