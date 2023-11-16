from QPSLClass.Base import *
from ..Hooks import *


class QPSLObjectBase(QObject):
    add_log = QPSLLogger()
    add_debug = QPSLLogger(QPSL_LOG_LEVEL.DBG.value)
    add_info = QPSLLogger(QPSL_LOG_LEVEL.INF.value)
    add_warning = QPSLLogger(QPSL_LOG_LEVEL.WARN.value)
    add_error = QPSLLogger(QPSL_LOG_LEVEL.ERR.value)
    add_critical = QPSLLogger(QPSL_LOG_LEVEL.CRT.value)
    action_dict = ActionManager()
    is_virtual = VirtualManager()

    @classmethod
    def from_json(cls, json: Dict):
        _class = get_registered_class(json.get("Type"))
        res: QPSLObjectBase = _class()
        res.load_by_json(json)
        return res

    def load_by_json(self, json: Dict):
        if "ObjectName" in json:
            self.setObjectName(json.get("ObjectName"))

    def to_json(self):
        res = dict()
        res.update({"Type": self.__class__.__name__})
        if self.objectName():
            res.update({"ObjectName": self.objectName()})
        return res

    def qpsl_parent(self):
        parent = self.parent()
        while parent is not None and not isinstance(parent, QPSLObjectBase):
            parent = parent.parent()
        return parent

    def __init__(self):
        super().__init__()

    def __init_subclass__(cls):
        register_class(cls=cls)

    def load_attr(self):
        return self

    def to_delete(self):
        pass

    def trace_path_up(self) -> Iterable[QObject]:
        w = self
        while w is not None:
            yield w
            w = self.parent()

    def trace_path_up_with_filter(self) -> Iterable['QPSLObjectBase']:
        w = self
        while w is not None:
            if isinstance(w, QPSLObjectBase):
                yield w
            w = self.parent()

    def remove_type(self) -> Any:
        return self

    def log_decorator(level=QPSL_LOG_LEVEL.DBG.value,
                      error_level=QPSL_LOG_LEVEL.ERR.value):

        def inner_wrap(func):
            para_count = get_function_para_count(func=func)

            def wrapped_func(self: QPSLObjectBase, *args, **kwargs):
                try:
                    if para_count > 1:
                        msg = "->into {0}.{1} ,args: {2} ...".format(
                            self.__class__.__name__,
                            get_function_name(func=func), ','.join(
                                map(
                                    lambda z: "{0} = {1}".format(
                                        z[0], simple_str(z[1])),
                                    itertools.chain(
                                        zip(
                                            get_function_para_names(
                                                func=func)[1:], args),
                                        kwargs.items()))))
                    else:
                        msg = "->into {0}.{1} ...".format(
                            self.__class__.__name__,
                            get_function_name(func=func))
                    self.add_log(msg=msg, level=level)
                    return func(self, *args, **kwargs)
                except BaseException as e:
                    self.add_log(msg=e,
                                 level=error_level,
                                 exc_info=True,
                                 stack_info=True)
                finally:
                    msg = "exit {0}.{1}".format(self.__class__.__name__,
                                                get_function_name(func=func))
                    self.add_log(msg=msg, level=level)

            wrapped_func.__name__ = func.__name__
            return wrapped_func

        return inner_wrap
