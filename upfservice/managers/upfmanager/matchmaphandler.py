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


class MatchMapHandler(apimanager.UPFServiceAPIHandler):
    """All the accounts defined in the controller."""

    URLS = [r"/upf/v1/matchmap/([0-9.]*)",
            r"/upf/v1/matchmap"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, match_index=0):
        """List entries in the Match Map.

        Args:

            [0]: the Match Index

        Example URLs:

            GET /upf/v1/matchmap
            GET /upf/v1/matchmap/5

            ...
        """
        if match_index:
            return self.service.matchmap[int(match_index) - 1]
        else:
            return self.service.matchmap

    @apimanager.validate(min_args=0, max_args=1)
    def post(self, match_index=1, **request_data):
        """Insert entry in the Match Map.

        Args:

            [0]: the Match Index

        Request:
            version: protocol version (1.0)
            params: the list of parameters to be set

        Example URLs:

            POST /upf/v1/matchmap
            POST /upf/v1/matchmap/5

            ...
        """
        self.service.add_matchmap(int(match_index) - 1, request_data)
        self.set_status(201)

    @apimanager.validate(min_args=0, max_args=1)
    def delete(self, match_index=0):
        """Delete entries in the Match Map.

        Args:

            [0]: the Match Index

        Example URLs:

            DELETE /upf/v1/matchmap
            DELETE /upf/v1/matchmap/5

            ...
        """
        self.service.del_matchmap(int(match_index) - 1)
