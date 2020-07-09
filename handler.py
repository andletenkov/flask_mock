import hashlib
import re
from collections import OrderedDict

import requests
from flask import request, Response
from templates import URLTemplate, SchemaItemTemplate
from config import Config
from util import str_to_dict, sub

# All available HTTP status codes
_CODES = (

    # Informational.
    100, 101, 102, 103, 122,
    200, 201, 202, 203, 204,
    205, 206, 207, 208, 226,

    # Redirection.
    300, 301, 302, 303, 304,
    305, 306, 307, 308,

    # Client Error.
    400, 401, 402, 403, 404,
    405, 406, 407, 408, 409,
    410, 411, 412, 413, 414,
    415, 416, 417, 418, 421,
    422, 423, 424, 425, 426,
    428, 429, 431, 444, 449,
    450, 451, 499,

    # Server Error.
    500, 501, 502, 503, 504,
    505, 506, 507, 509, 510,
    511
)


class RequestHandler(object):
    """
    Handles incoming HTTP requests
    """

    def __init__(self, file: dict):
        self.schema = file
        self._cache = None
        self._req_handled = False
        self.method = None
        self.path = None
        self.data = None
        self.url_template = None
        self.template = None
        self.global_ctx = {}

    @property
    def request_context(self):
        """Returns dict containing request object context variables"""
        ctx_vars = [v for v in request.__dir__() if not v.startswith("_") and "json" not in v]
        ctx_dct = {attr.upper(): getattr(request, attr) for attr in ctx_vars if isinstance(getattr(request, attr), str)}
        return ctx_dct

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        self._cache = value

    @property
    def req_handled(self):
        return self._req_handled

    @req_handled.setter
    def req_handled(self, value):
        self._req_handled = value

    @staticmethod
    def get_request_data():
        try:
            json_data = str_to_dict(request.data.decode()) if request.data else {}
            all_data = {
                **json_data,
                **dict(request.args),
                **dict(request.form)
            }
            return dict(OrderedDict(sorted(all_data.items())))
        except:
            raise Exception("Invalid request data format", 500)

    def handle(self):
        """Parses request object to internal fields"""
        self.method = request.method

        path = request.path[request.path.find("/", 1):]
        self.path = path[:-1] if path.endswith("/") and len(path) > 1 else path
        self.data = self.get_request_data()
        self.url_template = self._find_url_template()
        self.template = self._find_suited_item()
        self.global_ctx = self._build_ctx()
        self._update_ctx()
        self._req_handled = True

    def _update_ctx(self):
        pass

    def _find_url_template(self):
        templates = [URLTemplate(k) for k in self.schema.keys()]

        # find direct occurrences
        filtered = list(filter(
            lambda it: it.method.lower() == self.method.lower() and
                       it.path == self.path, templates
        ))
        if filtered:
            return next(iter(filtered))

        # check regex matching
        filtered = list(filter(
            lambda it: re.match(it.to_regex(), self.path), templates
        ))
        if filtered:
            return next(iter(filtered))

        raise Exception(f"Request '{self.path}' doesn't match any endpoint in schema")

    def _find_suited_item(self):
        if not self.url_template:
            raise Exception("URL template is not set", 500)

        items = self.schema.get(str(self.url_template))
        try:
            templates = [(SchemaItemTemplate(**item)) for item in items]
        except:
            raise Exception(f"Invalid structure for URL template: {self.url_template}", 500)

        # find direct occurrences
        filtered = list(filter(
            lambda r: r.body == Config.ANY or r.substitute(self.request_context) == self.data, templates
        ))
        if filtered:
            return next(iter(filtered))

        # check regex matching
        filtered = list(filter(
            lambda r: re.match(r.to_regex(), str(self.data)), templates
        ))
        if filtered:
            return next(iter(filtered))

        raise Exception(
            f"Request {self.method} {self.path} with data '{self.data}' doesn't match any endpoint in schema"
        )

    def _build_ctx(self):

        ctx = {
            **self.template.get_sub_values(self.data),
            **self.url_template.get_sub_values(self.path),
            **self.template.variables
        }

        cache_data = None

        if self.template.key:
            if self.template.create_cache:
                self.cache.add_new(self.template.key, ctx)
            else:
                if self.template.rule:
                    rules = {k: sub(v, **ctx) for k, v in self.template.rule.items()}
                    cache_data = self.cache.find(self.template.key, **rules)

        if cache_data:
            ctx.update(cache_data)
        return ctx

    def build_response(self):
        """Renders response template with substitutions"""
        if not self.req_handled:
            raise Exception(f"{self.__class__} doesn't handle any request")

        if isinstance(self.template.response, list):
            try:
                status, body = self.template.response
            except ValueError as e:
                raise Exception(f"Invalid response template: {e}", 500)

            if status not in _CODES:
                raise Exception(f"Invalid status code in template: {status}", 500)

        else:
            status, body = 200, self.template.response

        self._callback(**self.global_ctx, **self.request_context)
        resp = sub(body, **self.global_ctx, **self.request_context)

        return Response(resp, mimetype=self.template.content_type), status

    def _callback(self, **data):
        cb = self.template.callback
        if not cb:
            return

        callback_url = sub(cb.get("url"), **data)

        try:
            getattr(requests, cb.get("method", "").lower())(
                url=callback_url,
                data=sub(cb.get("data"), **data),
                headers=cb.get("headers", {})
            )
        except:
            raise Exception(f"Can't send callback to \"{callback_url}\"", 500)


class ExampleRequestHandler(RequestHandler):
    """
    Implement your own request handler if needed
    """

    def _update_ctx(self):
        print("overriden method!")
