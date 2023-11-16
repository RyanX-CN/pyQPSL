import json
import os
from typing import Callable, Iterable, Optional, Tuple
import weakref
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QListWidget, QMenu, QPushButton, QStyleFactory, QVBoxLayout

# 使用绝对路径，避免从其他路径执行
QPSL_Working_Directory = os.path.split(
    os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])[0].replace(
        '\\', '/')
QPSL_Temp_Directory = os.path.join(QPSL_Working_Directory,
                                   "Temp").replace('\\', '/')
QPSL_Config_Directory = os.path.join(QPSL_Working_Directory,
                                     "Conf").replace('\\', '/')
QPSL_Plugins_Directory = os.path.join(QPSL_Working_Directory,
                                      "Plugins").replace('\\', '/')
QPSL_Init_Config_Path = os.path.join(QPSL_Config_Directory,
                                     "init.json").replace('\\', '/')
QPSL_Log_Directory = os.path.join(QPSL_Working_Directory,
                                  "Log").replace('\\', '/')
QPSL_UI_Config_Path = os.path.join(QPSL_Config_Directory,
                                   "ui.json").replace('\\', '/')
if not os.path.exists(QPSL_Config_Directory):
    os.mkdir(QPSL_Config_Directory)
if not os.path.exists(QPSL_Init_Config_Path):
    with open(QPSL_Init_Config_Path, "wt") as f:
        f.write("{}")
if not os.path.exists(QPSL_UI_Config_Path):
    with open(QPSL_UI_Config_Path, "wt") as f:
        f.write("{}")
if not os.path.exists(QPSL_Temp_Directory):
    os.mkdir(QPSL_Temp_Directory)
with open(QPSL_Init_Config_Path, "rt") as f:
    __QPSL_init_config_dict: dict = json.load(f)


# 从设置里读取某项
def init_config_get(keys: Tuple):
    cur_level = __QPSL_init_config_dict
    for key in keys:
        if key not in cur_level:
            return None
        cur_level = cur_level[key]
    return cur_level


# 在设置里设置某项
def init_config_set(keys: Tuple, value):
    cur_level = __QPSL_init_config_dict
    for key in keys[:-1]:
        if key not in cur_level:
            cur_level[key] = dict()
        cur_level = cur_level[key]
    cur_level.update({keys[-1]: value})
    init_config_write()


# 在设置里读取某项，如果没读取到就设置为某值
def init_config_getset(keys: Tuple, value):
    cur_level = __QPSL_init_config_dict
    flag = False
    for key in keys[:-1]:
        if key not in cur_level:
            flag = True
            cur_level[key] = dict()
        cur_level = cur_level[key]
    if not flag and keys[-1] in cur_level:
        return cur_level[keys[-1]]
    cur_level.update({keys[-1]: value})
    init_config_write()
    return value


# 把设置写入到配置文件，永久化保存
def init_config_write():
    try:
        temp_path = os.path.join(QPSL_Temp_Directory,
                                 "init.json").replace('\\', '/')
        with open(temp_path, "wt") as f:
            json.dump(__QPSL_init_config_dict, f, indent=4, sort_keys=True)
    except BaseException as e:
        raise e
    else:
        with open(QPSL_Init_Config_Path, "wt") as f:
            json.dump(__QPSL_init_config_dict, f, indent=4, sort_keys=True)


# 管理各个控件是否为虚拟
class VirtualManager:

    def __set_name__(self, cls: type, name: str):
        self.m_name = name
        self.m_data = init_config_getset(keys=(name, ), value=dict())

    def get_obj_key(self, obj):
        return obj.__class__.__name__

    def __get__(self, obj, cls: type):
        key = self.get_obj_key(obj=obj)
        if key not in self.m_data:
            self.m_data[key] = True
            init_config_write()
        return self.m_data[key]

    def __set__(self, obj, val: bool):
        key = self.get_obj_key(obj=obj)
        if key not in self.m_data or self.m_data[key] != val:
            self.m_data[key] = val
            init_config_write()


