from QPSLClass.Base import *
from QPSLClass.Base import QMenu
from ..BaseClass import *


class QPSLPushButton(QPushButton, QPSLWidgetBase):
    sig_clicked = pyqtSignal()
    sig_clicked_of = pyqtSignal(QPushButton)
    sig_clicked_str = pyqtSignal(str)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("m_text")
        if text is None:
            text = self.default_text()
        if text:
            self.set_text(text=text)

    def to_json(self):
        res = super().to_json()
        if self.text() != self.default_text():
            res.update({"m_text": self.text()})
        return res

    def __init__(self):
        super().__init__()
        self.m_text = self.default_text()
        connect_direct(self.clicked, self.on_clicked)

    def load_attr(self,
                  text: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if text:
            self.set_text(text=text)
        return self

    @classmethod
    def default_text(cls):
        return ""

    def set_tooltip_enable(self):
        super().set_tooltip_enable()
        self.update_tooltip()

    def set_tooltip_disable(self):
        super().set_tooltip_disable()
        self.update_tooltip()

    def set_text(self, text: str):
        self.m_text = text
        self.update_text(text=text)
        self.update_tooltip()

    def set_font(self, font: QFont):
        self.setFont(font)
        self.update_text(text=self.m_text)

    def text(self):
        return self.m_text

    def update_text(self, text: str):
        w = self.fontMetrics().width(text)
        if w > self.width():
            self.setText(self.fontMetrics().elidedText(
                text, Qt.TextElideMode.ElideRight, self.width()))
        else:
            self.setText(text)

    def update_tooltip(self):
        if self.m_tooltip_enable:
            self.setToolTip(self.text())
        else:
            self.setToolTip("")

    def on_clicked(self, checked: bool):
        self.sig_clicked.emit()
        self.sig_clicked_of.emit(self)
        self.sig_clicked_str.emit(self.text())

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.update_text(text=self.m_text)
        return super().resizeEvent(a0)

    @register_single_text_attribute(action_name="set text")
    def text_attribute(self):
        return self.text(), "Set Text", "Text", self.set_text, QSize(400, 80)


class QPSLToggleButton(QPSLPushButton):
    sig_open = pyqtSignal()
    sig_close = pyqtSignal()
    sig_opened = pyqtSignal()
    sig_closed = pyqtSignal()
    sig_state_changed = pyqtSignal(bool)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        closed_text = json.get("m_closed_text")
        opened_text = json.get("m_opened_text")
        closed_background_color = json.get("m_closed_background_color")
        opened_background_color = json.get("m_opened_background_color")
        if closed_text is None:
            closed_text = self.default_closed_text()
        if opened_text is None:
            opened_text = self.default_opened_text()
        if closed_background_color is None:
            closed_background_color = self.default_closed_bg_color()
        if opened_background_color is None:
            opened_background_color = self.default_opened_bg_color()
        self.m_closed_text = closed_text
        self.m_opened_text = opened_text
        self.m_closed_background_color = closed_background_color
        self.m_opened_background_color = opened_background_color
        self.set_state(opened=False)

    def to_json(self):
        res = super().to_json()
        if self.m_closed_text != self.default_closed_text():
            res.update({"m_closed_text": self.m_closed_text})
        if self.m_opened_text != self.default_opened_text():
            res.update({"m_opened_text": self.m_opened_text})
        if self.m_closed_background_color != self.default_closed_bg_color():
            res.update(
                {"m_closed_background_color": self.m_closed_background_color})
        if self.m_opened_background_color != self.default_opened_bg_color():
            res.update(
                {"m_opened_background_color": self.m_opened_background_color})
        return res

    def __init__(self):
        super().__init__()
        self.m_state: bool = False
        self.m_closed_text = self.default_closed_text()
        self.m_opened_text = self.default_opened_text()
        self.m_closed_background_color = self.default_closed_bg_color()
        self.m_opened_background_color = self.default_opened_bg_color()

    def load_attr(self,
                  closed_text: Optional[str] = None,
                  opened_text: Optional[str] = None,
                  closed_background_color: Optional[str] = None,
                  opened_background_color: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if closed_text is None:
            closed_text = self.default_closed_text()
        if opened_text is None:
            opened_text = self.default_opened_text()
        if closed_background_color is None:
            closed_background_color = self.default_closed_bg_color()
        if opened_background_color is None:
            opened_background_color = self.default_opened_bg_color()
        self.m_closed_text = closed_text
        self.m_opened_text = opened_text
        self.m_closed_background_color = closed_background_color
        self.m_opened_background_color = opened_background_color
        self.set_state(opened=False)
        return self

    @classmethod
    def default_closed_text(cls):
        return ""

    @classmethod
    def default_opened_text(cls):
        return ""

    @classmethod
    def default_closed_bg_color(cls):
        return "#a2a2a2"

    @classmethod
    def default_opened_bg_color(cls):
        return "#ffffff"

    def get_state(self):
        return self.m_state

    def get_texts(self):
        return self.m_closed_text, self.m_opened_text

    def set_texts(self, closed_text: str, opened_text: str):
        self.m_closed_text = closed_text
        self.m_opened_text = opened_text
        self.set_state(opened=self.m_state)

    def set_background_colors(
            self, closed_background_color: typing.Union[str, QColor,
                                                        Qt.GlobalColor],
            opened_background_color: typing.Union[str, QColor,
                                                  Qt.GlobalColor]):
        self.m_closed_background_color = closed_background_color
        self.m_opened_background_color = opened_background_color
        self.set_state(opened=self.m_state)

    def set_state(self, opened: bool):
        self.m_state = opened
        if self.m_state:
            self.set_text(text=self.m_opened_text)
            if self.m_opened_background_color:
                self.update_background_palette(
                    color=self.m_opened_background_color)
            self.sig_opened.emit()
            self.sig_state_changed.emit(True)
        else:
            self.set_text(text=self.m_closed_text)
            if self.m_closed_background_color:
                self.update_background_palette(
                    color=self.m_closed_background_color)
            self.sig_closed.emit()
            self.sig_state_changed.emit(False)

    def set_opened(self):
        self.set_state(opened=True)

    def set_closed(self):
        self.set_state(opened=False)

    def on_clicked(self, checked: bool):
        if self.m_state:
            self.sig_close.emit()
        else:
            self.sig_open.emit()
        return super().on_clicked(checked)

    def filter_of_attr(self, attr):
        if attr is QPSLPushButton.text_attribute:
            return False
        return super().filter_of_attr(attr=attr)

    @register_multi_texts_attribute(action_name="set texts")
    def label_titles_attr(self):
        label_texts = self.get_texts()
        key_texts = ["text in closed state:", "text in opened state:"]

        def callback(texts):
            self.set_texts(*texts)

        return label_texts, "Set Closed And Opened Texts", key_texts, callback, QSize(
            400, 120)
