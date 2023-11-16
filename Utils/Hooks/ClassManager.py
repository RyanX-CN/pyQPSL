from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union
from PyQt5.QtCore import QObject, QSize, Qt, pyqtBoundSignal
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QVBoxLayout, QWidget

__QPSL_registered_classes: Dict[str, type] = dict()


def get_registered_classes():
    return __QPSL_registered_classes


def get_registered_class(name: str):
    return __QPSL_registered_classes.get(name)


def register_class(cls: type):
    __QPSL_registered_classes.update({cls.__name__: cls})


class ClassAttribute:

    def __init__(self, action_name: str, func: Callable):
        super().__init__()
        self.m_action_name = action_name
        self.m_class_name = func.__qualname__.split('.')[0]
        self.m_func = func

    def get_action_name(self):
        return self.m_action_name

    def get_attr(self):
        return self.m_func

    def get_class_name(self):
        return self.m_class_name

    def make_dialog(self, obj: QWidget) -> QDialog:
        pass

    def exec_dialog(self, obj: QWidget):
        dialog = self.make_dialog(obj=obj)
        dialog.exec()

    def dialog_execution_of(self, obj: QWidget):
        return lambda: self.exec_dialog(obj=obj)


class ClassAttribute_single_text(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_text: str = res[0]
        window_title: str = res[1]
        key_text: str = res[2]
        edit_callback: Callable = res[3]
        dialog_size: QSize = res[4]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)
        hlayout.addWidget(QLabel("{0}:".format(key_text)))
        edit = QLineEdit(old_text)
        hlayout.addWidget(edit)

        def callback(*arg):
            edit_callback(edit.text())

        def reject_callback():
            edit_callback(old_text)

        edit.textEdited.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_multi_texts(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_texts: List[str] = res[0]
        window_title: str = res[1]
        key_texts: List[str] = res[2]
        edit_callback: Callable = res[3]
        dialog_size: QSize = res[4]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)
        edits: List[QLineEdit] = []
        for i, (key_text, text) in enumerate(zip(key_texts, old_texts)):
            label = QLabel(key_text)
            edit = QLineEdit(text)
            edits.append(edit)
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(edit, i, 1)

        def callback(*arg):
            edit_callback([edit.text() for edit in edits])

        def reject_callback():
            edit_callback(old_texts)

        for edit in edits:
            edit.textEdited.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        layout.setStretch(0, len(old_texts))
        layout.setStretch(1, 1)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_single_integer(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_value: int = res[0]
        _range: Tuple[int, int] = res[1]
        window_title: str = res[2]
        key_text: str = res[3]
        slider_callback: Callable = res[4]
        dialog_size: QSize = res[5]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)

        slider = QSlider(orientation=Qt.Orientation.Horizontal)
        slider.setRange(*_range)
        slider.setValue(old_value)

        def get_repr():
            return "{0} = {1}".format(key_text, slider.value())

        label = QLabel(get_repr())
        hlayout.addWidget(label, 1)
        hlayout.addWidget(slider, 10)

        def callback(value):
            label.setText(get_repr())
            slider_callback(value)

        def reject_callback():
            slider_callback(old_value)

        slider.valueChanged.connect(callback)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_multi_integers(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_values: List[int] = res[0]
        _ranges: List[Tuple[int, int]] = res[1]
        window_title: str = res[2]
        key_texts: List[str] = res[3]
        sliders_callback: Callable = res[4]
        dialog_size: QSize = res[5]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        labels: List[QLabel] = []
        sliders: List[QSlider] = []

        def get_repr(i: int):
            return "{0} = {1}".format(key_texts[i], sliders[i].value())

        for i, (_range, value) in enumerate(zip(_ranges, old_values)):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(*_range)
            slider.setValue(value)
            sliders.append(slider)
            label = QLabel(get_repr(i))
            labels.append(label)
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(slider, i, 1)

        def callback(*arg):
            for i, label in enumerate(labels):
                label.setText(get_repr(i))
            sliders_callback([slider.value() for slider in sliders])

        def reject_callback():
            sliders_callback(old_values)

        for slider in sliders:
            slider.valueChanged.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_multi_floats(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_values: List[float] = res[0]
        _ranges: List[Tuple[float, float]] = res[1]
        decimals: int = res[2]
        window_title: str = res[3]
        key_texts: List[str] = res[4]
        sliders_callback: Callable = res[5]
        dialog_size: QSize = res[6]
        ratio = 10**decimals

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        labels: List[QLabel] = []
        sliders: List[QSlider] = []

        def get_repr(i: int):
            return "{{0}} = {{1:.{0}f}}".format(decimals).format(
                key_texts[i], sliders[i].value() / ratio)

        for i, (_range, value) in enumerate(zip(_ranges, old_values)):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(round(_range[0] * ratio), round(_range[1] * ratio))
            slider.setValue(round(value * ratio))
            sliders.append(slider)
            label = QLabel(get_repr(i))
            labels.append(label)
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(slider, i, 1)

        def callback(*arg):
            for i, label in enumerate(labels):
                label.setText(get_repr(i))
            sliders_callback([slider.value() / ratio for slider in sliders])

        def reject_callback():
            sliders_callback(old_values)

        for slider in sliders:
            slider.valueChanged.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        dialog.exec()


class ClassAttribute_integer_range(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_range: Tuple[int, int] = res[0]
        window_title: str = res[1]
        edit_callback: Callable = res[2]
        dialog_size: QSize = res[3]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        label1 = QLabel("minimum:")
        grid_layout.addWidget(label1, 0, 0)
        edit1 = QLineEdit(str(old_range[0]))
        edit1.setValidator(QIntValidator())
        grid_layout.addWidget(edit1, 0, 1)

        label2 = QLabel("maximum:")
        grid_layout.addWidget(label2, 1, 0)
        edit2 = QLineEdit(str(old_range[1]))
        edit2.setValidator(QIntValidator())
        grid_layout.addWidget(edit2, 1, 1)

        def callback(*arg):
            if not edit1.text() or not edit2.text(): return
            minimum, maximum = int(edit1.text()), int(edit2.text())
            if minimum >= maximum:
                return
            edit_callback(minimum, maximum)

        def reject_callback():
            edit_callback(*old_range)

        edit1.textChanged.connect(callback)
        edit2.textChanged.connect(callback)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_float_range(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_range: Tuple[float, float] = res[0]
        window_title: str = res[1]
        edit_callback: Callable = res[2]
        dialog_size: QSize = res[3]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        label1 = QLabel("minimum:")
        grid_layout.addWidget(label1, 0, 0)
        edit1 = QLineEdit(str(old_range[0]))
        edit1.setValidator(QDoubleValidator())
        grid_layout.addWidget(edit1, 0, 1)

        label2 = QLabel("maximum:")
        grid_layout.addWidget(label2, 1, 0)
        edit2 = QLineEdit(str(old_range[1]))
        edit2.setValidator(QDoubleValidator())
        grid_layout.addWidget(edit2, 1, 1)

        def callback(*arg):
            if not edit1.text() or not edit2.text(): return
            minimum, maximum = float(edit1.text()), float(edit2.text())
            if minimum >= maximum:
                return
            edit_callback(minimum, maximum)

        def reject_callback():
            edit_callback(*old_range)

        edit1.textChanged.connect(callback)
        edit2.textChanged.connect(callback)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_single_combobox(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_attr: str = res[0]
        attr_list: List[str] = res[1]
        window_title: str = res[2]
        key_text: str = res[3]
        combobox_callback: Callable = res[4]
        dialog_size: QSize = res[5]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)
        label = QLabel(key_text)
        combobox = QComboBox()
        combobox.addItems(attr_list)
        combobox.setCurrentText(old_attr)
        hlayout.addWidget(label)
        hlayout.addWidget(combobox)

        def callback(*arg):
            combobox_callback(combobox.currentText())

        def reject_callback():
            combobox_callback(old_attr)

        combobox.currentTextChanged.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_multi_comboboxes(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_attrs: List[str] = res[0]
        attr_lists: List[List[str]] = res[1]
        window_title: str = res[2]
        key_texts: List[str] = res[3]
        combobox_callback: Callable = res[4]
        dialog_size: QSize = res[5]

        dialog = QDialog()
        dialog.setWindowTitle(window_title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)
        comboboxes: List[QComboBox] = []
        for i, (key_text, attr_list,
                old_attr) in enumerate(zip(key_texts, attr_lists, old_attrs)):
            label = QLabel(key_text)
            combobox = QComboBox()
            combobox.addItems(attr_list)
            combobox.setCurrentText(old_attr)
            comboboxes.append(combobox)
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(combobox, i, 1)

        def callback(*arg):
            combobox_callback(
                [combobox.currentText() for combobox in comboboxes])

        def reject_callback():
            combobox_callback(old_attrs)

        for combobox in comboboxes:
            combobox.currentTextChanged.connect(callback)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog_size is not None:
            dialog.resize(dialog_size)
        layout.setStretch(0, len(old_attrs))
        layout.setStretch(1, 1)
        dialog.rejected.connect(reject_callback)
        return dialog


class ClassAttribute_dialog(ClassAttribute):

    def make_dialog(self, obj: QWidget):
        res = self.m_func(obj)
        old_attr: List[str] = res[0]
        dialog_class: type = res[1]
        window_title: str = res[2]
        signal: pyqtBoundSignal = res[3]
        edit_callback: Callable = res[4]

        def reject_callback():
            edit_callback(old_attr)

        dialog = dialog_class(old_attr, None)
        QDialog.setWindowTitle(dialog, window_title)
        pyqtBoundSignal.connect(signal.__get__(dialog), edit_callback)
        pyqtBoundSignal.connect(QDialog.rejected.__get__(dialog),
                                reject_callback)
        return dialog


__QPSL_registered_class_attrs: Dict[str, List[ClassAttribute]] = dict()


def get_registered_class_attrs(obj: QObject):
    for cls in obj.__class__.mro():
        if cls.__name__ in __QPSL_registered_class_attrs:
            for class_attr in __QPSL_registered_class_attrs.get(cls.__name__):
                yield class_attr


def register_single_text_attribute(action_name: str):
    """
    指定单文本属性的旧文本、标题、key 文本、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_single_text(action_name=action_name, func=func))
        return func

    return wrap


def register_multi_texts_attribute(action_name: str):
    """
    指定多文本属性的旧文本、标题、key 文本、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_multi_texts(action_name=action_name, func=func))
        return func

    return wrap


def register_single_integer_attribute(action_name: str):
    """
    指定单整数属性的旧值、范围、标题、key 文本、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_single_integer(action_name=action_name, func=func))
        return func

    return wrap


def register_multi_integers_attribute(action_name: str):
    """
    指定多整数属性的旧值、范围、标题、key 文本、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_multi_integers(action_name=action_name, func=func))
        return func

    return wrap


def register_multi_floats_attribute(action_name: str):
    """
    指定多整数属性的旧值、范围、精度、标题、key 文本、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_multi_floats(action_name=action_name, func=func))
        return func

    return wrap


def register_integer_range_attribute(action_name: str):
    """
    指定范围属性的旧值、标题、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_integer_range(action_name=action_name, func=func))
        return func

    return wrap


def register_float_range_attribute(action_name: str):
    """
    指定范围属性的旧值、标题、编辑回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_float_range(action_name=action_name, func=func))
        return func

    return wrap


def register_single_combobox_attribute(action_name: str):
    """
    指定单个组合框属性的旧值、旧选项集合、标题、key 文本、选项回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_single_combobox(action_name=action_name, func=func))
        return func

    return wrap


def register_multi_comboboxes_attribute(action_name: str):
    """
    指定多个组合框属性的旧值、旧选项集合、标题、key 文本、选项回调、默认尺寸
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_multi_comboboxes(action_name=action_name,
                                            func=func))
        return func

    return wrap


def register_dialog_attribute(action_name: str):
    """
    指定对话框属性的旧值、对话框类型、标题、信号、编辑回调
    """

    def wrap(func: Callable):
        cls_name = func.__qualname__.split('.')[0]
        if cls_name not in __QPSL_registered_class_attrs:
            __QPSL_registered_class_attrs.update({cls_name: []})
        __QPSL_registered_class_attrs[cls_name].append(
            ClassAttribute_dialog(action_name=action_name, func=func))
        return func

    return wrap