# 一个提供多个选项、只能单选的选择盒子
class SingleChoiceBox:

    def __init__(self,
                 name: str,
                 config_key: Optional[Tuple[str]] = None) -> None:
        self.m_name = name
        self.m_config_key = config_key
        self.m_current_choice = None

    def get_name(self):
        return self.m_name

    def get_choice_list(self) -> Iterable[str]:
        yield from self.m_choices

    def get_default_choice_from_config(self,
                                       default_value: Optional[str] = None):
        if default_value is None:
            return init_config_get(keys=self.m_config_key)
        else:
            return init_config_getset(keys=self.m_config_key,
                                      value=default_value)

    def is_choosen(self, choice: str):
        return choice == self.m_current_choice

    def callback_of(self, choice: str):

        def func():
            self.set_choice_as(choice=choice, with_callback=True)

        return func

    def set_choice_list(self,
                        choices: Iterable[str],
                        callback: Optional[Callable] = None):
        self.m_choices = list(choices)
        self.m_choice_callback = callback

    def set_choice_as(self, choice: str, with_callback: bool):
        if choice not in self.m_choices or self.m_current_choice == choice:
            return
        self.m_current_choice = choice
        if with_callback:
            if self.m_choice_callback is not None:
                self.m_choice_callback(choice)
        if self.m_config_key is not None:
            init_config_set(keys=self.m_config_key, value=choice)

    def attach_to(self, menu: QMenu):
        menu.addSection(self.get_name())
        for choice in self.get_choice_list():
            action = menu.addAction(choice, self.callback_of(choice=choice))
            action.setCheckable(True)
            if self.is_choosen(choice=choice):
                action.setChecked(True)

    def call(self):
        if self.m_choice_callback is not None:
            self.m_choice_callback(self.m_current_choice)


# 一个提供弹出窗口，内含多个选项、只能单选的选择盒子
class SingleChoicePopBox:

    def __init__(self,
                 name: str,
                 config_key: Optional[Tuple[str]] = None) -> None:
        self.m_name = name
        self.m_config_key = config_key

    def get_name(self):
        return self.m_name

    def get_choice_list(self) -> Iterable[str]:
        yield from self.m_choices

    def get_default_choice_from_config(self,
                                       default_value: Optional[str] = None):
        if default_value is None:
            return init_config_get(keys=self.m_config_key)
        else:
            return init_config_getset(keys=self.m_config_key,
                                      value=default_value)

    def is_choosen(self, choice: str):
        return choice == self.m_current_choice

    def callback_of(self, choice: str):

        def func():
            self.set_choice_as(choice=choice, with_callback=True)

        return func

    def set_choice_list(self,
                        choices: Iterable[str],
                        callback: Optional[Callable] = None):
        self.m_choices = list(choices)
        self.m_choice_callback = callback

    def set_choice_as(self, choice: str, with_callback: bool):
        if choice not in self.m_choices:
            return
        self.m_current_choice = choice
        if with_callback:
            if self.m_choice_callback is not None:
                self.m_choice_callback(choice)
        if self.m_config_key is not None:
            init_config_set(keys=self.m_config_key, value=choice)

    def attach_to(self, menu: QMenu):

        def func():
            dialog = QDialog(None)
            dialog.setWindowTitle(self.get_name())
            layout = QVBoxLayout()
            dialog.setLayout(layout)
            list_widget = QListWidget()
            layout.addWidget(list_widget)
            list_widget.addItems(self.get_choice_list())
            list_widget.setCurrentRow(
                list(self.get_choice_list()).index(self.m_current_choice))
            button = QPushButton("apply")
            layout.addWidget(button)

            def callback(*arg):
                dialog.accept()
                SingleChoicePopBox.set_choice_as(
                    self,
                    choice=list_widget.currentItem().text(),
                    with_callback=True)

            button.clicked.connect(callback)
            dialog.exec()

        if menu.actions():
            menu.addSeparator()
        menu.addAction("{0}...".format(SingleChoicePopBox.get_name(self)),
                       func)

    def call(self):
        if self.m_choice_callback is not None:
            self.m_choice_callback(self.m_current_choice)


