import threading
import inspect
import json
import textwrap
import functools
from misctypes import DateTime

def transform_value(target_type, inval):
    """Given a type and a value, create an object of the type from the value

    :param target_type: a type or a list/tuple containing a type as its
        only element; in the latter case, the input value is assumed to be
        iterable, and the output value will be a list of the transformed
        elements in the iterable
    :type target_type: type or [type] or (type,)
    :param inval: input value that can be passed to the type constructor;
        if ``target_type`` is a list or tuple, ``inval`` must be an iterable
    :raises TypeError: if the input value cannot be transformed
    """

    try:
        if isinstance(target_type, (list,tuple)):
            outval = []
            if inval is None:
                return outval
            if not isinstance(inval, (list,tuple)):
                target_type = list
                raise TypeError()
            target_type = target_type[0]
            inlist = inval
            for inval in inlist:
                outval.append(target_type(inval))
        elif inval is None:
            outval = None
        else:
            outval = target_type(inval)
    except Exception:
        m = "Cannot transform {0} to {1}".format(inval.__class__.__name__,
                                                 target_type.__name__)
        raise TypeError(m)
    return outval

class ParmDescException(Exception):
    pass

class ParmDescAware():
    """Base class for classes that use pre-defined parameter descriptions
    
    Allow classes to describe types, documentation, and function call details
    for parameters that are typically passed as dictionaries. The
    ParmDescAware class can be used to simplify parameter filtering,
    conversion, and documentation using the DRY (Don't Repeat Yourself)
    philosophy.

    If a subclass uses multiple inheritance, it should specify this
    superclass before any others. If a subclass defines a ``__new__`` method,
    that method should call ``ParmDescAware.__new__()``.
    """

    _lock = threading.Lock()
    
    #: Dictionary that maps AMIE parameters to their type. All ParmDescAware
    #: subclasses will see these parameters in addition to their own
    parm2type = {}

    #: Dictionary that maps AMIE parameters to their docstring. All
    #: ParmDescAware subclasses will see these parameters in addition
    #: to their own
    parm2doc = {}

    #: Default docstring for parameters that do not have entries in parm2doc
    default_parm_doc = '(Unknown)'

    #: Dictionary that maps module.class.function names to subdictionaries
    #: containing ``allowed``, ``required``, and ``class`` entries:
    #: ``allowed`` is a list of allowed parameter names, ``required`` is
    #: a list of required parameters, and ``class`` is the class where the
    #: function is defined. See the ``process_parms()``` decorator function.
    function_info = {}


    def __init_subclass__(cls, **kwargs):
        """Do some 'magic' after a subclass definition is processed

        This method runs automatically after the subclass defines
        its attributes and functions.

        If the subclass defines defaults for ``parm2type`` or ``parm2doc``,
        ``ParmDescAware`` will use them to initialize its own ``parm2type``
        and ``parm2doc`` dictionaries.

        ``ParmDescAware`` ensures that the subclass has its own ``parm2type``
        and ``parm2doc`` class attributes defined, and supplements them with
        the values in its own dictinoaries.

        If a subclass defines some set of methods using the `@process_parms`
        decorator (which takes ``allowed`` and ``required`` parameters lists),
        ``ParmDescAware`` supplements the docstrings of these methods using
        ``parm2doc`` data, and adds a ``class`` entry to the ``function_info``
        map that is initialized by ``process_parms()``.
        """
        
        super().__init_subclass__(**kwargs)
        with ParmDescAware._lock:
            ParmDescAware._initialize_defaults_in_ParmDescAware(cls)
            cls._apply_defaults_to_subclass()
            cls._update_function_info()

    def _initialize_defaults_in_ParmDescAware(cls):
        if not ParmDescAware.parm2type and hasattr(cls,'default_parm2type'):
            ParmDescAware.parm2type.update(cls.default_parm2type)
        if not ParmDescAware.parm2doc and hasattr(cls,'default_parm2doc'):
            ParmDescAware.parm2doc.update(cls.default_parm2doc)
        if not ParmDescAware.default_parm_doc == '(Unknown)' and \
           hasattr(cls,'default_default_parm_doc'):
            ParmDescAware.default_parm_doc = cls.default_parm2doc

    @classmethod
    def _apply_defaults_to_subclass(cls):
        if not hasattr(cls,'parm2doc'):
            cls.parm2doc = []
        if not hasattr(cls,'parm2type'):
            cls.parm2type = []

        for key in ParmDescAware.parm2type:
            if key not in cls.parm2type:
                cls.parm2type[key] = ParmDescAware.parm2type[key]
            if key not in cls.parm2doc:
                if key in ParmDescAware.parm2doc:
                    cls.parm2doc[key] = ParmDescAware.parm2doc[key] 
                else:
                    cls.parm2doc[key] = ParmDescAware.default_parm_doc
        return

    @classmethod
    def _update_function_info(cls):
        members = inspect.getmembers(cls)
        for k, v in members:
            if v.__class__.__name__ == 'function':
                info_key = cls.__module__ + '.' + cls.__name__ + '.' + k
                if info_key in ParmDescAware.function_info:
                    func_info = ParmDescAware.function_info[info_key]
                    func_info['class'] = cls
                    cls._validate_function_parms(func_info)
                    cls._add_function_attributes(func_info,v)
                    cls._build_function_docstring(func_info,v)
        return

    @classmethod
    def _validate_function_parms(cls,func_info):
        clsparms = cls.parm2type
        invalid = []
        allowed = set(func_info['allowed'])
        for parm in allowed:
            if parm not in clsparms:
                invalid.append(parm)
        if invalid:
            msg = "process_parms() given undefined parms: " + ", ".join(invalid)
            raise ParmDescException(msg)
        for parm in func_info['required']:
            if isinstance(parm,list):
                for subparm in parm:
                    if subparm not in allowed:
                        invalid.append(subparm)
            else:
                if parm not in allowed:
                    invalid.append(parm)
        if invalid:
            msg = "process_parms() given unallowed required parms: " + ", ".join(invalid)
            raise ParmDescException(msg)
        return

    @classmethod
    def _add_function_attributes(cls, func_info, func):
        allowed = func_info['allowed']
        if not allowed:
            return

        func.func_info = func_info

    @classmethod
    def _build_function_docstring(cls, func_info, func):
        allowed = func_info['allowed']
        if not allowed:
            return

        required = func_info['required']
        required_map = cls._build_required_map(allowed,required)

        if hasattr(func,'__doc__'):
            docstr = getattr(func,'__doc__')
        else:
            docstr = inspect.getcomments(func)

        doclines = [] if docstr is None else docstr.strip().split("\n")
        indent = cls._get_indent(doclines)
        leading, trailing = cls._find_new_param_location(doclines)

        parm_doclines = ['']
        for parm in allowed:
            parm_doclines.extend(cls._build_parm_desc_lines(required_map,parm))
            parm_doclines.extend(cls._build_parm_type_lines(required_map,parm))

        sep = "\n" + indent
        parmdoc = sep.join(parm_doclines)
        new_docstr = leading + parmdoc[1:] + "\n" + trailing
        func.__doc__ = new_docstr
