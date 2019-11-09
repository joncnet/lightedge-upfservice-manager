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

"""API Manager (REST Northbound Interface)."""

import json
import os

import tornado.web
import tornado.httpserver

from tornado.web import Application
from pymodm.errors import ValidationError

from upfservice.core.serialize import serialize
from upfservice.core.service import EService

DIRNAME = os.path.dirname(__file__)
ROOT_PATH = os.path.normpath(os.path.join(DIRNAME, '..'))
TEMPLATE_PATH = os.path.join(DIRNAME, 'templates')
STATIC_PATH = os.path.join(DIRNAME, 'static')
DEBUG = True
DEFAULT_PORT = 8888
COOKIE_SECRET = b'xyRTvZpRSUyk8/9/McQAvsQPB4Rqv0w9mBtIpH9lf1o='


def validate(returncode=200, min_args=0, max_args=0):
    """Validate REST method."""

    def decorator(func):

        def magic(self, *args):

            try:

                if len(args) < min_args or len(args) > max_args:
                    msg = "Invalid url (%u, %u)" % (min_args, max_args)
                    raise ValueError(msg)

                params = {}

                if self.request.body and json.loads(self.request.body):
                    params = json.loads(self.request.body)

                if "version" in params:
                    del params["version"]

                output = func(self, *args, **params)

                if returncode == 200:
                    self.write_as_json(output)

            except KeyError as ex:
                self.send_error(404, message=str(ex))

            except ValueError as ex:
                self.send_error(400, message=str(ex))

            except AttributeError as ex:
                self.send_error(400, message=str(ex))

            except TypeError as ex:
                self.send_error(400, message=str(ex))

            except ValidationError as ex:
                self.send_error(400, message=str(ex))

            self.set_status(returncode, None)

        magic.__doc__ = func.__doc__

        return magic

    return decorator


class IndexHandler(tornado.web.RequestHandler):
    """Index page handler."""

    # service associated to this handler
    service = None

    URLS = [r"/", r"/index.html"]

    @tornado.web.authenticated
    def get(self):
        """Render index page."""

        username = self.get_secure_cookie("username").decode('UTF-8')

        account = self.service.accounts_manager.accounts[username]

        self.render("index.html",
                    username=username,
                    password=account.password,
                    name=account.name,
                    email=account.email)


class UPFServiceAPIHandler(tornado.web.RequestHandler):
    """Base class for all the REST calls."""

    # service associated to this handler
    service = None

    def write_error(self, status_code, **kwargs):
        """Write error as JSON message."""

        self.set_header('Content-Type', 'application/json')

        out = {
            "title": self._reason,
            "status_code": status_code,
            "detail": kwargs.get("message"),
        }

        self.finish(json.dumps(out))

    def write_as_json(self, value):
        """Return reply as a json document."""

        self.write(json.dumps(serialize(value), indent=4))

    def prepare(self):
        """Prepare to handler reply."""

        self.set_header('Content-Type', 'application/json')


class APIManager(EService):
    """Service exposing the UPF Service REST API

    This service exposes the UPF Service REST API, the 'port' parameter
    specifies on which port the HTTP server should listen.

    Parameters:
        port: the port on which the HTTP server should listen (optional,
            default: 8888)
    """

    HANDLERS = [IndexHandler]

    def __init__(self, context, service_id, port=DEFAULT_PORT):

        super().__init__(context=context, service_id=service_id, port=port)

        self.settings = {
            "static_path": STATIC_PATH,
            "cookie_secret": COOKIE_SECRET,
            "template_path": TEMPLATE_PATH,
            "debug": DEBUG,
        }

        self.application = Application([], **self.settings)

        self.http_server = tornado.httpserver.HTTPServer(self.application)

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

    def start(self):
        """Start api manager."""

        super().start()

        self.http_server.listen(self.port)

        self.log.info("Listening on port %u", self.port)

        self.http_server.start()

    def register_handler(self, handler):
        """Add a new handler class."""

        for url in handler.URLS:
            self.log.info("Registering URL: %s", url)
            self.application.add_handlers(r".*$", [(url, handler)])
