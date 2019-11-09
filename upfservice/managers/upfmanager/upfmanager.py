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

"""UPF Manager."""

import re
import socket

from upfservice.managers.upfmanager.uemaphandler import UEMapHandler
from upfservice.core.service import EService

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7777
DEFAULT_ELEMENT = "upfr"


class UPFManager(EService):
    """Service exposing the UPF function

    Parameters:
        port: upf console port (optional, default: 8888)
        element: upf element (optional, default: upfr)
    """

    HANDLERS = [UEMapHandler]

    def __init__(self, context, service_id, port=DEFAULT_PORT,
                 element=DEFAULT_ELEMENT):

        super().__init__(context=context, service_id=service_id, port=port,
                         element=element)

    @property
    def uemap(self):
        """Return UE Map."""

        uemap = self.read_handler("uemap")

        print(uemap)

        return []

    @property
    def element(self):
        """Return element."""

        return self.params["element"]

    @element.setter
    def element(self, value):
        """Set element."""

        if "element" in self.params and self.params["element"]:
            raise ValueError("Param element can not be changed")

        self.params["element"] = value

    @property
    def port(self):
        """Return port."""

        return self.params["port"]

    @port.setter
    def port(self, value):
        """Set port."""

        if "port" in self.params and self.params["port"]:
            raise ValueError("Param port can not be changed")

        self.params["port"] = int(value)

    def write_handler(self, handler, value):
        """Write to a click handler."""

        sock = socket.socket()
        sock.connect((DEFAULT_HOST, self.port))

        f_hand = sock.makefile()
        line = f_hand.readline()

        if line != "Click::ControlSocket/1.3\n":
            raise ValueError("Unexpected reply: %s" % line)

        cmd = "write %s.%s %s\n" % (self.element, handler, value)
        sock.send(cmd.encode("utf-8"))

        line = f_hand.readline()

        regexp = '([0-9]{3}) (.*)'
        match = re.match(regexp, line)

        while not match:
            line = f_hand.readline()
            match = re.match(regexp, line)

        groups = match.groups()

        return (int(groups[0]), groups[1])

    def read_handler(self, handler):
        """Read a click handler."""

        sock = socket.socket()
        sock.connect((DEFAULT_HOST, self.port))

        f_hand = sock.makefile()
        line = f_hand.readline()

        if line != "Click::ControlSocket/1.3\n":
            raise ValueError("Unexpected reply: %s" % line)

        cmd = "read %s.%s\n" % (self.element, handler)
        sock.send(cmd.encode("utf-8"))

        line = f_hand.readline()

        regexp = '([0-9]{3}) (.*)'
        match = re.match(regexp, line)

        while not match:
            line = f_hand.readline()
            match = re.match(regexp, line)

        groups = match.groups()

        if int(groups[0]) == 200:

            line = f_hand.readline()
            res = line.split(" ")

            length = int(res[1])
            data = f_hand.read(length)

            return (int(groups[0]), data)

        return (int(groups[0]), line)
