import ast
import json
import re
import string
from collections import OrderedDict
from flask import jsonify
from templates import URLTemplate, RequestTemplate


class RequestHandler(object):
    """
    Handles incoming HTTP requests
    """

    def __init__(self, file: dict, ):
        self.schema = file
        self._req_handled = False
        self.method = None
        self.path = None
        self.data = None
        self._url_template = None
        self._request_template = None
        self._response_template = None

    @staticmethod
    def str_to_dict(s):
        """Converts string to dictionary"""
        if s.startswith("{") and s.endswith("}"):
            return ast.literal_eval(s)
        else:
            return ast.literal_eval("{" + s + "}")

    def handle(self, request):
        """Parses request object to internal fields"""
        self.method = request.method
        self.path = request.path[request.path.find("/", 1):]
        try:
            json_data = self.str_to_dict(request.data.decode()) if request.data else {}
            self.data = dict(OrderedDict(sorted(json_data.items())))
        except:
            raise Exception("Invalid request data format", 500)

        self._url_template = self._find_url_template()
        self._request_template, self._response_template = self._find_request_template()
        self._req_handled = True

    @property
    def req_handled(self):
        return self._req_handled

    @property
    def url_template(self):
        return self._url_template

    @property
    def request_template(self):
        return self._request_template

    @property
    def response_template(self):
        return self._response_template

    def _find_url_template(self):
        for e in self.schema.keys():
            template = URLTemplate(e)

            if not self.method.lower() == template.method.lower():
                continue

            if template.path == self.path:
                return template

            regex = template.to_regex()
            if re.match(regex, self.path):
                return template

        raise Exception(f"Request '{self.path}' doesn't match any endpoint in schema")

    def _find_request_template(self):
        items = self.schema.get(str(self.url_template))

        for n in range(2):
            for item in items:
                req = RequestTemplate(item.get("request", {}))
                resp = item.get("response")

                if not n:
                    if req.body == self.data:
                        return req, resp
                else:
                    regex = req.to_regex()
                    if re.match(regex, str(self.data)):
                        return req, resp

        raise Exception(f"Request with body '{self.data}' doesn't match any endpoint in schema")

    def build_response(self):
        """Renders response template with substitutions"""
        if not self.req_handled:
            raise Exception(f"{self.__class__} doesn't handle any request")

        subs = dict()
        subs.update(self.request_template.get_sub_values(self.data))
        subs.update(self.url_template.get_sub_values(self.path))

        resp = string.Template(self.response_template).safe_substitute(**subs)
        try:
            json_resp = self.str_to_dict(resp)
        except:
            return resp
        return jsonify(json_resp)
