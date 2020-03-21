import ast
import string


def str_to_dict(s):
    """Converts string to dictionary"""
    if s.startswith("{") and s.endswith("}"):
        return ast.literal_eval(s)
    else:
        return ast.literal_eval("{" + s + "}")


def sub(str_, **values):
    """Formats given string template with specified values"""
    return string.Template(str_).safe_substitute(**values)