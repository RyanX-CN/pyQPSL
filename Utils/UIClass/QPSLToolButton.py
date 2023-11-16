from QPSLClass.Base import *
from ..Enum import *
from ..BaseClass import *


class QPSLToolButton(QToolButton, QPSLWidgetBase):
    sig_clicked = pyqtSignal()
    sig_clicked_of = pyqtSignal(QPushButton)
    sig_clicked_str = pyqtSignal(str)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("text")
        style = json.get("style")
        if text is None:
            text = self.default_text()
        if style is None:
            style = self.default_style()
        if text:
            self.setText(text)
        self.setToolButtonStyle(style)

    def to_json(self):
        res = super().to_json()
        if self.text() != self.default_text():
            res.update({"text": self.text()})
        if self.toolButtonStyle() != self.default_style():
            res.update({"style": self.toolButtonStyle()})
        return res

    def __init__(self):
        super().__init__()
        self.m_text = self.default_text()
        connect_direct(self.clicked, self.on_clicked)

    def load_attr(self,
                  text: Optional[str] = None,
                  style: Optional[Qt.ToolButtonStyle] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if style is None:
            style = self.default_style()
        if text:
            self.set_text(text=text)
        self.setToolButtonStyle(style)
        return self

    @classmethod
    def default_text(cls):
        return ""

    @classmethod
    def default_style(cls):
        return Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    def set_tooltip_enable(self):
        super().set_tooltip_enable()
        self.update_tooltip()

    def set_tooltip_disable(self):
        super().set_tooltip_disable()
        self.update_tooltip()

    def on_clicked(self, checked: bool):
        self.sig_clicked.emit()
        self.sig_clicked_of.emit(self)
        self.sig_clicked_str.emit(self.text())

    @register_single_text_attribute(action_name="set text")
    def text_attribute(self):
        return self.text(), "Set Text", "Text", self.setText, QSize(400, 80)

    @register_single_combobox_attribute(action_name="set style")
    def style_attribute(self):

        def callback(style: str):
            self.setToolButtonStyle(
                toolbutton_style_enum_manager.get_value(style))

        return toolbutton_style_enum_manager.get_name(
            self.toolButtonStyle()), toolbutton_style_enum_manager.m_s2v.keys(
            ), "Set Style", "Style", callback, QSize(400, 80)
