from QPSLClass.Base import *
from ..BaseClass import *


class QPSLSplitter(QSplitter, QPSLFrameBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        orientation = json.get("orientation")
        if orientation is None:
            orientation = self.default_orientation()
        self.setOrientation(orientation)
        if "widgets" in json:
            for dic in json.get("widgets"):
                self.add_widget(widget=QPSLObjectBase.from_json(dic))

    def to_json(self):
        res: Dict = super().to_json()
        if self.orientation() != self.default_orientation():
            res.update({"orientation": self.orientation()})
        if self.get_widgets():
            res.update({
                "widgets": [widget.to_json() for widget in self.get_widgets()]
            })
        return res

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
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
        self.setOrientation(orientation)
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

    def add_widget(self, widget: QPSLWidgetBase):
        self.addWidget(widget)

    def add_widgets(self, widgets: Iterable[QPSLWidgetBase]):
        for widget in widgets:
            self.add_widget(widget)

    def insert_widget(self, widget: QPSLWidgetBase, index: int):
        self.insertWidget(index, widget)

    def remove_widget(self, widget: QPSLWidgetBase):
        widget.setParent(None)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget(widget=widget)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        widget.setParent(None)
        widget.to_delete()
        widget.deleteLater()

    def remove_widgets_and_delete(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget_and_delete(widget=widget)

    def index_of(self, widget: QPSLWidgetBase):
        return self.indexOf(widget)

    def get_widget(self, index: int) -> QPSLWidgetBase:
        return self.widget(index)

    def get_widgets(self):
        return [self.get_widget(i) for i in range(self.count())]

    def set_widgets(self, widgets: List[QPSLWidgetBase]):
        self.clear_widgets()
        self.add_widgets(widgets=widgets)

    def clear_widgets(self):
        widgets = [self.widget(i) for i in range(self.count())]
        self.remove_widgets_and_delete(widgets=widgets)


class QPSLHSplitter(QPSLSplitter):

    def load_attr(self,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(orientation=Qt.Orientation.Horizontal,
                                 frame_shape=frame_shape,
                                 frame_shadow=frame_shadow,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)


class QPSLVSplitter(QPSLSplitter):

    def load_attr(self,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(orientation=Qt.Orientation.Vertical,
                                 frame_shape=frame_shape,
                                 frame_shadow=frame_shadow,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Vertical


def make_QPSLSplitter_class(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Horizontal:
        return QPSLHSplitter
    else:
        return QPSLVSplitter