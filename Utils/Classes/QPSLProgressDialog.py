from QPSLClass.Base import *
from Utils.BaseClass import *


class QPSLProgressDialog(QProgressDialog, QPSLWidgetBase):

    def load_attr(self,
                  title: Optional[str] = None,
                  _range: Optional[Tuple[int, int]] = None,
                  width: Optional[int] = 800,
                  height: Optional[int] = 20,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if title is None:
            title = self.default_title()
        if _range is None:
            _range = self.default_range()
        if width is None:
            width = self.default_width()
        if height is None:
            height = self.default_height()
        self.setWindowTitle(title)
        self.setRange(*_range)
        self.resize(width, height)
        return self

    @classmethod
    def default_title(cls):
        return "progress"

    @classmethod
    def default_range(cls):
        return (0, 100)

    @classmethod
    def default_width(cls):
        return 800

    @classmethod
    def default_height(cls):
        return 20