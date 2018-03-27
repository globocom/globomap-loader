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
import importlib
import json
import logging
import time
from multiprocessing import Process

from pika.exceptions import ConnectionClosed

from globomap_core_loader.api.database import Session
from globomap_core_loader.api.job.models import Job
from globomap_core_loader.api.job.models import JobError
from globomap_core_loader.loader.globomap import GloboMapClient
from globomap_core_loader.loader.globomap import GloboMapException
from globomap_core_loader.rabbitmq import RabbitMQClient
from globomap_core_loader.settings import DRIVER_FETCH_INTERVAL
from globomap_core_loader.settings import DRIVERS
from globomap_core_loader.settings import GLOBOMAP_API_URL
from globomap_core_loader.settings import GLOBOMAP_RMQ_ERROR_EXCHANGE
from globomap_core_loader.settings import GLOBOMAP_RMQ_HOST
from globomap_core_loader.settings import GLOBOMAP_RMQ_PASSWORD
from globomap_core_loader.settings import GLOBOMAP_RMQ_PORT
from globomap_core_loader.settings import GLOBOMAP_RMQ_USER
from globomap_core_loader.settings import GLOBOMAP_RMQ_VIRTUAL_HOST


class CoreLoader(object):

    log = logging.getLogger(__name__)

    def __init__(self, driver_name=None):
        self.log.info('Starting Globmap loader')
        self.drivers = self._load_drivers(driver_name)
        self.globomap_client = GloboMapClient(GLOBOMAP_API_URL)

    def load(self):
        for driver in self.drivers:
            p = DriverWorker(
                self.globomap_client, driver, UpdateExceptionHandler()
            )
            p.start()

    def full_load(self):
        for driver in self.drivers:
            DriverFullLoadWorker(driver).start()

    def _load_drivers(self, driver_name=None):
        self.log.info('Loading drivers: %s' % DRIVERS)
        drivers = []
        for driver_config in DRIVERS:
            package = driver_config['package']
            driver_class = driver_config['class']

            if driver_name and driver_name != driver_class:
                continue

            factor = driver_config.get('factor') or 1
            for _ in range(0, factor):

                try:
                    driver_instance = self._create_driver_instance(
                        driver_class, package, driver_config.get('params')
                    )
                    drivers.append(driver_instance)
                    self.log.info("Driver '%s' loaded" % driver_class)
                except AttributeError:
                    self.log.exception('Cannot load driver %s' % driver_class)
                except ImportError:
                    self.log.exception('Cannot load driver %s' % driver_class)
                except Exception:
                    self.log.exception(
                        'Unknown error loading driver %s' % driver_config
                    )
                finally:
                    Session.remove()

        return drivers

    def _create_driver_instance(self, driver_class, package, params):
        driver_type = getattr(importlib.import_module(package), driver_class)
        has_update_method = hasattr(driver_type, 'process_updates') and \
            callable(getattr(driver_type, 'process_updates'))

        if not has_update_method:
            raise AttributeError(
                "Driver '%s' doesnt implement 'process_updates'" % driver_class
            )

        if params:
            return driver_type(params)
        else:
            return driver_type()


class DriverWorker(Process):
    """
    Worker bound to a driver instance that processes all the messages
    provided by the driver and then sleeps for the amount of seconds
    configured by the DRIVER_FETCH_INTERVAL envinroment variable.
    """

    log = logging.getLogger(__name__)

    def __init__(self, globomap_client, driver, exception_handler):
        Process.__init__(self)
        self.session = Session()
        self.name = driver.__class__.__name__
        self.globomap_client = globomap_client
        self.driver = driver
        self.exception_handler = exception_handler

    def run(self):
        print('called run method in process: %s' % self.name)
        while True:
            try:
                self.driver.process_updates(self._process_update)
            except Exception:
                self.log.exception(
                    'Error syncing updates from driver {}'.format(self.driver)
                )
            finally:
                self.log.debug('No more updates found')
                self.log.debug('Sleeping for %ss' % DRIVER_FETCH_INTERVAL)
                Session.remove()
                time.sleep(DRIVER_FETCH_INTERVAL)

    def _process_update(self, update):
        try:
            if update.get('jobid'):
                self.log.info('Processing update from JOB %s' %
                              update.get('jobid'))
            self.globomap_client.update_element_state(
                update['action'],
                update['type'],
                update['collection'],
                update.get('element'),
                update.get('key'),
            )
            self.update_job_success(update.get('jobid'))
        except GloboMapException as e:
            self.log.error('Could not process update: %s' % update)
            self.log.error('Status code: %s' % e.status_code)
            self.log.error('Response body: %s' % e.response)

            try:
                self.update_job_error(update.get('jobid'), update, e)

                update['status'] = e.status_code
                update['error_msg'] = e.response
                name = update.get('driver_name', self.name)

                self.exception_handler.handle_exception(name, update)
            except:
                self.log.exception('Fail to handle update error')
                self.session.rollback()
                raise
            finally:
                Session.remove()

    def update_job_success(self, job_id):
        if job_id:
            job = Job.find_by_uuid(job_id, for_update=True)
            if job:
                job.increment_success_count()
                job.save()
            else:
                self.log.error('Job with id %s not found' % job_id)

    def update_job_error(self, job_id, update, err):

        if job_id:
            job = Job.find_by_uuid(job_id, for_update=True)
            if job:
                err = JobError(
                    json.dumps(update), err.response, err.status_code
                )
                job.add_error(err)
                job.save()
            else:
                self.log.error('Job with id %s not found' % job_id)


class DriverFullLoadWorker(Process):
    """
    Worker bound to a driver instance that runs the 'full_load'
    method on the driver. This method must take care of all processing
    needed to recreate all the objects (collections and edges) in the domain
    that this driver is responsible for.
    """

    log = logging.getLogger(__name__)

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
                self.log.error("Driver does not implement 'full_load' method")
        except Exception:
            self.log.exception(
                'Error syncing updates from driver %s' % self.driver
            )
        return


class UpdateExceptionHandler(object):

    log = logging.getLogger(__name__)

    def __init__(self):
        self._connect_rabbit()

    def _connect_rabbit(self):
        self.rabbit_mq = RabbitMQClient(
            GLOBOMAP_RMQ_HOST, GLOBOMAP_RMQ_PORT, GLOBOMAP_RMQ_USER,
            GLOBOMAP_RMQ_PASSWORD, GLOBOMAP_RMQ_VIRTUAL_HOST
        )

    def handle_exception(self, driver_name, update, retry=True):
        try:
            self.log.debug('Sending failing update to rabbitmq error queue')
            collection = update.get('collection')
            key = 'globomap.error.%s.%s' % (driver_name, collection)
            self.rabbit_mq.post_message(
                GLOBOMAP_RMQ_ERROR_EXCHANGE,
                key,
                json.dumps(update)
            )
        except ConnectionClosed:
            if retry:
                self.log.error('RabbitMQ Connection closed, reconnecting')
                self._connect_rabbit()
                self.handle_exception(driver_name, update, False)
        except Exception as err:
            self.log.exception('Unable to handle exception %s', err)