#        setattr(func,'__doc__',new_docstr)

    def _find_new_param_location(doclines):
        # split docstring at the point where new :param entries should be added

        leading_doclines = []

        add_blank_to_lead = False
        while doclines:
            line = doclines[0]
            stripped = line.lstrip()
                
            if stripped.startswith(':param'):
                add_blank_to_lead = False
            elif stripped.startswith(':'):
                break
            else:
                add_blank_to_lead = (stripped != '')
            leading_doclines.append(doclines.pop(0))
            
        if add_blank_to_lead:
            leading_doclines.append('')

        leading_doclines.append('')
        return "\n".join(leading_doclines), "\n".join(doclines)

    def _get_indent(doclines):
        # Note that the first line in doclines will not have initial whitespace.
        nlines = len(doclines)
        for i in range(1,nlines):
            line = doclines[i]
            if line.strip() == "":
                continue
            if line.startswith(" "):
                stripped = line.lstrip()
                indentlen = len(line) - len(stripped)
                return ' ' * indentlen
        return "    "
        
        
    def _build_required_map(allowed,required) -> dict:
        # map parmname to True if parm is required, False if it is optional,
        # or string describing when it is required
        required_map = {}
        for required_parm in required:
            if isinstance(required_parm,list):
                for parm in required_parm:
                    remaining = required_parm.copy()
                    remaining.remove(parm)
                    required_map[parm] = "Required if " + \
                        "'" + "', '".join(remaining) + "'" + \
                        " not present"
            else:
                required_map[required_parm] = True
        for parm in allowed:
            if parm not in required_map:
                required_map[parm] = False
        return required_map

    @classmethod
    def _get_parm_type(cls, parm):
        if parm in cls.parm2type:
            return cls.parm2type[parm]
        raise ParmDescException("type of '" + parm + "' unknown")

    @classmethod
    def _get_parm_doc(cls, parm):
        if parm in cls.parm2doc:
            return cls.parm2doc[parm]
        raise ParmDescException("'" + parm + "' unknown")

    @classmethod
    def _build_parm_desc_lines(cls, required_map, parm):
        req =  required_map[parm]
        reqmsg = " (" + req + ")" if isinstance(req, str) else ''
        desc = ":param " + parm + ": " + cls._get_parm_doc(parm) + reqmsg
        return textwrap.wrap(desc, initial_indent='', subsequent_indent='    ')

    @classmethod
    def _build_parm_type_lines(cls, required_map, parm):
        req =  required_map[parm]
        optmsg = ", optional" if isinstance(req, bool) and not req else ''
        parm_type = cls._get_parm_type(parm)
        if isinstance(parm_type, (list,tuple)):
            parm_type = parm_type[0]
            typestr = "list of " + parm_type.__name__
        else:
            typestr = parm_type.__name__
        typedesc = ":type " + parm + ": " + typestr + optmsg
        return textwrap.wrap(typedesc, initial_indent='', subsequent_indent='    ')


