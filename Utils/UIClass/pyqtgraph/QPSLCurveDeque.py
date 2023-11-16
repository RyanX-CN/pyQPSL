from QPSLClass.Base import *
from ...BaseClass import *
from ..QPSLToolButton import QPSLToolButton
from .QPSLPlotCurveItem import QPSLPlotCurveItem


class QPSLCurveDeque(QPSLToolButton):
    sig_curve_added = pyqtSignal(QPSLPlotCurveItem)
    sig_curve_removed = pyqtSignal(QPSLPlotCurveItem)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        color = json.get("color")
        capacity = json.get("capacity")
        if color is None:
            color = self.default_color()
        else:
            color = QColor(color)
        if capacity is None:
            capacity = self.default_capacity()
        self.set_icon()
        self.set_color(color=color)
        self.set_capacity(capacity=capacity)
        connect_direct(self.sig_clicked, self.on_click_select_color)

    def to_json(self):
        res: Dict = super().to_json()
        if self.get_color() != self.default_color():
            res.update({"color": self.get_color().name()})
        if self.get_capacity() != self.default_capacity():
            res.update({"capacity": self.get_capacity()})
        return res

    def __init__(self):
        super().__init__()
        self.m_curves = deque()
        self.m_color = self.default_color()
        self.m_capacity = self.default_capacity()
        self.m_action_clear_data = QAction("clear data")
        connect_direct(self.m_action_clear_data.triggered, self.clear_data)
        self.m_action_clear_curves = QAction("clear curves")
        connect_direct(self.m_action_clear_curves.triggered, self.clear_curves)
        self.action_dict.update(
            {self.m_action_clear_data.text(): self.m_action_clear_data})
        self.action_dict.update(
            {self.m_action_clear_curves.text(): self.m_action_clear_curves})

    def load_attr(self,
                  deque_name: Optional[str] = None,
                  color: Optional[QColor] = None,
                  capacity: Optional[int] = None,
                  style: Optional[Qt.ToolButtonStyle] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(style=style,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if deque_name is None:
            deque_name = self.default_deque_name()
        if color is None:
            color = self.default_color()
        if capacity is None:
            capacity = self.default_capacity()
        self.set_icon()
        self.set_deque_name(deque_name=deque_name)
        self.set_color(color=color)
        self.set_capacity(capacity=capacity)
        connect_direct(self.sig_clicked, self.on_click_select_color)
        return self

    def to_delete(self):
        self.clear_curves()
        return super().to_delete()

    @classmethod
    def default_deque_name(cls):
        return "deque unnamed"

    @classmethod
    def default_color(cls):
        return QColor("#ffffff")

    @classmethod
    def default_capacity(cls):
        return 100

    @staticmethod
    def get_curve_icon(color: QColor):
        w, h, pen_width = 100, 20, 3
        pixmap = QPixmap(w + pen_width + 10, h + pen_width + 10)
        pixmap.fill(QColor("#00000000"))
        painter = QPainter(pixmap)
        painter.setPen(QPen(color, pen_width))
        painter_path = QPainterPath(
            QPoint(pen_width // 2 + 5,
                   pixmap.height() // 2))
        for i in range(w):
            painter_path.lineTo(
                QPoint(
                    pen_width // 2 + i + 6,
                    pixmap.height() // 2 +
                    h // 2 * math.sin(i * 2 * math.pi / w)))
        painter.drawPath(painter_path)
        return pixmap

    def get_deque_name(self):
        return self.text()

    def set_deque_name(self, deque_name: str):
        self.setText(deque_name)

    def get_color(self):
        return self.m_color

    def set_color(self, color: QPen):
        if color == self.m_color:
            return
        self.m_color = color
        self.set_icon()
        for curve in self.m_curves:
            curve: QPSLPlotCurveItem
            curve.setPen(color)

    def set_icon(self):
        pixmap = self.get_curve_icon(color=self.get_color())
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())

    def get_capacity(self):
        return self.m_capacity

    def set_capacity(self, capacity: int):
        self.m_capacity = capacity
        while len(self.m_curves) > capacity:
            self.sig_curve_removed.emit(self.m_curves.popleft())

    def append_data(self, x: np.ndarray, y: np.ndarray):
        if len(self.m_curves) < self.get_capacity():
            curve = QPSLPlotCurveItem().load_attr(x=x,
                                                  y=y,
                                                  pen=self.get_color())
            self.sig_curve_added.emit(curve)
        else:
            curve: QPSLPlotCurveItem = self.m_curves.popleft()
            curve.setData(x=x, y=y)
        self.m_curves.append(curve)

    def set_data(self, x: np.ndarray, y: np.ndarray):
        self.clear_data()
        if not self.m_curves:
            curve = QPSLPlotCurveItem().load_attr(x=x,
                                                  y=y,
                                                  pen=self.get_color())
            self.sig_curve_added.emit(curve)
        else:
            curve: QPSLPlotCurveItem = self.m_curves.popleft()
            curve.setData(x=x, y=y)
        self.m_curves.append(curve)

    def get_curves(self) -> deque:
        return self.m_curves

    def get_curve(self, index: int):
        return self.m_curves[index]

    def clear_curves(self):
        while self.m_curves:
            self.sig_curve_removed.emit(self.m_curves.popleft())

    def clear_data(self):
        for curve in self.m_curves:
            curve: QPSLPlotCurveItem
            curve.clear()
            curve.update()

    def on_click_select_color(self):
        old_color = self.get_color()
        dialog = QColorDialog(old_color, None)

        def reject_callback():
            self.set_color(color=old_color)

        connect_direct(dialog.currentColorChanged, self.set_color)
        connect_direct(dialog.rejected, reject_callback)
        dialog.exec()

    def filter_of_attr(self, attr):
        if attr is QPSLToolButton.text_attribute:
            return False
        return super().filter_of_attr(attr)

    @register_single_text_attribute(action_name="set deque name")
    def deque_name_attr(self):
        return self.get_deque_name(
        ), "Set Deque Name", "Deque Name", self.set_deque_name, QSize(400, 80)

    @register_single_integer_attribute(action_name="set capacity")
    def capacity_attr(self):
        return self.get_capacity(), (
            1, 200), "Set Capacity", "Capacity", self.set_capacity, QSize(
                400, 80)

    @register_dialog_attribute(action_name="set color")
    def color_attr(self):
        return self.get_color(
        ), QColorDialog, "Set Dialog", QColorDialog.currentColorChanged, self.set_color
