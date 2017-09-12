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
import json
import logging

import requests


class GloboMapClient(object):

    log = logging.getLogger(__name__)

    def __init__(self, host):
        self.host = host

    def update_element_state(self, action, type, collection, element, key):
        if action.upper() == 'CREATE':
            return self.create(type, collection, element)
        elif action.upper() == 'UPDATE':
            return self.update(type, collection, key, element)
        elif action.upper() == 'PATCH':
            return self.patch(type, collection, key, element)
        elif action.upper() == 'DELETE':
            return self.delete(type, collection, key)

    def create(self, type, collection, payload):
        return self._make_request(
            'POST', self._build_uri(type, collection), payload
        )

    def update(self, type, collection, key, payload):
        try:
            return self._make_request(
                'PUT', self._build_uri(type, collection, key), payload
            )
        except ElementNotFoundException:
            return self.create(type, collection, payload)

    def patch(self, type, collection, key, payload):
        try:
            return self._make_request(
                'PATCH', self._build_uri(type, collection, key), payload
            )
        except ElementNotFoundException:
            return self.create(type, collection, payload)

    def delete(self, type, collection, key):
        try:
            return self._make_request(
                'DELETE', self._build_uri(type, collection, key)
            )
        except ElementNotFoundException:
            self.log.debug('Element %s already deleted' % key)

    def list(self, type, collection, keys=None):
        keys = keys if keys else []
        return self._make_request(
            'GET', self._build_uri(type, collection, ';'.join(keys))
        )

    def get(self, collection, key):
        elements = self.list(collection, [key])
        if elements:
            return elements[0]

    def _make_request(self, method, uri, data=None):
        request_url = '%s%s' % (self.host, uri)

        self._log_http('REQUEST', method, request_url, data)

        response = requests.request(method, request_url, data=json.dumps(data))
        status = response.status_code
        content = response.content

        self._log_http('RESPONSE', method, request_url, content, status)

        if status == 404:
            raise ElementNotFoundException()
        elif status >= 400:
            raise GloboMapException()
        return self._parse_response(content)

    def _log_http(self, operation, method, url, content=None, status=''):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug(
                '%s: %s %s %s %s' % (operation, method, url, status, content)
            )
        else:
            self.log.info(
                '%s: %s %s %s' % (operation, method, url, status)
            )

    def _parse_response(self, response):
        if response:
            return json.loads(response)

    def _build_uri(self, type, collection, key=None):
        uri = '/%s/%s' % (type, collection)
        uri += '/%s' % (key) if key else ''

        return uri


class GloboMapException(Exception):
    pass


class ElementNotFoundException(GloboMapException):
    pass
