from QPSLClass.Base import *
from ..BaseClass import *
from ..Enum import *
from ..UIClass.QPSLDialog import QPSLDialog


class QPSLPenDialog(QPSLDialog):
    sig_pen_changed = pyqtSignal()
    sig_pen_changed_to = pyqtSignal(QPen)

    def __init__(self):
        super().__init__()
        self.m_pen = QPen()
        self.m_selecting_color = False

    def load_attr(self,
                  color: Optional[QColor] = None,
                  width: Optional[int] = None,
                  style: Optional[Qt.PenStyle] = None,
                  cap_style: Optional[Qt.PenCapStyle] = None,
                  join_style: Optional[Qt.PenJoinStyle] = None,
                  size: Optional[QSize] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(window_title=window_title,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        connect_direct(self.finished, self.to_delete)
        if color is not None:
            self.m_pen.setColor(color)
        if width is not None:
            self.m_pen.setWidth(width)
        if style is not None:
            self.m_pen.setStyle(style)
        if cap_style is not None:
            self.m_pen.setCapStyle(cap_style)
        if join_style is not None:
            self.m_pen.setJoinStyle(join_style)
        if size is None:
            size = self.default_size()
        self.setup_logic()
        self.resize(size)
        return self

    @classmethod
    def default_window_title(cls):
        return "Set Pen"

    @classmethod
    def default_size(cls):
        return QSize(240, 320)

    def setup_logic(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        color_button = QToolButton()
        color_button.setText("color...")
        color_button.setSizePolicy(QSizePolicy.Policy.Preferred,
                                   QSizePolicy.Policy.Preferred)
        color_button.clicked.connect(self.on_select_color)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setSizePolicy(QSizePolicy.Policy.Preferred,
                             QSizePolicy.Policy.Preferred)
        slider.setRange(1, 10)
        slider.setValue(self.get_width())
        connect_direct(slider.valueChanged, self.on_slider_move)
        slider.setToolTip("width = {0}".format(slider.value()))

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Style:"), 0, 0)
        combobox = QComboBox()
        combobox.setSizePolicy(QSizePolicy.Policy.Preferred,
                               QSizePolicy.Policy.Preferred)
        for value, name in pen_style_enum_manager.m_v2s.items():
            combobox.addItem(name, value)
        combobox.setCurrentText(
            pen_style_enum_manager.get_name(self.get_pen_style()))
        connect_direct(combobox.currentTextChanged, self.set_pen_style)
        grid_layout.addWidget(combobox, 0, 1)

        grid_layout.addWidget(QLabel("Cap Style:"), 1, 0)
        combobox = QComboBox()
        combobox.setSizePolicy(QSizePolicy.Policy.Preferred,
                               QSizePolicy.Policy.Preferred)
        for value, name in pen_cap_style_enum_manager.m_v2s.items():
            combobox.addItem(name, value)
        combobox.setCurrentText(
            pen_cap_style_enum_manager.get_name(self.get_pen_cap_style()))
        connect_direct(combobox.currentTextChanged, self.set_pen_cap_style)
        grid_layout.addWidget(combobox, 1, 1)

        grid_layout.addWidget(QLabel("Join Style:"), 2, 0)
        combobox = QComboBox()
        combobox.setSizePolicy(QSizePolicy.Policy.Preferred,
                               QSizePolicy.Policy.Preferred)
        for value, name in pen_join_style_enum_manager.m_v2s.items():
            combobox.addItem(name, value)
        combobox.setCurrentText(
            pen_join_style_enum_manager.get_name(self.get_pen_join_style()))
        connect_direct(combobox.currentTextChanged, self.set_pen_join_style)
        grid_layout.addWidget(combobox, 2, 1)

        label = QLabel()
        label.installEventFilter(self)

        buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                     | QDialogButtonBox.StandardButton.Cancel)
        connect_direct(buttonbox.accepted, self.accept)
        connect_direct(buttonbox.rejected, self.reject)

        layout.addWidget(color_button)
        layout.addWidget(slider)
        layout.addLayout(grid_layout)
        layout.addWidget(label)
        layout.addWidget(buttonbox)
        layout.setStretch(0, 1)
        layout.setStretch(1, 1)
        layout.setStretch(2, 3)
        layout.setStretch(3, 3)
        layout.setStretch(4, 1)

    def get_color(self):
        return self.m_pen.color()

    def set_color(self, color: QColor):
        self.m_pen.setColor(color)
        self.on_pen_changed()

    def get_width(self):
        return self.m_pen.width()

    def set_width(self, width: int):
        self.m_pen.setWidth(width)
        self.on_pen_changed()

    def get_pen_style(self):
        return self.m_pen.style()

    def set_pen_style(self, style: Union[Qt.PenStyle, str]):
        if isinstance(style, str):
            style = pen_style_enum_manager.get_value(name=style)
        self.m_pen.setStyle(style)
        self.on_pen_changed()

    def get_pen_cap_style(self):
        return self.m_pen.capStyle()

    def set_pen_cap_style(self, cap_style: Union[Qt.PenCapStyle, str]):
        if isinstance(cap_style, str):
            cap_style = pen_cap_style_enum_manager.get_value(name=cap_style)
        self.m_pen.setCapStyle(cap_style)
        self.on_pen_changed()

    def get_pen_join_style(self):
        return self.m_pen.joinStyle()

    def set_pen_join_style(self, join_style: Union[Qt.PenJoinStyle, str]):
        if isinstance(join_style, str):
            join_style = pen_join_style_enum_manager.get_value(name=join_style)
        self.m_pen.setJoinStyle(join_style)
        self.on_pen_changed()

    def on_select_color(self):
        self.m_selecting_color = True
        old_color = self.m_pen.color()
        dialog = QColorDialog(old_color, None)
        connect_direct(dialog.currentColorChanged, self.set_color)

        def reject_callback():
            self.set_color(old_color)

        connect_direct(dialog.rejected, reject_callback)
        dialog.exec()
        self.m_selecting_color = False
        if self.m_pen.color() != old_color:
            self.on_pen_changed()

    def on_slider_move(self):
        slider: QSlider = self.layout().itemAt(1).widget()
        val = slider.value()
        slider.setToolTip("width: {0}".format(val))
        self.set_width(width=val)

    def on_pen_changed(self):
        self.layout().itemAt(3).widget().update()
        if not self.m_selecting_color:
            self.sig_pen_changed.emit()
            self.sig_pen_changed_to.emit(self.m_pen)

    def eventFilter(self, label: QLabel, ev: QEvent) -> bool:
        if ev.type() == QEvent.Type.Paint:
            w, h = label.width(), label.height()
            painter = QPainter(label)
            painter.setPen(self.m_pen)
            painter.fillRect(0, 0, w, h, QColor("#ffffff"))
            path = QPainterPath(QPoint(10, 10))
            path.lineTo(10, h - 11)
            path.lineTo(w - 11, 10)
            path.arcTo(w // 2, 10, w - 20, h - 20, 90, 270)
            painter.drawPath(path)
        return super().eventFilter(label, ev)


class QPenDialog(QPSLPenDialog):

    def __init__(self, initial: QPen, parent: Optional[QWidget] = None):
        super().__init__()
        self.load_attr(color=initial.color(),
                       width=initial.width(),
                       style=initial.style(),
                       cap_style=initial.capStyle(),
                       join_style=initial.joinStyle())

    @staticmethod
    def pen_to_dict(pen: QPen):
        res = dict()
        res.update({"color": pen.color().name()})
        res.update({"width": pen.width()})
        res.update({"style": pen.style()})
        res.update({"cap_style": pen.capStyle()})
        res.update({"join_style": pen.joinStyle()})
        return res

    @staticmethod
    def pen_from_dict(dic: Dict):
        pen = QPen()
        color = dic.get("color")
        width = dic.get("width")
        style = dic.get("style")
        cap_style = dic.get("cap_style")
        join_style = dic.get("join_style")
        if color is not None:
            pen.setColor(QColor(color))
        if width is not None:
            pen.setWidth(width)
        if style is not None:
            pen.setStyle(style)
        if cap_style is not None:
            pen.setCapStyle(cap_style)
        if join_style is not None:
            pen.setJoinStyle(join_style)
        return pen
