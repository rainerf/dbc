from __future__ import print_function
import inspect
from functools import wraps
import copy


def __getLinesStartingWith(prefix, lines):
    for line in lines.splitlines():
        line = line.lstrip()
        if line.startswith(prefix):
            yield line[len(prefix):].strip()


class DbcViolation(Exception):
    def __init__(self, con):
        self.con = con

    def __str__(self):
        return "DBC Constraint '%s' violated" % self.con


def dbc_function(func, self=None, additional=None):
    if additional is None:
        additional = []

    # we need this to work around a difference between methods and
    # functions: for functions we can store the attribute in
    # themselves, for methods we need to use their __func__ member
    # for this
    if hasattr(func, "__func__"):
        func = func.__func__

    name = func.__name__

    func.__pres__ = copy.copy(additional)
    func.__posts__ = copy.copy(additional)
    if func.func_doc:
        for line in __getLinesStartingWith("pre:", func.func_doc):
            if name == "__init__":
                raise AttributeError("__init__ must not have preconditions or postconditions")
            func.__pres__.append(line)
        for line in __getLinesStartingWith("post:", func.func_doc):
            if name == "__init__":
                raise AttributeError("__init__ must not have preconditions or postconditions")
            func.__posts__.append(line)

    @wraps(func)
    def dbc_wrapper(*args, **kwargs):
        def __check(conds, a):
            for i in conds:
                # we're working around a limitation of eval here: if a list
                # comprehension is used in eval(...), the variables referenced
                # inside need to be global, local variables are not found;
                # therefore, present all values as globals
                if not eval(i, a):
                    raise DbcViolation(i)

        fa = inspect.getargspec(func)[0]

        if fa[0] == "self" and len(args) == len(fa) - 1:
            args = (self,) + args
        a = dict(zip(fa, args))

        __check(func.__pres__, a)
        old = {k: copy.copy(v) for k, v in a.items()}
        ret = func(*args, **kwargs)
        a["__ret__"] = ret
        a["__old__"] = old
        __check(func.__posts__, a)
        return ret

    return dbc_wrapper


def dbc_class(cls):
    ####
    # define and set the new __setattr__
    def __setattr__(self, name, value):
        self.__dict__[name] = value

        if name in ["__invariants__", "__init__", "__init_dbc__"]:
            return

        for i in self.__invariants__:
            try:
                if not eval(i):
                    raise DbcViolation(i)
            except AttributeError:
                pass
    cls.__setattr__ = __setattr__

    ####
    # define and set the new __init_dbc__
    def __init_dbc__(self):
        soft_invariants = []
        # initialize invariants from all the way up the MRO
        for c in inspect.getmro(self.__class__):
            if c.__doc__:
                for line in __getLinesStartingWith("hinv:", c.__doc__):
                    self.__invariants__.append(line)
                for line in __getLinesStartingWith("sinv:", c.__doc__):
                    soft_invariants.append(line)

        # initialize preconditions and postconditions
        for name, _ in inspect.getmembers(self, inspect.ismethod):
            if name != "__setattr__":
                setattr(self, name, dbc_function(getattr(self, name), self, soft_invariants))
    cls.__init_dbc__ = __init_dbc__

    ####
    # define and set the new __init__
    orig__init__ = cls.__init__

    @wraps(orig__init__, assigned=("__name__", "__doc__"))
    def __init__(self, *args, **kwargs):
        self.__invariants__ = []
        self.__init_dbc__()
        orig__init__(self, *args, **kwargs)
    cls.__init__ = __init__

    ####
    # done, return the modified class
    return cls
