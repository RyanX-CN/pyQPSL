from QPSLClass.Base import *
from ..BaseClass import *
from ..Enum import *
from .QPSLLayout import QPSLHBoxLayout, QPSLVBoxLayout, QPSLBoxLayout


class QPSLScrollList(QScrollArea, QPSLFrameBase):

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
            if "ratios" in json:
                for dic, ratio in zip(json.get("widgets"),
                                      str_to_float_tuple(json.get("ratios"))):
                    self.add_widget(widget=QPSLObjectBase.from_json(dic),
                                    ratio=ratio)
            else:
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
        res.update({"ratios": "; ".join(map(str, self.m_ratios))})
        return res

    def __new__(cls, *args, **kwargs):
        if cls is __class__:
            raise TypeError("{0} may not be directly instantiated".format(
                cls.__name__))
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()
        self.m_orientation: Qt.Orientation = self.default_orientation()
        self.m_ratios: List[float] = []

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

    def add_widget(self, widget: QPSLWidgetBase, ratio: float = 1.0):
        self.layout.add_widget(widget=widget)
        self.m_ratios.append(ratio)
        self.on_update_view()

    def add_widgets(self,
                    widgets: List[QPSLWidgetBase],
                    ratios: Union[float, Iterable[float]] = 1.0):
        if isinstance(ratios, float):
            for widget in widgets:
                self.add_widget(widget=widget, ratio=ratios)
        else:
            for widget, ratio in zip(widgets, ratios):
                self.add_widget(widget=widget, ratio=ratio)

    def insert_widget(self,
                      widget: QPSLWidgetBase,
                      index: int,
                      ratio: float = 1.0):
        self.layout.insert_widget(widget=widget, index=index)
        self.m_ratios.insert(index, ratio)
        self.on_update_view()

    def remove_widget(self, widget: QPSLWidgetBase):
        index = self.index_of(widget=widget)
        self.m_ratios.pop(index)
        self.layout.remove_widget(widget=widget)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget(widget=widget)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        index = self.index_of(widget=widget)
        self.m_ratios.pop(index)
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
        self.m_ratios.clear()

    def on_update_height(self):
        size = self.size()
        l, t, r, b = self.get_contents_margins()
        spacing = self.get_spacing()
        n = len(self.get_widgets())
        widget_height = size.height() - 2 - t - b
        fw, fh = 2 + l + r + sum(
            int(widget_height * r)
            for r in self.m_ratios) + (n - 1) * spacing, size.height() - 2
        d = self.scrollBar.height() if fw > size.width() else 0
        self.widget().setFixedSize(fw, fh - d)
        for widget, ratio in zip(self.layout.get_widgets(), self.m_ratios):
            widget.setFixedSize(int(widget_height * ratio), widget_height - d)

    def on_update_width(self):
        size = self.size()
        l, t, r, b = self.get_contents_margins()
        spacing = self.get_spacing()
        n = len(self.get_widgets())
        widget_width = size.width() - 2 - l - r
        fw, fh = size.width() - 2, 2 + t + b + sum(
            int(widget_width * r) for r in self.m_ratios) + (n - 1) * spacing
        d = self.scrollBar.width() if fh > size.height() else 0
        self.widget().setFixedSize(fw - d, fh)
        for widget, ratio in zip(self.get_widgets(), self.m_ratios):
            widget.setFixedSize(widget_width - d, int(widget_width * ratio))

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

    @register_multi_floats_attribute(action_name="set ratios")
    def ratios_attribute(self):
        n = len(self.get_widgets())

        def callback(ratios):
            self.m_ratios = ratios
            self.on_update_view()

        return self.m_ratios, [(0.001, 10)] * n, 3, "Set Ratios", [
            "No.{0}".format(i + 1) for i in range(n)
        ], callback, QSize(400, 40 * (n + 1))

    @property
    def layout(self) -> Union[QPSLHBoxLayout, QPSLVBoxLayout]:
        return self.widget().layout()

    @property
    def scrollBar(self):
        if self.get_orientation() == Qt.Orientation.Horizontal:
            return self.horizontalScrollBar()
        else:
            return self.verticalScrollBar()


class QPSLHScrollList(QPSLScrollList):

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


class QPSLVScrollList(QPSLScrollList):

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


def make_QPSLScrollList_class(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Horizontal:
        return QPSLHScrollList
    else:
        return QPSLVScrollList
