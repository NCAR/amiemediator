from abc import ABC, abstractmethod
import pprint
import re
import xml.etree.ElementTree as ET

_re_obj = re.compile('^<[^ ]+ object at 0x[0-9a-f]+>$')
_pp = pprint.PrettyPrinter(indent=2)

class Prettifiable(ABC):
    @abstractmethod
    def pformat(self):
        pass

    def vpformat(self):
        self.pformat()

def truthy(val):
    if val is None:
        return False
    elif type(val) is str:
        lval = val.lower()
        if lval == "" or lval == "0" or \
           lval == "false" or lval == "f" or \
           lval == "no" or lval == "n":
            return False
        return True
    else:
        b = True if val else False
        return b

def pformat(arg, **kwargs):
    return _pp.pformat(arg,kwargs)

def to_expanded_string(val):
    if val is None:
        return '(None)'
    elif isinstance(val,str):
        return _format_if_XML_or_return(val)
    elif isinstance(val,(float, int, bool)):
        return str(val)
    elif isinstance(val,Prettifiable):
        valdump = val.pformat()
    else:
        valdump = _pp.pformat(val)
        if _re_obj.match(valdump):
            valdump = valdump + ":\n" + _pp.pformat(vars(val))
            
    return valdump

def _format_if_XML_or_return(val):
    if val[0:1] == '<' and val[-1] == '>':
        try:
            t = ET.XML(val)
            ET.indent(t)
            xmlstr = ET.tostring(t, encoding='unicode')
            return xmlstr
        except ET.ParseError:
            pass
    return val


