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
import time

from iptc import Chain, Match as IPT_Match, Rule, Table

from upfservice.managers.upfmanager.match import Match
from upfservice.managers.upfmanager.uemaphandler import UEMapHandler
from upfservice.managers.upfmanager.matchmaphandler import MatchMapHandler
from upfservice.core.service import EService

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7777
DEFAULT_ELEMENT = "upfr"
DEFAULT_UE_SUBNET = "10.0.0.0/8"


class MatchList(list):

    def _update_index(self):

        for match in self:
            match.delete()

        new_index = 0
        for match in self:
            match.index = new_index
            match.save()
            new_index += 1

    def insert(self, index, match):

        super().insert(index, match)

        self._update_index()

    def pop(self, index: int = -1):

        self[index].delete()
        super().pop(index)

        self._update_index()

    def clear(self):

        for match in self:
            match.delete()
        super().clear()


class UPFManager(EService):
    """Service exposing the UPF function

    Parameters:
        host: click upf host (optional, default: 127.0.0.1)
        port: upf console port (optional, default: 8888)
        element: upf element (optional, default: upfr)
        ue_subnet: ue subnet (optional, default: 10.0.0.0/8)
    """

    HANDLERS = [UEMapHandler, MatchMapHandler]

    def __init__(self, context, service_id, port, host, element, ue_subnet):

        super().__init__(context=context, service_id=service_id, port=port,
                         host=host, element=element, ue_subnet=ue_subnet)

        self._prot_port_supp = {6: "tcp", 17: "udp", 132: "sctp"}
        self.matches = MatchList()

    def start(self):
        """Start UPF manager."""

        super().start()

        self._init_click_upf()
        self._init_netfilter()

        for match in Match.objects.all():
            self.add_matchmap(match.index, match)

    def _init_click_upf(self):

        while True:
            try:
                self.write_handler("matchmapclear", "0")
                break
            except:
                self.log.info("Waiting for Click UPF to start...")
                time.sleep(5)

    def _init_netfilter(self):

        self.nat_table = Table(Table.NAT)
        prerouting_chain = Chain(self.nat_table, "PREROUTING")

        for rule in prerouting_chain.rules:
            if rule.target.name == "UPF":
                prerouting_chain.delete_rule(rule)

        self.upf_chain = Chain(self.nat_table, "UPF")
        if self.upf_chain in self.nat_table.chains:
            self.upf_chain.flush()
        else:
            self.nat_table.create_chain(self.upf_chain)

        self.nat_table.refresh()

        upf_rule = Rule()
        upf_rule.src = self.ue_subnet
        upf_rule.create_target("UPF")
        prerouting_chain.insert_rule(upf_rule)

        self.nat_table.refresh()

    @property
    def uemap(self):
        """Return UE Map."""

        status, response = self.read_handler("uemap")

        if status != 200:
            raise Exception(response)

        fields = ["ue_ip", "enb_ip", "teid_downlink", "epc_ip", "teid_uplink"]
        uemap = dict()

        for ue_entry in response.split('\n'):
            if ue_entry != "":
                ue_dict = dict(zip(fields, ue_entry.split(',')))
                uemap[ue_dict["ue_ip"]] = ue_dict

        return uemap

    @property
    def matchmap(self):
        """Return matchmap."""

        self.log.debug("Getting matchmaps")
        status, response = self.read_handler("matchmap")

        if status != 200:
            raise Exception(response)

        self.log.debug("Response from upf-service is: %s" % response)

        fields = ["ip_proto_num", "dst_ip", "dst_port"]
        matchmaplist = list()

        for match_entry in response.split('\n'):
            if match_entry != "":

                matchmap_dict = dict()

                match_index, match_entry = match_entry.split(',')
                match_index = int(match_index) - 1
                matchmap_dict["index"] = match_index

                ip_proto_num, dst_ip, dst_port = match_entry.split('-')
                matchmap_dict["ip_proto_num"] = int(ip_proto_num)
                matchmap_dict["dst_port"] = int(dst_port)

                dst_ip, netmask = dst_ip.split('/')
                matchmap_dict["dst_ip"] = dst_ip
                matchmap_dict["netmask"] = int(netmask)

                self.log.debug("Looking for match_index: %s" % match_index)
                self.log.debug("UPF rules are: %s" % self.upf_chain.rules)

                rule = self.upf_chain.rules[match_index]
                new_dst = None
                new_port = 0

                if rule.target.name == "DNAT":
                    dst = rule.target.to_destination
                    if ":" in dst:
                        new_dst, new_port = dst.split(":")
                    else:
                        new_dst = dst

                matchmap_dict["new_dst_ip"] = new_dst
                matchmap_dict["new_dst_port"] = int(new_port)

                matchmap_dict["desc"] = self.matches[match_index].desc

                matchmaplist.append(matchmap_dict)

        if matchmaplist != [match.to_dict() for match in self.matches]:
            raise ValueError("Inconsistencies in the matches")

        return matchmaplist

    def add_matchmap(self, match_index, data):
        """Set matchmap."""

        if isinstance(data, Match):
            match = data
        else:
            match = Match()
            match.from_dict(match_index, data)

        if match.index not in range(0, len(self.matches) + 1):
            raise ValueError("Indexes must be within 1 and %s"
                             % (len(self.matches) + 1))

        if (match.dst_port != 0 or match.new_dst_port != 0) \
                and match.ip_proto_num not in self._prot_port_supp:
            raise ValueError("Matching protocol does not allow ports")

        status, response = self.write_handler(
            "matchmapinsert",
            "%s,%s-%s/%s-%s" % (match.index, match.ip_proto_num, match.dst_ip,
                                match.netmask, match.dst_port))

        if status != 200:
            raise Exception(response)

        if match.new_dst_ip:
            self._add_rewrite_rule(match)
        else:
            self._add_dummy_rule(match)

        self.matches.insert(match.index, match)

    def _add_rewrite_rule(self, match):

        rule = self._get_base_rule(match)

        rule.create_target("DNAT")
        rule.target.to_destination = match.new_dst_ip

        if match.new_dst_port != 0:
            rule.target.to_destination += ":%s" % match.new_dst_port

        self.log.debug("Inserting new rule: %s at index: %s" % (rule, match.index))
        self.upf_chain.insert_rule(rule, match.index)
        self.nat_table.refresh()

    def _add_dummy_rule(self, match):

        rule = self._get_base_rule(match)

        rule.create_target("ACCEPT")

        self.log.debug("Inserting new rule: %s at index: %s" % (rule, match.index))
        self.upf_chain.insert_rule(rule, match.index)
        self.nat_table.refresh()

    def _get_base_rule(self, match):

        rule = Rule()
        rule.protocol = match.ip_proto_num
        rule.dst = "%s/%s" % (match.dst_ip, match.netmask)

        if match.dst_port != 0:
            ipt_match = IPT_Match(rule,
                                  self._prot_port_supp[match.ip_proto_num])
            ipt_match.dport = str(match.dst_port)
            rule.add_match(ipt_match)

        return rule

    def del_matchmap(self, match_index):
        """Delete a match rule."""

        if match_index != -1:
            action = "matchmapdelete"
            if match_index >= 0 and match_index < len(self.upf_chain.rules):
                self.upf_chain.delete_rule(self.upf_chain.rules[match_index])
                self.matches.pop(match_index)
            else:
                raise KeyError()
        else:
            action = "matchmapclear"
            self.upf_chain.flush()
            self.matches.clear()

        status, response = self.write_handler(action, match_index)

        if status != 200:
            raise Exception(response)

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

    @property
    def host(self):
        """Return host."""

        return self.params["host"]

    @host.setter
    def host(self, value):
        """Set host."""

        if "host" in self.params and self.params["host"]:
            raise ValueError("Param host can not be changed")

        self.params["host"] = value

    @property
    def ue_subnet(self):
        """Return ue_subnet."""

        return self.params["ue_subnet"]

    @ue_subnet.setter
    def ue_subnet(self, value):
        """Set ue_subnet."""

        if "ue_subnet" in self.params and self.params["ue_subnet"]:
            raise ValueError("Param ue_subnet can not be changed")

        self.params["ue_subnet"] = value

    def write_handler(self, handler, value):
        """Write to a click handler."""

        sock = socket.socket()
        sock.connect((self.host, self.port))

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
        sock.connect((self.host, self.port))

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


def launch(context, service_id, port=DEFAULT_PORT, host=DEFAULT_HOST,
           element=DEFAULT_ELEMENT, ue_subnet=DEFAULT_UE_SUBNET):
    """ Initialize the module. """

    return UPFManager(context, service_id, port, host, element, ue_subnet)
