"""
   Copyright 2018 Globo.com

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
import logging

from globomap_loader.driver.consumer import RabbitMQClient
from globomap_loader.settings import GLOBOMAP_RMQ_EXCHANGE
from globomap_loader.settings import GLOBOMAP_RMQ_HOST
from globomap_loader.settings import GLOBOMAP_RMQ_KEY
from globomap_loader.settings import GLOBOMAP_RMQ_PASSWORD
from globomap_loader.settings import GLOBOMAP_RMQ_PORT
from globomap_loader.settings import GLOBOMAP_RMQ_QUEUE_NAME
from globomap_loader.settings import GLOBOMAP_RMQ_USER
from globomap_loader.settings import GLOBOMAP_RMQ_VIRTUAL_HOST


logger = logging.getLogger(__name__)


class GenericDriver(object):

    def __init__(self):
        self._connect_rabbitmq()

    def _connect_rabbitmq(self):
        self.rabbitmq = RabbitMQClient(
            GLOBOMAP_RMQ_HOST, GLOBOMAP_RMQ_PORT, GLOBOMAP_RMQ_USER,
            GLOBOMAP_RMQ_PASSWORD, GLOBOMAP_RMQ_VIRTUAL_HOST
        )

    def process_updates(self, callback):
        """
        Reads and processes messages from the GloboMap event bus until
        there's no message left in the target queue. Only acks message if
        processed successfully by the callback.
        """

        self.rabbitmq.set_settings(
            GLOBOMAP_RMQ_EXCHANGE, GLOBOMAP_RMQ_QUEUE_NAME, GLOBOMAP_RMQ_KEY, callback
        )

        try:
            self.rabbitmq.run()
        except Exception:
            self.rabbitmq.stop()
