from QPSLClass.Base import *
from ..Enum import *
from ..Hooks import *
from .QPSLObjectBase import QPSLObjectBase


class QPSLWidgetBase(QWidget, QPSLObjectBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        font = json.get("font")
        backgroud_color = json.get("backgroud_color")
        h_size_policy = json.get("h_size_policy")
        v_size_policy = json.get("v_size_policy")
        if font is None:
            font = self.default_font()
        else:
            family, pointSize, weight, italic = font.split("; ")
            font = QFont(family, int(pointSize), int(weight), False)
        if h_size_policy is None:
            h_size_policy = self.default_h_size_policy()
        if v_size_policy is None:
            v_size_policy = self.default_v_size_policy()
        self.setFont(font)
        if backgroud_color is not None:
            self.update_background_palette(QColor(backgroud_color))
        self.setSizePolicy(h_size_policy, v_size_policy)
        self.set_custom_context_menu()

    def to_json(self):
        res: Dict = super().to_json()
        font = self.font()
        font0 = self.default_font()
        if font.family() != font0.family() or font.pointSize(
        ) != font0.pointSize() or font.weight() != font0.weight(
        ) or font.italic() != font0.italic():
            res.update({
                "font":
                "{0}; {1}; {2}; {3}".format(font.family(), font.pointSize(),
                                            font.weight(), font.italic())
            })
        color = self.palette().color(self.get_background_color_role())
        if color != self.default_background_color():
            res.update({"backgroud_color": color.name()})
        if self.sizePolicy().horizontalPolicy() != self.default_h_size_policy(
        ):
            res.update({"h_size_policy": self.sizePolicy().horizontalPolicy()})
        if self.sizePolicy().verticalPolicy() != self.default_v_size_policy():
            res.update({"v_size_policy": self.sizePolicy().verticalPolicy()})
        return res

    def __init__(self):
        super().__init__()
        self.m_tooltip_enable: bool = False

    def load_attr(self,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr()
        if h_size_policy is None:
            h_size_policy = self.default_h_size_policy()
        if v_size_policy is None:
            v_size_policy = self.default_v_size_policy()
        self.setSizePolicy(h_size_policy, v_size_policy)
        self.set_custom_context_menu()
        return self

    def to_delete(self):
        if self.get_widgets():
            for widget in self.get_widgets():
                widget.to_delete()
        return super().to_delete()

    def add_widget(self, widget: 'QPSLWidgetBase'):
        pass

    def add_widgets(self, widgets: Iterable['QPSLWidgetBase']):
        pass

    def insert_widget(self, widget: 'QPSLWidgetBase', index: int):
        pass

    def remove_widget(self, widget: 'QPSLWidgetBase'):
        pass

    def remove_widgets(self, widgets: List['QPSLWidgetBase']):
        pass

    def remove_widget_and_delete(self, widget: 'QPSLWidgetBase'):
        pass

    def remove_widgets_and_delete(self, widgets: List['QPSLWidgetBase']):
        pass

    def index_of(self, widget: 'QPSLWidgetBase') -> int:
        pass

    def clear_widgets(self):
        pass

    def get_widget(self, index: int) -> 'QPSLWidgetBase':
        pass

    def get_widgets(self) -> List['QPSLWidgetBase']:
        return []

    def yield_all_widgets(self) -> Iterable['QPSLWidgetBase']:
        yield self
        for widget in self.get_widgets():
            yield from widget.yield_all_widgets()

    @classmethod
    def is_container(cls):
        return False

    @classmethod
    def default_font(cls):
        return QFont("Arial", 12, 50, False)

    @classmethod
    def default_background_color(cls):
        return QColor("#f0f0f0")

    @classmethod
    def default_h_size_policy(cls):
        return QSizePolicy.Policy.Preferred

    @classmethod
    def default_v_size_policy(cls):
        return QSizePolicy.Policy.Preferred

    @classmethod
    def default_tooltip_enable(cls):
        return False

    def set_tooltip_enable(self):
        if not self.m_tooltip_enable:
            self.m_tooltip_enable = True

    def set_tooltip_disable(self):
        if self.m_tooltip_enable:
            self.m_tooltip_enable = False

    def set_custom_context_menu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        connect_direct(self.customContextMenuRequested,
                       self.show_custom_context_menu)

    def unset_custom_context_menu(self):
        disconnect(self.customContextMenuRequested,
                   self.show_custom_context_menu)

    def update_palette(self, role: QPalette.ColorRole,
                       color: typing.Union[str, QColor, Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(role, color)
        self.setPalette(palette)

    def get_background_color_role(self):
        if isinstance(self, QPushButton):
            return QPalette.ColorRole.Button
        else:
            return QPalette.ColorRole.Window

    def get_foreground_color_role(self):
        if isinstance(self, QPushButton):
            return QPalette.ColorRole.ButtonText
        else:
            return QPalette.ColorRole.WindowText

    def update_window_palette(self, color: typing.Union[str, QColor,
                                                        Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)

    def update_button_palette(self, color: typing.Union[str, QColor,
                                                        Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Button, color)
        self.setPalette(palette)

    def update_background_palette(self, color: typing.Union[str, QColor,
                                                            Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(self.get_background_color_role(), color)
        self.setPalette(palette)

    def update_windowtext_palette(self, color: typing.Union[str, QColor,
                                                            Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(QPalette.Foreground, color)
        self.setPalette(palette)

    def update_buttontext_palette(self, color: typing.Union[str, QColor,
                                                            Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(QPalette.ButtonText, color)
        self.setPalette(palette)

    def update_foreground_palette(self, color: typing.Union[str, QColor,
                                                            Qt.GlobalColor]):
        if isinstance(color, str):
            color = QColor(color)
        palette = self.palette()
        palette.setColor(self.get_foreground_color_role(), color)
        self.setPalette(palette)

    def code_runner_box_factory(self):
        box = QWidget()
        layout = QVBoxLayout()
        box.setLayout(layout)
        edit = QTextEdit()
        layout.addWidget(edit)
        button = QPushButton("run")
        layout.addWidget(button)

        def callback(*arg):
            try:
                text = edit.document().toPlainText()
                exec(text, globals(), {'self': self})
            except BaseException as e:
                self.add_error(msg=e)

        connect_direct(button.clicked, callback)
        short_cut = QShortcut("F5", edit, callback)
        return box, None

    def member_widgets_list_factory(self):
        box = QDialog()
        layout = QVBoxLayout()
        box.setLayout(layout)
        res = []
        for w in self.yield_all_widgets():
            if w.objectName():
                res.append(
                    "        self.{0} : {1} = self.findChild({1}, \"{0}\")".
                    format(w.objectName(), w.__class__.__name__))

        edit = QTextEdit()
        for text in res:
            edit.append(text)
        edit.setReadOnly(True)
        layout.addWidget(edit)
        button_box = QDialogButtonBox()
        button = QPushButton("copy")
        button_box.addButton(button, QDialogButtonBox.ButtonRole.AcceptRole)
        layout.addWidget(button_box)

        def callback(*arg):
            clipboard_setText(edit.document().toPlainText())

        connect_direct(button.clicked, callback)
        return box, None

    def add_custom_context_menu_action(
        self,
        menu: QMenu,
        attr_factory: Callable,
        name: str,
        window_title: Optional[str] = None,
        buttons: Optional[
            Union[QDialogButtonBox.StandardButton, QDialogButtonBox.
                  StandardButtons]] = QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Cancel):

        def callback():
            window, reject_callback = attr_factory(self)
            if isinstance(window, QDialog):
                dialog = window
            else:
                dialog = QDialog()
                layout = QVBoxLayout()
                dialog.setLayout(layout)
                layout.addWidget(window)
                if buttons is not None:
                    button_box = QDialogButtonBox(buttons)
                    connect_direct(button_box.accepted, dialog.accept)
                    connect_direct(button_box.rejected, dialog.reject)
                    layout.addWidget(button_box)
            dialog.resize(600, 200)
            if window_title is not None:
                dialog.setWindowTitle(window_title)
            if reject_callback is not None:
                connect_direct(dialog.rejected, reject_callback)
            dialog.exec()

        menu.addAction(name, callback)

    def prepare_custom_context_menu(self, menu: QMenu):

        def clipboard_set_class_name():
            clipboard_setText(self.__class__.__name__)

        menu.addAction(self.__class__.__name__, clipboard_set_class_name)
        parent: QPSLWidgetBase = self.qpsl_parent()
        if parent is not None:
            parent_menu = QMenu("parent...", menu)

            def about_show_parent_context_menu():
                parent_menu.clear()
                parent.prepare_custom_context_menu(parent_menu)

            connect_direct(parent_menu.aboutToShow,
                           about_show_parent_context_menu)
            menu.addMenu(parent_menu)
        menu.addSeparator()

        for name, act in dict.items(self.action_dict):
            action_attach_to_menu(act=act, menu=menu)

        menu.addSeparator()
        global_settings_menu = QMenu("global settings", menu)
        for name, act in get_global_settings().items():
            action_attach_to_menu(act=act, menu=global_settings_menu)
        action_attach_to_menu(act=global_settings_menu, menu=menu)

        menu.addSeparator()
        attribute_settings_menu = QMenu("attributes", menu)
        for class_attr in get_registered_class_attrs(self):
            if self.filter_of_attr(class_attr.get_attr()):
                attribute_settings_menu.addAction(
                    class_attr.get_action_name(),
                    class_attr.dialog_execution_of(self))
        action_attach_to_menu(act=attribute_settings_menu, menu=menu)
        self.add_custom_context_menu_action(
            menu=menu,
            attr_factory=QPSLWidgetBase.code_runner_box_factory,
            name="run code",
            window_title="Run Code",
            buttons=None)
        self.add_custom_context_menu_action(
            menu=menu,
            attr_factory=QPSLWidgetBase.member_widgets_list_factory,
            name="member widgets...",
            window_title="Member Widgets With Names")

    def show_custom_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.prepare_custom_context_menu(menu=menu)
        menu.popup(self.mapToGlobal(pos))

    def filter_of_attr(self, attr):
        return True

    @register_single_text_attribute(action_name="set object name")
    def object_name_attribute(self):
        return self.objectName(
        ), "Set Object Name", "Object Name", self.setObjectName, QSize(
            400, 80)

    @register_multi_comboboxes_attribute(action_name="set size policy")
    def size_policy_attribute(self):

        def callback(names: Tuple[str, str]):
            self.setSizePolicy(size_policy_enum_manager.get_value(names[0]),
                               size_policy_enum_manager.get_value(names[1]))

        return [
            size_policy_enum_manager.get_name(
                self.sizePolicy().horizontalPolicy()),
            size_policy_enum_manager.get_name(
                self.sizePolicy().verticalPolicy())
        ], [size_policy_enum_manager.m_s2v.keys()] * 2, "Set Size Policy", [
            "Horizontal Size Policy", "Vertical Size Policy"
        ], callback, QSize(400, 120)

    @register_dialog_attribute(action_name="set font")
    def font_attribute(self):
        return self.font(
        ), QFontDialog, "Set Font", QFontDialog.currentFontChanged, self.setFont

    @register_dialog_attribute(action_name="set background color")
    def background_color_attribute(self):
        return self.palette().color(
            self.get_background_color_role()
        ), QColorDialog, "Set Background Color", QColorDialog.currentColorChanged, self.update_background_palette

    @register_dialog_attribute(action_name="set foreground color")
    def foreground_color_attribute(self):
        return self.palette().color(
            self.get_foreground_color_role()
        ), QColorDialog, "Set Foreground Color", QColorDialog.currentColorChanged, self.update_foreground_palette
