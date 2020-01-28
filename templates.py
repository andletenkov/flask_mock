import pydoc
import re
from collections import OrderedDict


class Template(object):
    """
    Schema template base class
    """

    def __init__(self, body):
        self.body = body
        self._pattern = r"[\"|']?[{|<](\w+):(int|str)[}|>][\"|']?"

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
        vals = re.findall(self.to_regex(), str(source))
        vals = vals[0] if isinstance(vals[0], tuple) else vals
        dict_vals = dict(zip(self.substitutions().keys(), vals))
        for k, v in dict_vals.items():
            type_ = self.substitutions()[k]
            try:
                typed_v = type_(v)
                # typed_v = typed_v if isinstance(typed_v, int) else typed_v[1:-1]
                dict_vals[k] = typed_v
            except:
                raise Exception(f"Can't convert {v} to type {type_}")
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
        if result.endswith("(\\w+)"):
            result += "$"
        result = "^" + result
        return result


class RequestTemplate(Template):
    """
    Request body schema template description
    """

    def __init__(self, body):
        super().__init__(body)
        self.body = dict(OrderedDict(sorted(body.items())))

    def __str__(self):
        return str(self.body)

    def to_regex(self):
        return re.sub(self._pattern, r"[\"|']?([a-zA-Z0-9_@.\s]+)[\"|']?", self.__str__())
