from QPSLClass.Base import *
from ..BaseClass import *
from .QPSLFrameList import QPSLHFrameList
from .QPSLLineEdit import QPSLLineEdit
from .QPSLLabel import QPSLLabel


class QPSLComboLineEdit(QPSLHFrameList):
    sig_return_pressed = pyqtSignal()
    sig_return_pressed_at = pyqtSignal(str)
    sig_editing_finished = pyqtSignal()
    sig_editing_finished_at = pyqtSignal(str)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def load_attr(self,
                  key_text: Optional[str] = None,
                  spacing: Optional[int] = None,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(spacing=spacing,
                          margins=margins,
                          frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if key_text is None:
            key_text = self.default_key_text()
        self.add_widget(QPSLLabel().load_attr(text=key_text))
        self.add_widget(QPSLLineEdit().load_attr())
        self.set_stretch(sizes=(1, 2))
        self.setup_logic()
        return self

    @classmethod
    def default_key_text(cls):
        return "text:"

    def setup_logic(self):
        self.label_key: QPSLLabel = self.get_widget(index=0).remove_type()
        self.edit_text: QPSLLineEdit = self.get_widget(index=1).remove_type()
        connect_direct(self.edit_text.returnPressed, self.on_return_pressed)
        connect_direct(self.edit_text.editingFinished,
                       self.on_editing_finished)
        connect_direct(self.sig_return_pressed, self.sig_editing_finished)
        connect_direct(self.sig_return_pressed_at,
                       self.sig_editing_finished_at)

    def key_text(self):
        return self.label_key.text()

    def value_text(self):
        return self.edit_text.text()

    def clear(self):
        self.edit_text.clear()

    def set_key_text(self, key_text: str):
        self.label_key.setText(key_text)

    def set_value_text(self, text: str):
        self.edit_text.setText(text)

    def set_read_only(self, b: bool):
        self.edit_text.setReadOnly(b)

    def on_return_pressed(self):
        self.sig_return_pressed.emit()
        self.sig_return_pressed_at.emit(self.value_text())

    def on_editing_finished(self):
        self.sig_editing_finished.emit()
        self.sig_editing_finished_at.emit(self.value_text())

    def set_echo_mode(self, echo_mode: QLineEdit.EchoMode):
        self.edit_text.setEchoMode(echo_mode)