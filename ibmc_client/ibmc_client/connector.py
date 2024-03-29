# Copyright (c) [2019-2022] xFusion Digital Technologies Co., Ltd.All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging
from time import sleep

import requests
import six

from ibmc_client import constants
from ibmc_client import exceptions
from ibmc_client import utils

LOG = logging.getLogger(__name__)


class Connector(object):
    """IBMC API connector base on requests"""

    # Default timeout in seconds for requests connect and read
    # http://docs.python-requests.org/en/master/user/advanced/#timeouts
    _DEFAULT_TIMEOUT = 60

    def __init__(self, address, username, password, verify_ca):
        self.base_url = '%s/redfish/v1' % address
        self.address = address
        self._username = username
        self._password = password
        self._verify_ca = verify_ca
        self.session = None
        self._resource_id = None

        # Initial request session
        self._conn = requests.Session()
        self._conn.verify = verify_ca

        from ibmc_client import __version__ as version
        self._conn.headers.update({
            'User-Agent': 'python-ibmcclient - v%s' % version
        })

        self._meta = self.request(constants.GET, self.base_url).json()
        utils.init_common_key(self._meta)

    @property
    def resource_id(self):
        return self._resource_id

    @property
    def system_base_url(self):
        return '%s/%s' % (self._meta['Systems']['@odata.id'],
                          self._resource_id)

    @property
    def manager_base_url(self):
        return '%s/%s' % (self._meta['Managers']['@odata.id'],
                          self._resource_id)

    @property
    def chassis_base_url(self):
        return '%s/%s' % (self._meta['Chassis']['@odata.id'],
                          self._resource_id)

    @property
    def task_service_base_url(self):
        return self._meta['Tasks']['@odata.id']

    @property
    def session_service_base_url(self):
        return self._meta['SessionService']['@odata.id']

    @property
    def version(self):
        return self._meta['RedfishVersion']  # pragma: no cover

    def get_url(self, resource):
        """get absolute URL for odata resource

        :param resource: redfish resource
        :return:
        """
        if isinstance(resource, six.string_types):
            path = resource
        elif isinstance(resource, dict) and resource.get("@odata.id", None):
            path = resource.get("@odata.id", None)

        if path.startswith(self.base_url):
            return path
        elif path.startswith('/redfish/v1'):
            return '%s%s' % (self.address, path)
        else:
            return '%s%s' % (self.base_url, path)

    def connect(self):
        if self.session is None:
            self._fetch_session()
            self._get_resource_id()

    def disconnect(self):
        try:
            session_path = '%(address)s%(location)s' % self.session
            self.request(constants.DELETE, session_path)
        except requests.exceptions.RequestException:  # pragma: no cover
            # Failed to delete session, just ignore the errors now.
            # may be the session has expired. we can let it expired auto.
            LOG.warning('Failed to delete session.')

    def _fetch_session(self):
        """Fetch and cache a new session"""
        payload = {
            'UserName': self._username,
            'Password': self._password
        }
        create_session_url = '%s/Sessions' % self.session_service_base_url
        res = self.request(constants.POST, create_session_url, json=payload)

        # cache session
        token = res.headers.get(constants.HEADER_AUTH_TOKEN)
        location = res.headers.get('Location')
        self.session = dict(address=self.address, token=token,
                            location=location)

        # update request credential header
        self._conn.headers.update({
            constants.HEADER_AUTH_TOKEN: token,
        })

    def _get_resource_id(self):
        """get resource id of server.

        - The value is 1 for a rack server.
        - The value is BladeN for a high-density server.
          N indicates the slot number of the server node. For example, Blade1.
        - The value is BladeN for a compute node or SwiN for a switch module
          in a blade server. N indicates the slot number of the compute node
          or switch module.
        """
        managers_url = self.address + self._meta['Managers']['@odata.id']
        res = self.request(constants.GET, managers_url).json()
        manager_odata_id = res['Members'][0]['@odata.id']
        self._resource_id = manager_odata_id.split('/')[-1]

    def request(self, method, url, json=None, etag=None, headers=None,
                retry=False):
        try:
            url = self.get_url(url)
            return self._request(method, url, json=json, etag=etag,
                                 headers=headers)
        except requests.exceptions.RequestException as e:
            response = e.response
            if response is not None:
                if not retry and response.status_code:
                    if response.status_code == 401:
                        # If session expired, renew session then retry
                        self._fetch_session()
                        return self.request(method, url, json=json, etag=etag,
                                            headers=headers, retry=True)

                    if response.status_code == 412:
                        # If 412 pre-condition checking failed,
                        # just retry after 10 seconds.
                        sleep(10)
                        return self.request(method, url, json=json, etag=etag,
                                            headers=headers, retry=True)

                LOG.warning('iBMC response -> %(method)s %(url)s, '
                            'code: %(code)s, response: %(resp_txt)s',
                            {'method': method, 'url': url,
                             'code': response.status_code,
                             'resp_txt': response.content})
                raise exceptions.raise_for_response(method, url, response)
            else:
                raise exceptions.IBMCConnectionError(url=url, error=e)

    def _request(self, method, url, json=None, etag=None, headers=None):
        # If request method is PATCH or PUT,
        # "If-Match" header is required by iBMC redfish API.
        if method.upper() in [constants.PATCH, constants.PUT]:
            headers = headers or {}
            if not etag:
                res = self.request(constants.GET, url)
                headers.update({
                    constants.HEADER_IF_MATCH:
                        res.headers.get(constants.HEADER_ETAG)})
            else:
                headers.update({constants.HEADER_IF_MATCH: etag})

        if method.upper() in [constants.POST, constants.PATCH, constants.PUT]:
            headers = headers or {}
            headers.update({constants.HEADER_CONTENT_TYPE: 'application/json'})

        if url.endswith('/Sessions') and method == constants.POST:
            LOG.debug('iBMC request -> %(method)s %(url)s',
                      {'method': method, 'url': url})
        else:
            LOG.debug(
                'iBMC request -> %(method)s %(url)s, payload:: %(payload)s',
                {'method': method, 'url': url, 'payload': json})

        req = requests.Request(method, url, json=json, headers=headers)
        prepped = self._conn.prepare_request(req)
        res = self._conn.send(prepped, timeout=self._DEFAULT_TIMEOUT)
        res.raise_for_status()
        LOG.debug('iBMC response -> %(method)s %(url)s, code: %(code)s, '
                  'content:: %(content)s',
                  {'method': method, 'url': url, 'code': res.status_code,
                   'content': res.text})
        return res
