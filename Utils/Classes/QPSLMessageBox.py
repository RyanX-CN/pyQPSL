from QPSLClass.Base import *
from ..BaseClass import *


class QPSLMessageBox(QMessageBox, QPSLWidgetBase):

    def load_attr(self,
                  text: Optional[str] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if text is None:
            text = self.default_text()
        if window_title is None:
            window_title = self.default_window_title()
        if text:
            self.setText(text)
        if window_title:
            self.setWindowTitle(window_title)
        return self

    @classmethod
    def default_text(cls):
        return ""

    @classmethod
    def default_window_title(cls):
        return ""