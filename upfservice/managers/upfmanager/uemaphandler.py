#!/usr/bin/env python3
#
# Copyright (c) 2019 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""UE Map handler."""

import upfservice.managers.apimanager.apimanager as apimanager


# pylint: disable=W0223
class UEMapHandler(apimanager.UPFServiceAPIHandler):
    """All the accounts defined in the controller."""

    URLS = [r"/upf/v1/uemap/([0-9.]*)"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, ue_ip=None):
        """List entries in the UE Map.

        Args:

            [0]: the UE Ip

        Example URLs:

            GET /upf/v1/uemap
            GET /upf/v1/uemap/10.10.0.5

            ...
        """

        if ue_ip:
            return self.service.uemap[ue_ip]

        return self.service.uemap
