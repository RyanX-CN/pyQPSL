from PyQt5 import QtGui
from QPSLClass.Base import *
from QPSLClass.Base import Optional, Tuple
from ..BaseClass import *


class QPSLSlider(QSlider, QPSLWidgetBase):
    sig_mouse_hovered_ratio = pyqtSignal(tuple)
    sig_clicked_ratio = pyqtSignal(tuple)
    sig_entered = pyqtSignal()
    sig_left = pyqtSignal()

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        orientation = json.get("orientation")
        _range = str_to_int_tuple(json.get("range"))
        value = json.get("value")
        mouse_tracking = json.get("mouse_tracking")
        if orientation is None:
            orientation = self.default_orientation()
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if mouse_tracking is None:
            mouse_tracking = self.default_mouse_tracking()
        self.setOrientation(orientation)
        self.setRange(*_range)
        self.setValue(value)
        self.setMouseTracking(mouse_tracking)

    def to_json(self):
        res: Dict = super().to_json()
        if self.orientation() != self.default_orientation():
            res.update({"orientation": self.orientation()})
        if (self.minimum(), self.maximum()) != self.default_range():
            res.update(
                {"range": tuple_to_str((self.minimum(), self.maximum()))})
        if self.value() != self.default_value():
            res.update({"value": self.value()})
        if self.hasMouseTracking() != self.default_mouse_tracking():
            res.update({"mouse_tracking": self.hasMouseTracking()})
        return res

    def __init__(self):
        super().__init__()
        self.m_dragable = self.default_dragable()

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
                  _range: Optional[Tuple[int, int]] = None,
                  value: Optional[int] = None,
                  mouse_tracking: Optional[bool] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if orientation is None:
            orientation = self.default_orientation()
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if mouse_tracking is None:
            mouse_tracking = self.default_mouse_tracking()
        self.setOrientation(orientation)
        self.setRange(*_range)
        self.setValue(value)
        self.setMouseTracking(mouse_tracking)
        return self

    @classmethod
    def default_orientation(cls):
        return Qt.Orientation.Horizontal

    @classmethod
    def default_range(cls):
        return (0, 100)

    @classmethod
    def default_value(cls):
        return 10

    @classmethod
    def default_mouse_tracking(cls):
        return True

    @classmethod
    def default_dragable(cls):
        return True

    def set_dragable(self, b: bool):
        self.m_dragable = b

    def convert_position_to_ratio(self, pos: QPointF):
        if self.orientation() == Qt.Orientation.Horizontal:
            f = (pos.x() - 6) / (self.width() - 13)
        else:
            f = 1 - (pos.y() - 6) / (self.height() - 13)
        return (1 - f, f)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.sig_clicked_ratio.emit(
                self.convert_position_to_ratio(pos=event.pos()))
        if self.m_dragable:
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.sig_mouse_hovered_ratio.emit(
            self.convert_position_to_ratio(pos=event.pos()))
        return super().mouseMoveEvent(event)

    def wheelEvent(self, e: QWheelEvent) -> None:
        if self.m_dragable:
            return super().wheelEvent(e)

    def enterEvent(self, event: QMouseEvent):
        if self.isEnabled():
            self.sig_entered.emit()
        return super().enterEvent(event)

    def leaveEvent(self, event: QMouseEvent):
        if self.isEnabled():
            self.sig_left.emit()
        return super().leaveEvent(event)

    @register_integer_range_attribute(action_name="set range")
    def range_attribute(self):
        return (self.minimum(),
                self.maximum()), "Set Range", self.setRange, QSize(400, 120)


