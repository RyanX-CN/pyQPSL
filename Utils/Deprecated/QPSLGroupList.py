from QPSLClass.Base import *
from ..BaseClass import *
from .QPSLGroupBox import QPSLGroupBox
from .QPSLWidget import QPSLWidget
from .QPSLLayout import QPSLHBoxLayout, QPSLVBoxLayout, QPSLBoxLayout


class QPSLLinearGroupList(QPSLGroupBox):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        orientation = json.get("orientation")
        spacing = json.get("spacing")
        if orientation is None:
            orientation = self.default_orientation()
        if spacing is None:
            spacing = self.default_spacing()
        self.set_orientation(orientation=orientation)
        self.set_spacing(spacing=spacing)
        if "widgets" in json:
            for dic in json.get("widgets"):
                self.add_widget(widget=QPSLObjectBase.from_json(dic))
        if "stretch" in json:
            self.layout.set_stretch(
                sizes=str_to_int_tuple(json.get("stretch")))

    def to_json(self):
        res = super().to_json()
        if self.m_orientation != self.default_orientation():
            res.update({"orientation": self.m_orientation})
        if self.layout.spacing() != self.default_spacing():
            res.update({"spacing": self.layout.spacing()})
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
            raise TypeError(
                "QPSLLinearGroupList may not be directly instantiated")
        return super().__new__(cls, *args, **kwargs)

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
                  spacing: Optional[int] = None,
                  title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(title=title,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if orientation is None:
            orientation = self.default_orientation()
        if spacing is None:
            spacing = self.default_spacing()
        self.set_orientation(orientation=orientation)
        self.set_spacing(spacing=spacing)
        return self

    @classmethod
    def is_container(cls):
        return True

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal

    @classmethod
    def default_spacing(cls):
        return 0

    def set_orientation(self, orientation: Qt.Orientation):
        self.m_orientation = orientation
        self.setLayout(QPSLBoxLayout(orientation=orientation)())

    def get_orientation(self):
        return self.m_orientation

    def add_widget(self, widget: QPSLWidget):
        self.layout.add_widget(widget=widget)

    def add_widgets(self, widgets: List[QPSLWidget]):
        self.layout.add_widgets(widgets=widgets)

    def remove_widget(self, widget: QPSLWidget):
        widget.setParent(None)
        self.layout.remove_widget(widget=widget)

    def remove_widgets(self, widgets: List[QPSLWidget]):
        for widget in widgets:
            widget.setParent(None)
        self.layout.remove_widgets(widgets=widgets)

    def remove_widget_and_delete(self, widget: QPSLWidget):
        widget.setParent(None)
        self.layout.remove_widget_and_delete(widget=widget)

    def remove_widgets_and_delete(self, widgets: List[QPSLWidget]):
        for widget in widgets:
            widget.setParent(None)
        self.layout.remove_widgets_and_delete(widgets=widgets)

    def clear_widgets(self):
        self.layout.clear_widgets()

    def get_widget(self, index: int):
        return self.layout.get_widget(index=index)

    def get_widgets(self):
        return self.layout.get_widgets()

    def set_spacing(self, spacing: int):
        self.layout.setSpacing(spacing)

    def set_stretch(self, sizes: Tuple[int, ...]):
        self.layout.set_stretch(sizes=sizes)

    @attribute_factory_decorator(cls_name="QPSLLinearGroupList",
                                 name="spacing...",
                                 window_title="Set Spacing")
    def spacing_spinbox_factory(self):
        box = QWidget()
        layout = QHBoxLayout()
        box.setLayout(layout)
        old_spacing = self.layout.spacing()

        slider = QSlider(orientation=Qt.Orientation.Horizontal)
        slider.setRange(0, 30)
        slider.setValue(old_spacing)

        def get_repr():
            return "spacing = {0}".format(slider.value())

        label = QLabel(get_repr())
        layout.addWidget(label, 1)
        layout.addWidget(slider, 10)

        def callback(value):
            label.setText(get_repr())
            self.set_spacing(spacing=value)

        def reject_callback():
            self.set_spacing(spacing=old_spacing)

        connect_direct(slider.valueChanged, callback)
        return box, reject_callback

    @attribute_factory_decorator(cls_name="QPSLLinearGroupList",
                                 name="stretch...",
                                 window_title="Set Stretch")
    def stretch_box_factory(self):
        box = QWidget()
        layout = QGridLayout()
        box.setLayout(layout)
        old_stretch = [
            self.layout.stretch(i) for i in range(len(self.get_widgets()))
        ]

        labels: List[QLabel] = []
        sliders: List[QSlider] = []

        def get_repr(i):
            return "No.{0} = {1}".format(i, sliders[i].value())

        for i in range(len(self.get_widgets())):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 30)
            slider.setValue(old_stretch[i])
            sliders.append(slider)
            label = QLabel(get_repr(i))
            labels.append(label)
            layout.addWidget(label, i, 0)
            layout.addWidget(slider, i, 1)

        def callback(*arg):
            for i in range(len(self.get_widgets())):
                labels[i].setText(get_repr(i))
                self.layout.setStretch(i, sliders[i].value())

        def reject_callback():
            self.layout.set_stretch(sizes=old_stretch)

        for i in range(len(self.get_widgets())):
            connect_direct(sliders[i].valueChanged, callback)

        return box, reject_callback

    @property
    def layout(self) -> Union[QPSLHBoxLayout, QPSLVBoxLayout]:
        return super().layout()


class QPSLHGroupList(QPSLLinearGroupList):

    def load_attr(self,
                  spacing: Optional[int] = None,
                  title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(orientation=Qt.Orientation.Horizontal,
                                 spacing=spacing,
                                 title=title,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)


class QPSLVGroupList(QPSLLinearGroupList):

    def load_attr(self,
                  spacing: Optional[int] = None,
                  title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        return super().load_attr(orientation=Qt.Orientation.Vertical,
                                 spacing=spacing,
                                 title=title,
                                 h_size_policy=h_size_policy,
                                 v_size_policy=v_size_policy)

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Vertical


def make_QPSLGroupList_class(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Horizontal:
        return QPSLHGroupList
    else:
        return QPSLVGroupList