from QPSLClass.Base import *
from ..BaseClass import *


class QPSLSpinBox(QSpinBox, QPSLWidgetBase):
    sig_value_changed = pyqtSignal()
    sig_value_changed_to = pyqtSignal(int)
    sig_editing_finished = pyqtSignal()
    sig_editing_finished_at = pyqtSignal(int)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        _range = str_to_int_tuple(json.get("range"))
        value = json.get("value")
        prefix = json.get("prefix")
        suffix = json.get("suffix")
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if prefix is None:
            prefix = self.default_prefix()
        if suffix is None:
            suffix = self.default_suffix()
        self.setRange(*_range)
        self.setValue(value)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)

    def to_json(self):
        res: Dict = super().to_json()
        if (self.minimum(), self.maximum()) != self.default_range():
            res.update(
                {"range": tuple_to_str((self.minimum(), self.maximum()))})
        if self.value() != self.default_value():
            res.update({"value": self.value()})
        if self.prefix() != self.default_prefix():
            res.update({"prefix": self.prefix()})
        if self.suffix() != self.default_suffix():
            res.update({"suffix": self.suffix()})
        return res

    def __init__(self, ):
        super().__init__()
        self.setKeyboardTracking(False)
        connect_direct(self.valueChanged, self.on_value_changed)
        connect_direct(self.editingFinished, self.on_editing_finished)

    def load_attr(self,
                  _range: Optional[Tuple[int, int]] = None,
                  value: Optional[int] = None,
                  prefix: Optional[str] = None,
                  suffix: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if prefix is None:
            prefix = self.default_prefix()
        if suffix is None:
            suffix = self.default_suffix()
        self.setRange(*_range)
        self.setValue(value)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)
        return self

    @classmethod
    def default_range(cls):
        return (-1000000, 1000000)

    @classmethod
    def default_value(cls):
        return 0

    @classmethod
    def default_prefix(cls):
        return ""

    @classmethod
    def default_suffix(cls):
        return ""

    def set_read_only(self, b: bool):
        self.setReadOnly(b)
        if b:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        else:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

    def on_value_changed(self):
        self.sig_value_changed.emit()
        self.sig_value_changed_to.emit(self.value())

    def on_editing_finished(self):
        self.sig_editing_finished.emit()
        self.sig_editing_finished_at.emit(self.value())

    @register_single_text_attribute(action_name="set prefix")
    def prefix_attribute(self):
        return self.prefix(), "Set Prefix", "Prefix", self.setPrefix, QSize(
            400, 80)

    @register_single_text_attribute(action_name="set suffix")
    def suffix_attribute(self):
        return self.suffix(), "Set Suffix", "Suffix", self.setSuffix, QSize(
            400, 80)

    @register_integer_range_attribute(action_name="set range")
    def range_attribute(self):
        return (self.minimum(),
                self.maximum()), "Set Range", self.setRange, QSize(400, 120)


class QPSLDoubleSpinBox(QDoubleSpinBox, QPSLWidgetBase):
    sig_value_changed = pyqtSignal()
    sig_value_changed_to = pyqtSignal(float)
    sig_editing_finished = pyqtSignal()
    sig_editing_finished_at = pyqtSignal(float)

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        decimals = json.get("decimals")
        _range = str_to_float_tuple(json.get("range"))
        value = json.get("value")
        prefix = json.get("prefix")
        suffix = json.get("suffix")
        if decimals is None:
            decimals = self.default_decimals()
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if prefix is None:
            prefix = self.default_prefix()
        if suffix is None:
            suffix = self.default_suffix()
        self.setDecimals(decimals)
        self.setRange(*_range)
        self.setValue(value)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)

    def to_json(self):
        res: Dict = super().to_json()
        if self.decimals() != self.default_decimals():
            res.update({"decimals": self.decimals()})
        if (self.minimum(), self.maximum()) != self.default_range():
            res.update(
                {"range": tuple_to_str((self.minimum(), self.maximum()))})
        if self.value() != self.default_value():
            res.update({"value": self.value()})
        if self.prefix() != self.default_prefix():
            res.update({"prefix": self.prefix()})
        if self.suffix() != self.default_suffix():
            res.update({"suffix": self.suffix()})
        return res

    def __init__(self):
        super().__init__()
        self.setKeyboardTracking(False)
        connect_direct(self.valueChanged, self.on_value_changed)
        connect_direct(self.editingFinished, self.on_editing_finished)

    def load_attr(self,
                  _range: Optional[Tuple[float, float]] = None,
                  value: Optional[float] = None,
                  prefix: Optional[str] = None,
                  suffix: Optional[str] = None,
                  decimals: Optional[int] = 3,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if _range is None:
            _range = self.default_range()
        if value is None:
            value = self.default_value()
        if prefix is None:
            prefix = self.default_prefix()
        if suffix is None:
            suffix = self.default_suffix()
        if decimals is None:
            decimals = self.default_decimals()
        self.setDecimals(decimals)
        self.setRange(*_range)
        self.setValue(value)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)
        return self

    @classmethod
    def default_range(cls):
        return (-1000000, 1000000)

    @classmethod
    def default_value(cls):
        return 0

    @classmethod
    def default_prefix(cls):
        return ""

    @classmethod
    def default_suffix(cls):
        return ""

    @classmethod
    def default_decimals(cls):
        return 3

    def set_read_only(self, b: bool):
        self.setReadOnly(b)
        if b:
            self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        else:
            self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)

    def on_value_changed(self):
        self.sig_value_changed.emit()
        self.sig_value_changed_to.emit(self.value())

    def on_editing_finished(self):
        self.sig_editing_finished.emit()
        self.sig_editing_finished_at.emit(self.value())

    def edit_value(self, value: float):
        self.setValue(value)

    @register_single_text_attribute(action_name="set prefix")
    def prefix_attribute(self):
        return self.prefix(), "Set Prefix", "Prefix", self.setPrefix, QSize(
            400, 80)

    @register_single_text_attribute(action_name="set suffix")
    def suffix_attribute(self):
        return self.suffix(), "Set Suffix", "Suffix", self.setSuffix, QSize(
            400, 80)

    @register_single_integer_attribute(action_name="set decimals")
    def decimals_attribute(self):
        return self.decimals(), (
            0,
            9), "Set Decimals", "Decimals", self.setDecimals, QSize(400, 80)

    @register_float_range_attribute(action_name="set range")
    def range_attribute(self):
        return (self.minimum(),
                self.maximum()), "Set Range", self.setRange, QSize(400, 120)
