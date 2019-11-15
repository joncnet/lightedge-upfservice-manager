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

import tornado.web
import tornado.httpserver

from tornado.web import Application
from pymodm.errors import ValidationError

from upfservice.core.serialize import serialize
from upfservice.core.service import EService

DEBUG = True
DEFAULT_PORT = 8888
DEFAULT_WEBUI = "/var/www/upfservice/"
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

                request_body = self.request.body.decode('utf-8')
                if self.request.body and json.loads(request_body):
                    params = json.loads(request_body)

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


# pylint: disable=W0223
class IndexHandler(tornado.web.RequestHandler):
    """Index page handler."""

    # service associated to this handler
    service = None

    URLS = [r"/", r"/([a-z]*).html"]

    def get(self, args=None):
        """Render index page."""

        try:

            page = "index.html" if not args else "%s.html" % args

            self.render(page)

        except KeyError as ex:
            self.send_error(404, message=str(ex))

        except ValueError as ex:
            self.send_error(400, message=str(ex))


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

    This service exposes the UPF Service API, the 'port' parameter
    specifies on which port the HTTP server should listen.

    Parameters:
        port: the port on which the HTTP server should listen (optional,
            default: 8888)
    """

    HANDLERS = [IndexHandler]

    def __init__(self, context, service_id, webui, port):

        super().__init__(context=context, service_id=service_id, webui=webui,
                         port=port)

        self.settings = {
            "static_path": self.webui + "static/",
            "cookie_secret": COOKIE_SECRET,
            "template_path": self.webui + "templates/",
            "debug": DEBUG,
        }

        self.application = Application([], **self.settings)

        self.http_server = tornado.httpserver.HTTPServer(self.application)

    @property
    def webui(self):
        """Return path to Web UI."""

        return self.params["webui"]

    @webui.setter
    def webui(self, value):
        """Set path to Web UI."""

        if "webui" in self.params and self.params["webui"]:
            raise ValueError("Param webui can not be changed")

        self.params["webui"] = value

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


def launch(context, service_id, webui=DEFAULT_WEBUI, port=DEFAULT_PORT):
    """ Initialize the module. """

    return APIManager(context=context, service_id=service_id, webui=webui,
                      port=port)
