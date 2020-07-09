import pydoc
import re
from collections import OrderedDict
from config import Config
from util import sub


class Template(object):
    """
    Schema template base class
    """
    _pattern = r"[\"|']?[{|<](\w+):(int|str|float|list)[}|>][\"|']?"

    def __init__(self, body):
        self.body = body

    def to_regex(self):
        """Returns template representation as normal regex"""
        raise NotImplementedError

    def substitutions(self):
        """Dictionary of values to paste in response string mapped with its types"""
        subs = re.findall(self._pattern, self.__str__())
        subs_dict = {
            sub[0]: pydoc.locate(sub[1]) for sub in subs
        }
        return subs_dict

    def get_sub_values(self, source):
        """Gets dictionary of values to paste in response string"""
        if not source:
            return {}

        r = self.to_regex()

        vals = re.findall(self.to_regex(), str(source))
        if not vals:
            return {}

        subs = self.substitutions()

        vals = vals[0] if isinstance(vals[0], tuple) else vals
        dict_vals = dict(zip(subs.keys(), vals))
        for k, v in dict_vals.items():
            type_ = subs[k]
            try:
                if type_ is list:
                    typed_v = v.strip("[]").split(", ")
                else:
                    typed_v = type_(v)
                dict_vals[k] = typed_v
            except:
                raise Exception(f"Invalid request. Can't convert \"{v}\" to type {type_}", 400)
        return dict_vals


class URLTemplate(Template):
    """
    Request URL schema template description
    """

    def __init__(self, body):
        super().__init__(body)
        self.method, self.path = body.split(" ")

    def __str__(self):
        return self.body

    def to_regex(self):
        result = re.sub(self._pattern, r"(\\w+)", self.path)
        result = f"^{result}$"
        return result


class SchemaItemTemplate(Template):
    """
    Schema item template description
    """

    def __init__(self, **kwargs):
        req = kwargs.pop("request", Config.ANY)
        super().__init__(req)
        self.body = dict(OrderedDict(sorted(req.items())))
        self.response = kwargs.pop("response")
        self.key = kwargs.pop("key", "")
        self.create_cache = kwargs.pop("create_cache", False)
        self.rule = kwargs.pop("rule", {})
        self.content_type = kwargs.pop("content_type", Config.JSON_MIME_TYPE)
        self.variables = kwargs.pop("variables", {})
        self.callback = kwargs.pop("callback", {})

    def __str__(self):
        return str(self.body)

    def substitute(self, ctx):
        """Formats request template body with current context"""
        result = {}
        for k, v in self.body.items():
            if isinstance(v, str):
                result.update({k: sub(v, **ctx)})
            else:
                result.update({k: v})
        return result

    def to_regex(self):
        return re.sub(
            self._pattern, r"[\"|']?([^\'\"]+)[\"|']?",
            self.__str__()
        )
