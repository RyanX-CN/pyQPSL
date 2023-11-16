from QPSLClass.Base import *
from ..BaseClass import *


class QPSLDialog(QDialog, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        window_title = json.get("window_title")
        if window_title is None:
            window_title = self.default_window_title()
        if window_title:
            self.setWindowTitle(window_title)

    def to_json(self):
        res: Dict = super().to_json()
        if self.windowTitle() != self.default_window_title():
            res.update({"window_title": self.windowTitle()})
        return res

    def load_attr(self,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if window_title is None:
            window_title = self.default_window_title()
        if window_title:
            self.setWindowTitle(window_title)
        return self

    @classmethod
    def default_window_title(cls):
        return ""

    @register_single_text_attribute(action_name="set window title")
    def window_title_attribute(self):
        return self.windowTitle(
        ), "Set Window Title", "Window Title", self.setWindowTitle, QSize(
            400, 80)
