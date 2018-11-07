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
import os

DRIVER_FETCH_INTERVAL = int(os.getenv('DRIVER_FETCH_INTERVAL', 60))

GLOBOMAP_API_URL = os.getenv('GLOBOMAP_API_URL')
GLOBOMAP_API_USERNAME = os.getenv('GLOBOMAP_API_USERNAME')
GLOBOMAP_API_PASSWORD = os.getenv('GLOBOMAP_API_PASSWORD')

GLOBOMAP_RMQ_USER = os.getenv('GLOBOMAP_RMQ_USER')
GLOBOMAP_RMQ_PASSWORD = os.getenv('GLOBOMAP_RMQ_PASSWORD')
GLOBOMAP_RMQ_HOST = os.getenv('GLOBOMAP_RMQ_HOST')
GLOBOMAP_RMQ_PORT = int(os.getenv('GLOBOMAP_RMQ_PORT', 5672))
GLOBOMAP_RMQ_VIRTUAL_HOST = os.getenv('GLOBOMAP_RMQ_VIRTUAL_HOST')
GLOBOMAP_RMQ_QUEUE_NAME = os.getenv('GLOBOMAP_RMQ_QUEUE_NAME')
GLOBOMAP_RMQ_EXCHANGE = os.getenv('GLOBOMAP_RMQ_EXCHANGE')
GLOBOMAP_RMQ_ERROR_EXCHANGE = os.getenv('GLOBOMAP_RMQ_ERROR_EXCHANGE')
GLOBOMAP_RMQ_KEY = os.getenv('GLOBOMAP_RMQ_BINDING_KEY', 'globomap.updates')

SCHEDULER_FREQUENCY_EXEC = os.getenv('SCHEDULER_FREQUENCY_EXEC')

LOADER_UPDATE = 'globomap_loader_update'

RETRIES = os.getenv('RETRIES', 10)

FACTOR = int(os.getenv('FACTOR', 1))

QUERIES = os.getenv('QUERIES', '')

ZBX_PASSIVE_MONITOR_LOADER = os.getenv('ZBX_PASSIVE_MONITOR_LOADER')
ZBX_PASSIVE_MONITOR_SCHED_QUERIES = os.getenv(
    'ZBX_PASSIVE_MONITOR_SCHED_QUERIES')

SENTRY_DSN = os.getenv('SENTRY_DSN')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': 'level=%(levelname)s timestamp=%(asctime)s module=%(name)s line=%(lineno)d ' +
            'message=%(message)s '
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        },
    },
    'loggers': {
        'globomap_loader': {
            'handlers': ['default', 'sentry'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