def process_parms(allowed,required):
    """Decorator function that specifies allowed and required parms

    This can only be used on methods defined in a ``ParmDescAware`` subclass.
    The decorated methods must have arguments ``(self, *args, **kwargs)``.

    When the decorated function is called, the wrapper automatically
    calls ``transform_args()`` and passes the resulting dictionary to
    the decorated function as ``**kwargs``.

    :param allowed: List of allowed parameters; these must all be defined in
        the class' ``parm2type`` attribute
    :type allowed: list
    :param required: List of required parameters; these must all be defined in
        the class' ``parm2type`` attribute. Entries can be parmeter names or
        lists of parameter names: if an entry is a list, at least one of the
        names in the list must be given
    :type required: list
    """
    
    if isinstance(allowed,str):
        allowed = [ allowed ]
    elif not isinstance(allowed,list):
        msg = "process_parms requires 'allowed' list or string argument"
        raise ParmDescException(msg)
    if isinstance(required,str):
        required = [required ]
    elif not isinstance(required,list):
        msg = "process_parms 'required' argument must be a list or string"
        raise ParmDescException(msg)

    def inner(func):
        info_key = func.__module__ + "." + func.__qualname__
        func_info = {
            'allowed': allowed,
            'required': required,
            }
        with ParmDescAware._lock:
            ParmDescAware.function_info[info_key] = func_info
            
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if 'class' not in func_info:
                raise ParmDescException("@process_parms can only be used on" + \
                                        " methods in ParmDescAware subclasses")
            cls = func_info['class']
            new_args = transform_args(cls.__name__,cls.parm2type,func_info['allowed'],
                                      func_info['required'],
                                      *args, **kwargs);
            func(self, **new_args)

        return wrapper
    return inner

def transform_args(cls: str, parm2type: dict, allowed: list, required: list,
                   *args, **kwargs) -> dict:
    """Filter/validate/transform function arguments
        
    This is a helper function that validates , filters, and transforms
    parameters. It can be called directly, but is designed to be internally
    by the process_parms() decorator function.

    :param parm2type: Dictionary that maps parameter names to types
    :type parm2type: dict
    :param allowed: List of allowed parameters names
    :type allowed: list
    :param required: List of required parameters names or sublists of
        parameter names; a sublist implies that at least one of the
        parameters in the sublist is required
    :type required: list
    :param \**kwargs: All other arguments are keyword arguments, which will
        be filtered according to the ``allowed`` list, validated against the
        ``required`` list, and transformed using the ``parm2type`` map.
    :type \**kwargs: dict
        Name of the function whose parameters are being validated
    :raises JSONDecodeError: if a string argument is given that is not a
        decodeable JSON string
    :raises KeyError: if a required key is missing or cannot be transformed
    :raises TypeError: if a value cannot be transformed according to
        the ``parm2type`` map, or the ``arg`` value is not, or cannot be
        decoded into, a dictionary
    :return: A dictionary containing a subset of ``allowed`` keys, all
        ``required`` keys, and nothing else. All values types will be
        consistent with the ``attr2type`` map.
    :rtype: dict
    """

    if args:
        arg = args[0]
        if isinstance(arg,str):
            in_dict = json.loads(arg)
            if not isinstance(in_dict, dict):
                msg = 'JSON string argument does not decode to a dictionary'
                raise TypeError(msg)
        elif isinstance(arg, dict):
            in_dict = arg
        else:
            raise TypeError('Argument is not a dict or str')
    else:
        in_dict = kwargs

    out_dict = {}
    for key in allowed:
        if key in parm2type:
            t = parm2type[key]
            if key in in_dict:
                try:
                    out_dict[key] = transform_value(t,in_dict[key])
                except TypeError as err:
                    msg = cls + '.' + key + ": " + str(err)
                    raise TypeError(msg)
    missing = []
    for key in required:
        if isinstance(key,list):
            present = False
            for rkey in key:
                if in_dict.get(rkey) is not None:
                    present = True
                    break
            if not present:
                missing.append(' or '.join(key))
        else:
            if in_dict.get(key) is None:
                missing.append(key)
                
    if missing:
        raise KeyError(cls + ": Missing required parameters: " + ','.join(missing))
            
    return out_dict

