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
import json
import logging
import time
from multiprocessing import Process

from pika.exceptions import ConnectionClosed

from globomap_loader.driver.generic import GenericDriver
from globomap_loader.loader.globomap import GloboMapClient
from globomap_loader.loader.globomap import GloboMapException
from globomap_loader.rabbitmq import RabbitMQClient
from globomap_loader.settings import DRIVER_FETCH_INTERVAL
from globomap_loader.settings import FACTOR
from globomap_loader.settings import GLOBOMAP_API_URL
from globomap_loader.settings import GLOBOMAP_RMQ_ERROR_EXCHANGE
from globomap_loader.settings import GLOBOMAP_RMQ_HOST
from globomap_loader.settings import GLOBOMAP_RMQ_PASSWORD
from globomap_loader.settings import GLOBOMAP_RMQ_PORT
from globomap_loader.settings import GLOBOMAP_RMQ_USER
from globomap_loader.settings import GLOBOMAP_RMQ_VIRTUAL_HOST

logger = logging.getLogger(__name__)


class CoreLoader(object):

    def __init__(self, driver_name=None):
        logger.info('Starting Globmap loader')
        self.globomap_client = GloboMapClient(GLOBOMAP_API_URL)

    def load(self):
        instances = []
        for _ in range(0, FACTOR):
            p = DriverWorker(
                self.globomap_client, GenericDriver(), UpdateExceptionHandler()
            )
            instances.append(p)
            p.start()


class DriverWorker(Process):
    """
    Worker bound to a driver instance that processes all the messages
    provided by the driver and then sleeps for the amount of seconds
    configured by the DRIVER_FETCH_INTERVAL envinroment variable.
    """

    def __init__(self, globomap_client, driver, exception_handler):
        Process.__init__(self)
        self.name = driver.__class__.__name__
        self.globomap_client = globomap_client
        self.driver = driver
        self.exception_handler = exception_handler

    def run(self):
        logger.info('called run method in process: %s', self.name)
        while True:
            try:
                self.driver.process_updates(self._process_update)
            except Exception:
                logger.exception(
                    'Error syncing updates from driver %s', self.driver)
            finally:
                logger.debug('No more updates found')
                logger.debug('Sleeping for %ss' % DRIVER_FETCH_INTERVAL)
                time.sleep(DRIVER_FETCH_INTERVAL)

    def _process_update(self, update, **kwargs):
        try:
            self.globomap_client.update_element_state(
                update['action'],
                update['type'],
                update['collection'],
                update.get('element'),
                update.get('key'),
            )
        except GloboMapException as err:
            if type(err.message) == bytes:
                error_msg = err.message.decode('utf-8')
            else:
                error_msg = err.message

            logger.error('Could not process update: %s', update)
            logger.debug('Status code: %s', err.status_code)
            logger.debug('Response body: %s', err.message)

            try:
                update['status'] = err.status_code
                update['error_msg'] = error_msg
                name = update.get('driver_name', self.name)

                self.exception_handler.handle_exception(
                    name, update, **kwargs)
            except Exception as err:
                logger.exception('Fail to handle update error')
                raise Exception(str(err))


class DriverFullLoadWorker(Process):
    """
    Worker bound to a driver instance that runs the 'full_load'
    method on the driver. This method must take care of all processing
    needed to recreate all the objects (collections and edges) in the domain
    that this driver is responsible for.
    """

    def __init__(self, driver):
        Process.__init__(self)
        self.name = driver.__class__.__name__
        self.driver = driver

    def run(self):
        try:
            full_load_action = getattr(self.driver, 'full_load', None)
            if callable(full_load_action):
                self.driver.full_load()
            else:
                logger.error("Driver does not implement 'full_load' method")
        except Exception:
            logger.exception(
                'Error syncing updates from driver %s', self.driver)
        return


class UpdateExceptionHandler(object):

    def __init__(self):
        self._connect_rabbit()

    def _connect_rabbit(self):
        self.rabbit_mq = RabbitMQClient(
            GLOBOMAP_RMQ_HOST, GLOBOMAP_RMQ_PORT, GLOBOMAP_RMQ_USER,
            GLOBOMAP_RMQ_PASSWORD, GLOBOMAP_RMQ_VIRTUAL_HOST
        )

    def handle_exception(self, driver_name, update, retry=True, **kwargs):
        try:
            logger.debug('Sending failing update to rabbitmq error queue')
            collection = update.get('collection')
            key = 'globomap.error.{}.{}'.format(driver_name, collection)
            self.rabbit_mq.post_message(
                GLOBOMAP_RMQ_ERROR_EXCHANGE,
                key,
                json.dumps(update),
                kwargs.get('headers')
            )
            logger.error(kwargs)
        except ConnectionClosed:
            if retry:
                logger.warning('RabbitMQ Connection closed, reconnecting')
                self._connect_rabbit()
                self.handle_exception(driver_name, update, False, **kwargs)
        except Exception as err:
            logger.exception('Unable to handle exception %s', err)
