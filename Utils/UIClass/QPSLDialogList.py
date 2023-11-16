from QPSLClass.Base import *
from ..BaseClass import *
from .QPSLLayout import *
from .QPSLDialog import QPSLDialog


class QPSLDialogList(QPSLDialog):

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
        if "stretch" in json:
            self.set_stretch(sizes=str_to_int_tuple(json.get("stretch")))
        connect_direct(self.finished, self.to_delete)

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
        stretches = list(
            self.layout.stretch(i) for i in range(len(self.get_widgets())))
        if any(stretches):
            res.update({"stretch": tuple_to_str(stretches)})
        return res

    def __new__(cls, *args, **kwargs):
        if cls is __class__:
            raise TypeError("{0} may not be directly instantiated".format(
                cls.__name__))
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

    def to_delete(self):
        self.clear_widgets()
        return super().to_delete()

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(window_title=window_title,
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
        connect_direct(self.finished, self.to_delete)
        return self

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal

    @classmethod
    def default_margins(cls):
        return 0, 0, 0, 0

    @classmethod
    def default_spacing(cls):
        return 0

    def set_orientation(self, orientation: Qt.Orientation):
        self.m_orientation = orientation
        self.setLayout(QPSLBoxLayout(orientation=orientation)())
        self.set_contents_margins(0, 0, 0, 0)

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

    def set_stretch(self, sizes: Tuple[int, ...]):
        self.layout.set_stretch(sizes=sizes)

    def add_widget(self, widget: QPSLWidgetBase):
        self.layout.add_widget(widget=widget)

    def add_widgets(self, widgets: List[QPSLWidgetBase]):
        self.layout.add_widgets(widgets=widgets)

    def insert_widget(self, widget: QPSLWidgetBase, index: int):
        self.layout.insert_widget(widget=widget, index=index)

    def remove_widget(self, widget: QPSLWidgetBase):
        widget.setParent(None)
        self.layout.remove_widget(widget=widget)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            widget.setParent(None)
        self.layout.remove_widgets(widgets=widgets)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        widget.setParent(None)
        self.layout.remove_widget_and_delete(widget=widget)

    def remove_widgets_and_delete(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            widget.setParent(None)
        self.layout.remove_widgets_and_delete(widgets=widgets)

    def clear_widgets(self):
        self.layout.clear_widgets()

    def get_widget(self, index: int):
        return self.layout.get_widget(index=index)

    def get_widgets(self):
        return self.layout.get_widgets()

    def index_of(self, widget: QPSLWidgetBase):
        return self.layout.index_of(widget=widget)

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

    @register_multi_integers_attribute(action_name="set stretches")
    def stretches_attribute(self):
        n = len(self.get_widgets())
        return list(self.layout.stretch(i)
                    for i in range(n)), [(0, 100)] * n, "Set Stretches", [
                        "No.{0}".format(i + 1) for i in range(n)
                    ], self.set_stretch, QSize(400, 40 * (n + 1))

    @property
    def layout(self) -> Union[QPSLHBoxLayout, QPSLVBoxLayout]:
        return super().layout()


class QPSLHDialogList(QPSLDialogList):

    def load_attr(self,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(spacing=spacing,
                                 margins=margins,
                                 window_title=window_title,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)


class QPSLVDialogList(QPSLDialogList):

    def load_attr(self,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  spacing: Optional[int] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(spacing=spacing,
                                 margins=margins,
                                 window_title=window_title,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Vertical


def make_QPSLDialogList_class(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Horizontal:
        return QPSLHDialogList
    else:
        return QPSLVDialogList