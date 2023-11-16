from PyQt5 import QtGui
from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLCheckBox(QCheckBox, QPSLWidgetBase):
    sig_value_changed = pyqtSignal()
    sig_value_changed_of = pyqtSignal(QCheckBox)
    sig_value_changed_to = pyqtSignal(bool)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        text = json.get("text")
        checked = json.get("checked")
        if text is None:
            text = self.default_text()
        if checked is None:
            checked = self.default_checked()
        if text:
            self.setText(text)
        self.setChecked(checked)
        self.setup_logic()
        return self

    def to_json(self):
        res: Dict = super().to_json()
        if self.text() != self.default_text():
            res.update({"text": self.text()})
        if self.isChecked() != self.default_checked():
            res.update({"checked": self.isChecked()})
        return res

    def load_attr(self,
                  text: Optional[str] = None,
                  checked: Optional[bool] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        self.setCheckable(True)
        if text is None:
            text = self.default_text()
        if checked is None:
            checked = self.default_checked()
        if text:
            self.setText(text)
        self.setChecked(checked)
        self.setup_logic()
        return self

    @classmethod
    def default_text(cls):
        return "option"

    @classmethod
    def default_checked(cls):
        return False

    def setup_logic(self):
        connect_direct(self.toggled, self.on_toggled)

    def on_toggled(self, val: bool):
        self.sig_value_changed.emit()
        self.sig_value_changed_of.emit(self)
        self.sig_value_changed_to.emit(val)

    @register_single_text_attribute(action_name="set text")
    def text_attribute(self):
        return self.text(), "Set Text", "Text", self.setText, QSize(400, 80)
