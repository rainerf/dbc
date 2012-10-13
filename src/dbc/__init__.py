import inspect
from functools import wraps


def _getLinesStartingWith(prefix, lines):
    for line in lines.splitlines():
        line = line.lstrip()
        if line.startswith(prefix):
            yield line[len(prefix):].strip()


class DbcViolation(Exception):
    def __init__(self, inv):
        self.inv = inv

    def __str__(self):
        return "DBC Constraint '%s' violated" % self.inv


def _dbc_function_wrapper(func, self=None):
    # we need this to work around a difference between methods and
    # functions: for functions we can store the attribute in
    # themselves, for methods we need to use their __func__ member
    # for this
    if hasattr(func, "__func__"):
        func = func.__func__

    name = func.__name__

    func.__pres__ = []
    func.__posts__ = []
    if func.func_doc:
        for line in _getLinesStartingWith("pre:", func.func_doc):
            if name == "__init__":
                raise AttributeError("__init__ must not have preconditions or postconditions")
            func.__pres__.append(line)
        for line in _getLinesStartingWith("post:", func.func_doc):
            if name == "__init__":
                raise AttributeError("__init__ must not have preconditions or postconditions")
            func.__posts__.append(line)

    @wraps(func)
    def dbc_wrapper(*args, **kwargs):

        fa = inspect.getargspec(func)[0]

        if fa[0] == "self" and len(args) == len(fa) - 1:
            args = (self,) + args
        a = dict(zip(fa, args))

        for i in func.__pres__:
            if not eval(i, globals(), a):
                raise DbcViolation(i)
        ret = func(*args, **kwargs)
        a["__ret__"] = ret
        for i in func.__posts__:
            if not eval(i, globals(), a):
                raise DbcViolation(i)
        return ret

    return dbc_wrapper


class _Dbc:
    def __init__(self):
        self.__invariants__ = []
        self.__pres__ = {}
        self.__posts__ = {}
        self.__initDbc()

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        if name in ["__invariants__", "__pres__", "__posts__"]:
            return

        for i in self.__invariants__:
            try:
                if not eval(i):
                    raise DbcViolation(i)
            except AttributeError:
                pass

    def __initDbc(self):
        # initialize invariants from all the way up the MRO
        for c in inspect.getmro(self.__class__):
            if c.__doc__:
                for line in _getLinesStartingWith("inv:", c.__doc__):
                    self.__invariants__.append(line)

        # initialize preconditions and postconditions
        for name, _ in inspect.getmembers(self, inspect.ismethod):
            if name not in ["_Dbc__initDbc", "__setattr__"]:
                setattr(self, name, _dbc_function_wrapper(getattr(self, name), self))