class QPSLFloatSlider(QPSLSlider):
    sig_value_clicked_at = pyqtSignal(float)
    sig_value_mouse_hovered_at = pyqtSignal(float)
    sig_value_changed_to = pyqtSignal(float)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        decimals = json.get("m_decimals")
        _range = str_to_float_tuple(json.get("m_range"))
        value = json.get("m_value")
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if decimals is None:
            decimals = self.default_decimals()
        self.m_range = _range
        self.m_true_value = value
        self.set_decimals(decimals=decimals)

    def to_json(self):
        res: Dict = super().to_json()
        if "range" in res:
            res.pop("range")
        if "value" in res:
            res.pop("value")
        if self.get_decimals() != self.default_decimals():
            res.update({"m_decimals": self.get_decimals()})
        if self.get_range() != self.default_range():
            res.update({"m_range": tuple_to_str(self.get_range())})
        if self.get_value() != self.default_value():
            res.update({"m_value": self.get_value()})
        return res

    def __init__(self):
        super().__init__()
        self.m_decimals = self.default_decimals()
        self.m_range = self.default_range()
        self.m_true_value = self.default_value()
        connect_direct(self.sig_clicked_ratio, self.on_ratio_clicked)
        connect_direct(self.sig_mouse_hovered_ratio,
                       self.on_ratio_mouse_hovered)

    def load_attr(self,
                  orientation: Optional[Qt.Orientation] = None,
                  _range: Optional[Tuple[int, int]] = None,
                  value: Optional[int] = None,
                  decimals: Optional[int] = 3,
                  mouse_tracking: Optional[bool] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(orientation=orientation,
                          mouse_tracking=mouse_tracking,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if decimals is None:
            decimals = self.default_decimals()
        self.m_range = _range
        self.m_true_value = value
        self.set_decimals(decimals=decimals)
        return self

    @classmethod
    def default_decimals(cls):
        return 3

    @classmethod
    def default_range(cls):
        return (0, 100)

    @classmethod
    def default_value(cls):
        return 10

    @classmethod
    def default_dragable(cls):
        return False

    def set_decimals(self, decimals: int):
        self.m_decimals = decimals
        super().setRange(0, 10**decimals)
        self.update_slider()

    def set_range(self, minimum: int, maximum: int) -> None:
        self.m_range = minimum, maximum
        self.update_slider()

    def set_value(self, val: float):
        if self.m_range[0] <= val <= self.m_range[1]:
            self.m_true_value = val
            self.update_slider()

    def get_decimals(self):
        return self.m_decimals

    def get_range(self):
        return self.m_range

    def get_value(self):
        return self.m_true_value

    def update_slider(self):
        self.setValue(self.map_to_internal_value(true_value=self.m_true_value))
        self.sig_value_changed_to.emit(self.m_true_value)

    def ratio_to_true_value(self, ratio: Tuple[float, float]):
        return ratio[0] * self.m_range[0] + ratio[1] * self.m_range[1]

    def map_to_internal_value(self, true_value: float):
        return int(self.maximum() * ((true_value - self.m_range[0]) /
                                     (self.m_range[1] - self.m_range[0])))

    def on_ratio_clicked(self, ratio: Tuple[float, float]):
        val = self.ratio_to_true_value(ratio=ratio)
        if self.minimum() <= self.map_to_internal_value(
                true_value=val) <= self.maximum():
            self.sig_value_clicked_at.emit(val)

    def on_ratio_mouse_hovered(self, ratio: Tuple[float, float]):
        true_val = self.ratio_to_true_value(ratio=ratio)
        val = self.map_to_internal_value(true_value=true_val)
        if self.minimum() <= val <= self.maximum():
            self.sig_value_mouse_hovered_at.emit(true_val)

    @register_single_integer_attribute(action_name="set decimals")
    def decimals_attribute(self):
        return self.get_decimals(), (
            0,
            9), "Set Decimals", "Decimals", self.set_decimals, QSize(400, 80)

    @register_float_range_attribute(action_name="set range")
    def range_attribute(self):
        return self.get_range(), "Set Range", self.set_range, QSize(400, 120)

    def filter_of_attr(self, attr):
        if attr is QPSLSlider.range_attribute:
            return False
        return super().filter_of_attr(attr=attr)
