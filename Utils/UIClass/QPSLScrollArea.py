from QPSLClass.Base import *
from ..BaseClass import *
from ..Enum import *
from .QPSLLayout import QPSLHBoxLayout, QPSLVBoxLayout, QPSLBoxLayout


class QPSLScrollArea(QScrollArea, QPSLFrameBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        orientation = json.get("orientation")
        margins = json.get("margins")
        spacing = json.get("spacing")
        if orientation is None:
            orientation = self.default_orientation()
        if margins is None:
            margins = self.default_margins()
        else:
            margins = str_to_int_tuple(margins)
        if spacing is None:
            spacing = self.default_spacing()
        self.set_orientation(orientation=orientation)
        self.set_contents_margins(*margins)
        self.set_spacing(spacing=spacing)
        if "widgets" in json:
            for dic in json.get("widgets"):
                self.add_widget(widget=QPSLObjectBase.from_json(dic))

    def to_json(self):
        res: Dict = super().to_json()
        if self.m_orientation != self.default_orientation():
            res.update({"orientation": self.m_orientation})
        if self.get_contents_margins() != self.default_margins():
            res.update({"margins": tuple_to_str(self.get_contents_margins())})
        if self.get_spacing() != self.default_spacing():
            res.update({"spacing": self.get_spacing()})
        if self.get_widgets():
            res.update({
                "widgets": [widget.to_json() for widget in self.get_widgets()]
            })
        return res

    def __new__(cls, *args, **kwargs):
        if cls is __class__:
            raise TypeError("{0} may not be directly instantiated".format(
                cls.__name__))
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()
        self.m_orientation: Qt.Orientation = self.default_orientation()

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if orientation is None:
            orientation = self.default_orientation()
        if margins is None:
            margins = self.default_margins()
        if spacing is None:
            spacing = self.default_spacing()
        self.set_orientation(orientation=orientation)
        self.set_contents_margins(*margins)
        self.set_spacing(spacing=spacing)
        return self

    def to_delete(self):
        self.clear_widgets()
        return super().to_delete()

    @classmethod
    def is_container(cls):
        return True

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal

    @classmethod
    def default_margins(cls):
        return 0, 0, 0, 0

    @classmethod
    def default_spacing(cls):
        return 0

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal

    def set_orientation(self, orientation: Qt.Orientation):
        self.m_orientation = orientation
        frame = QFrame()
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(QPSLBoxLayout(orientation=orientation)().load_attr())
        frame.installEventFilter(self)
        self.setWidget(frame)

    def get_orientation(self):
        return self.m_orientation

    def set_contents_margins(self, left: int, top: int, right: int,
                             bottom: int):
        self.layout.setContentsMargins(left, top, right, bottom)

    def get_contents_margins(self):
        return self.layout.getContentsMargins()

    def set_spacing(self, spacing: int):
        self.layout.setSpacing(spacing)

    def get_spacing(self):
        return self.layout.spacing()

    def add_widget(self, widget: QPSLWidgetBase):
        self.layout.add_widget(widget=widget)
        self.on_update_view()

    def add_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.add_widget(widget=widget)

    def insert_widget(self, widget: QPSLWidgetBase, index: int):
        self.layout.insert_widget(widget=widget, index=index)
        self.on_update_view()

    def remove_widget(self, widget: QPSLWidgetBase):
        self.layout.remove_widget(widget=widget)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget(widget=widget)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        self.layout.remove_widget_and_delete(widget=widget)

    def remove_widgets_and_delete(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget_and_delete(widget=widget)

    def index_of(self, widget: QPSLWidgetBase):
        return self.layout.index_of(widget=widget)

    def get_widget(self, index: int):
        return self.layout.get_widget(index=index)

    def get_widgets(self):
        return self.layout.get_widgets()

    def clear_widgets(self):
        self.layout.clear_widgets()

    def on_update_height(self):
        size = self.size()
        l, t, r, b = self.get_contents_margins()
        fh = size.height() - 2
        d = self.scrollBar.height(
        ) if self.widget().sizeHint().width() > size.width() else 0
        self.widget().setFixedHeight(fh - d)
        self.widget().adjustSize()
        for widget in self.layout.get_widgets():
            widget.setFixedHeight(fh - t - b - d)

    def on_update_width(self):
        size = self.size()
        l, t, r, b = self.get_contents_margins()
        fw = size.width() - 2
        d = self.scrollBar.width(
        ) if self.widget().sizeHint().height() > size.height() else 0
        self.widget().setFixedWidth(fw - d)
        self.widget().adjustSize()
        for widget in self.get_widgets():
            widget.setFixedWidth(fw - l - r - d)

    def on_update_view(self):
        if self.m_orientation == Qt.Orientation.Horizontal:
            self.on_update_height()
        else:
            self.on_update_width()

    def showEvent(self, ev: QShowEvent):
        self.on_update_view()
        return super().showEvent(ev)

    def resizeEvent(self, ev: QResizeEvent):
        self.on_update_view()
        return super().resizeEvent(ev)

    def eventFilter(self, frame: QFrame, ev: QEvent):
        if frame == self.widget() and ev.type() == QEvent.Type.LayoutRequest:
            self.on_update_view()
        return super().eventFilter(frame, ev)

    @register_single_integer_attribute(action_name="set spacing")
    def spacing_attribute(self):
        return self.get_spacing(), (
            0,
            100), "Set Spacing", "Spacing", self.set_spacing, QSize(400, 80)

    @register_multi_integers_attribute(action_name="set contents margins")
    def contents_margins_attribute(self):

        def callback(values):
            self.set_contents_margins(*values)

        return self.get_contents_margins(), [
            (0, 100)
        ] * 4, "Set Contents Margin", ("left", "top", "right",
                                       "bottom"), callback, QSize(400, 200)

    @property
    def layout(self) -> Union[QPSLHBoxLayout, QPSLVBoxLayout]:
        return self.widget().layout()

    @property
    def scrollBar(self):
        if self.get_orientation() == Qt.Orientation.Horizontal:
            return self.horizontalScrollBar()
        else:
            return self.verticalScrollBar()


class QPSLHScrollArea(QPSLScrollArea):

    def load_attr(self,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(margins=margins,
                                 spacing=spacing,
                                 frame_shape=frame_shape,
                                 frame_shadow=frame_shadow,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)


class QPSLVScrollArea(QPSLScrollArea):

    def load_attr(self,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(margins=margins,
                                 spacing=spacing,
                                 frame_shape=frame_shape,
                                 frame_shadow=frame_shadow,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Vertical


def make_QPSLScrollArea_class(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Horizontal:
        return QPSLHScrollArea
    else:
        return QPSLVScrollArea
