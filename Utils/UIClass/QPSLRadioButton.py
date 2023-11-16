from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLRadioButton(QRadioButton, QPSLWidgetBase):
    sig_clicked = pyqtSignal()
    sig_clicked_of = pyqtSignal(QRadioButton)
    sig_clicked_str = pyqtSignal(str)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("text")
        is_checked = json.get("is_checked")
        if text is None:
            text = self.default_text()
        if is_checked is None:
            is_checked = self.default_is_checked()
        if text:
            self.setText(text)
        if is_checked:
            self.setChecked(True)

    def to_json(self):
        res: Dict = super().to_json()
        if self.text() != self.default_text():
            res.update({"text": self.text()})
        if self.isChecked() != self.default_is_checked():
            res.update({"is_checked": self.isChecked()})
        return res

    def load_attr(self,
                  text: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if text:
            self.setText(text)
        connect_direct(self.clicked, self.on_clicked)
        return self

    @classmethod
    def default_text(cls):
        return ""

    @classmethod
    def default_is_checked(cls):
        return False

    def on_clicked(self):
        self.sig_clicked.emit()
        self.sig_clicked_of.emit(self)
        self.sig_clicked_str.emit(self.text())

    @register_single_text_attribute(action_name="set text")
    def text_attribute(self):
        return self.text(), "Set Text", "Text", self.setText, QSize(400, 80)