# 一个提供可打勾选项的盒子，只能选择 true false
class ToggleBox:

    def __init__(self,
                 name: str,
                 default_value: bool,
                 callback: Callable,
                 config_key: Optional[Tuple[str]] = None) -> None:
        self.m_name = name
        self.m_value = default_value
        self.m_callback = callback
        self.m_config_key = config_key

    def get_name(self):
        return self.m_name

    def get_default_choice_from_config(self,
                                       default_value: Optional[str] = None):
        if default_value is None:
            return init_config_get(keys=self.m_config_key)
        else:
            return init_config_getset(keys=self.m_config_key,
                                      value=default_value)

    def get_value(self):
        return self.m_value

    def set_value(self, value: bool, with_callback: bool):
        self.m_value = value
        if with_callback:
            if self.m_callback is not None:
                self.m_callback(value)
        if self.m_config_key is not None:
            init_config_set(keys=self.m_config_key, value=value)

    def attach_to(self, menu: QMenu):
        action = QAction(self.m_name, menu)
        action.setCheckable(True)
        action.setChecked(self.get_value())

        def callback(value):
            self.set_value(value, True)

        action.triggered.connect(callback)
        menu.addAction(action)

    def call(self):
        if self.m_callback is not None:
            self.m_callback(self.get_value())


# 管理 app style 的选择盒子
QPSL_App_Style_Choice_Box = SingleChoiceBox(name="style_control",
                                            config_key=("style_control", ))
QPSL_App_Style_Choice_Box.set_choice_list(
    choices=QStyleFactory.keys(),
    callback=lambda style: QApplication.setStyle(QStyleFactory.create(style)))
QPSL_App_Style_Choice_Box.set_choice_as(
    choice=QPSL_App_Style_Choice_Box.get_default_choice_from_config(
        default_value="Fusion"),
    with_callback=True)

# 管理 dark light style 的选择盒子
try:
    import qdarkstyle
    QPSL_Dark_Light_Style_Choice_Box = SingleChoiceBox(
        name="dark/light_style", config_key=("dark/light_style", ))

    def __dark_light_style_callback(style: str):
        if style == "Dark":
            QApplication.instance().setStyleSheet(
                qdarkstyle.load_stylesheet(qt_api='pyqt5',
                                           palette=qdarkstyle.DarkPalette))
        elif style == "Light":
            QApplication.instance().setStyleSheet(
                qdarkstyle.load_stylesheet(qt_api='pyqt5',
                                           palette=qdarkstyle.LightPalette))
        else:
            QApplication.instance().setStyleSheet("")

    QPSL_Dark_Light_Style_Choice_Box.set_choice_list(
        choices=["None", "Light", "Dark"],
        callback=__dark_light_style_callback)
    QPSL_Dark_Light_Style_Choice_Box.set_choice_as(
        choice=QPSL_Dark_Light_Style_Choice_Box.get_default_choice_from_config(
            default_value="None"),
        with_callback=False)
except BaseException as e:
    QPSL_Dark_Light_Style_Choice_Box = None

# 管理 material themes 的选择盒子
try:
    import qt_material
    QPSL_Material_Themes_Choice_PopBox = SingleChoicePopBox(
        name="themes", config_key=("themes", ))

    def __material_theme_callback(theme: str):
        if theme == "None":
            QApplication.instance().setStyleSheet("")
        else:
            qt_material.apply_stylesheet(QApplication.instance(), theme=theme)

    QPSL_Material_Themes_Choice_PopBox.set_choice_list(
        choices=["None"] + qt_material.list_themes(),
        callback=__material_theme_callback)
    QPSL_Material_Themes_Choice_PopBox.set_choice_as(
        choice=QPSL_Material_Themes_Choice_PopBox.
        get_default_choice_from_config(default_value="None"),
        with_callback=False)
except BaseException as e:
    QPSL_Material_Themes_Choice_PopBox = None

# 管理 ui load path 的选择盒子
QPSL_UI_Load_Path_Box = SingleChoiceBox(name="UI load path",
                                        config_key=("ui", "UI load path"))
QPSL_UI_Load_Path_Box.set_choice_list(
    choices=["Conf/ui.json", "Plugin/*/ui.json", "always ask"], callback=None)
QPSL_UI_Load_Path_Box.set_choice_as(
    choice=QPSL_UI_Load_Path_Box.get_default_choice_from_config(
        default_value="always ask"),
    with_callback=False)

# 管理程序为单插件还是多插件模式的动作
QPSL_App_Mode_PopBox = SingleChoicePopBox(name="app mode", config_key=None)
