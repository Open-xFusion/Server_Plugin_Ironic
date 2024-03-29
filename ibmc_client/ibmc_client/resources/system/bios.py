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

# Version 0.0.2
from ibmc_client import constants
from ibmc_client.resources import BaseResource

_BOOT_SEQUENCE_MAP = {
    'HardDiskDrive': constants.BOOT_SOURCE_TARGET_HDD,
    'DVDROMDrive': constants.BOOT_SOURCE_TARGET_CD,
    'PXE': constants.BOOT_SOURCE_TARGET_PXE,
}


class Bios(BaseResource):
    """iBMC System Resource Model"""

    def extra_init_action(self):
        self._attrs = self._json['Attributes']

    def __init__(self, resp, ibmc_client=None):
        """Initial a iBMC System BIOS resource

        :param resp: bios attribute resource HTTP response
        """
        super(Bios, self).__init__(resp, ibmc_client=ibmc_client)
        self._attrs = None

    @property
    def boot_sequence(self):
        # v5 series server
        keys = [k for k in self._attrs.keys()
                if k.startswith('BootTypeOrder')]
        seq = [self._attrs.get(t) for t in sorted(keys)]
        return [_BOOT_SEQUENCE_MAP.get(t, t) for t in seq]
