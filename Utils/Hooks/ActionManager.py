from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union
from weakref import WeakKeyDictionary
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QMenu
from .InitConfig import SingleChoiceBox, SingleChoicePopBox, ToggleBox


class ActionManager:

    def __set_name__(self, cls: type, name: str):
        self.m_data: Dict[QObject, Dict[
            str, Union[QAction, QMenu, SingleChoiceBox,
                       SingleChoicePopBox]]] = WeakKeyDictionary()

    def __get__(self, obj: Optional[QObject], cls: type):
        if obj not in self.m_data:
            self.m_data[obj] = dict()
        return self.m_data[obj]


__QPSL_Global_Settings: Dict[str, Union[QAction, QMenu, SingleChoiceBox,
                                        SingleChoicePopBox]] = dict()


def get_global_settings():
    return __QPSL_Global_Settings


def add_global_single_choice_box(box: SingleChoiceBox):
    __QPSL_Global_Settings.update({box.get_name(): box})


def add_global_single_choice_popbox(box: SingleChoicePopBox):
    __QPSL_Global_Settings.update({box.get_name(): box})


def add_global_toggle_box(box: ToggleBox):
    __QPSL_Global_Settings.update({box.get_name(): box})


def add_global_action(act: QAction):
    __QPSL_Global_Settings.update({act.text(): act})


def add_global_menu(menu: QMenu):
    __QPSL_Global_Settings.update({menu.title(): menu})


def action_attach_to_menu(act: Union[QAction, QMenu, SingleChoiceBox,
                                     SingleChoicePopBox, ToggleBox],
                          menu: QMenu):
    if isinstance(act, QAction):
        menu.addAction(act)
    elif isinstance(act, QMenu):
        menu.addMenu(act)
    elif isinstance(act, SingleChoiceBox):
        act.attach_to(menu=menu)
    elif isinstance(act, SingleChoicePopBox):
        act.attach_to(menu=menu)
    elif isinstance(act, ToggleBox):
        act.attach_to(menu=menu)
    else:
        exit(-1)