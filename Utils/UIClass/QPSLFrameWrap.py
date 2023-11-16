from QPSLClass.Base import *
from QPSLClass.Base import Dict
from ..BaseClass import *
from .QPSLFrame import QPSLFrame


class QPSLFrameWrap(QPSLFrame):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setLayout(QGridLayout())
        self.layout.setContentsMargins(0, 0, 0, 0)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.m_widget: Optional[QPSLWidgetBase] = None

    def load_attr(self,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        self.setLayout(QGridLayout())
        self.layout.setContentsMargins(0, 0, 0, 0)
        return self

    def to_delete(self):
        self.set_inner_widget(widget=None)
        return super().to_delete()

    def set_inner_widget(self, widget: QPSLWidgetBase):
        if self.m_widget is not None:
            self.layout.removeWidget(self.m_widget)
        if widget is not None:
            self.layout.addWidget(widget)
        self.m_widget = widget

    def get_inner_widget(self):
        return self.m_widget

    @property
    def layout(self) -> QGridLayout:
        return super().layout()