from typing import List
from PyQt5.QtWidgets import QDockWidget

__QPSL_opened_plugins: List[QDockWidget] = []


def auto_generate_plugin_name(cls_name):
    id = 0
    while any(w.windowTitle() == "%s_%d" % (cls_name, id)
              for w in __QPSL_opened_plugins):
        id += 1
    return "%s_%d" % (cls_name, id)


def get_opened_plugins():
    yield from __QPSL_opened_plugins


def add_opened_plugins(plugin):
    __QPSL_opened_plugins.append(plugin)


def remove_opened_plugins(plugin):
    __QPSL_opened_plugins.remove(plugin)