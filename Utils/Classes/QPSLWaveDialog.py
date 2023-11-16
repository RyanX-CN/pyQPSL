from QPSLClass.Base import *
from QPSLClass.Base import Any
from ..BaseClass import *
from ..Enum import *
from ..UIClass.QPSLDialog import QPSLDialog


class AttrType(QObject):
    sig_value_changed = pyqtSignal()

    def __init__(self, name: str, initial: Any) -> None:
        super().__init__()
        self.m_name = name
        self.m_value = initial
        self.m_last_widget = None
        connect_direct(self.sig_value_changed, self.on_value_changed)

    def get_name(self):
        return self.m_name

    def get_value(self):
        return self.m_value

    def set_value(self, val):
        if val != self.get_value():
            self.m_value = val
            self.sig_value_changed.emit()

    def get_widget(self) -> QWidget:
        pass

    def on_value_changed(self):
        pass


class AttrType_Float(AttrType):

    def __init__(self,
                 name: str,
                 initial: Any,
                 _range: Tuple[float, float] = (-10, 10),
                 decimals: int = 4) -> None:
        super().__init__(name, initial)
        self.m_range = _range
        self.m_decimals = decimals

    def get_range(self):
        return self.m_range

    def get_decimals(self):
        return self.m_decimals

    def get_widget(self):
        widget = QDoubleSpinBox()
        widget.setKeyboardTracking(False)
        widget.setRange(*self.get_range())
        widget.setDecimals(self.get_decimals())
        widget.setValue(self.get_value())
        connect_direct(widget.valueChanged, self.set_value)
        self.m_last_widget = weakref.ref(widget)
        return widget

    def on_value_changed(self):
        val = self.get_value()
        if self.m_last_widget is not None:
            if val != self.m_last_widget().value():
                self.m_last_widget().setValue(val)
        return super().on_value_changed()


class AttrType_Integer(AttrType):

    def __init__(self,
                 name: str,
                 initial: Any,
                 _range: Tuple[int, int] = (0, 2000000)) -> None:
        super().__init__(name, initial)
        self.m_range = _range

    def get_range(self):
        return self.m_range

    def get_widget(self):
        widget = QSpinBox()
        widget.setKeyboardTracking(False)
        widget.setRange(*self.get_range())
        widget.setValue(self.get_value())
        connect_direct(widget.valueChanged, self.set_value)
        self.m_last_widget = weakref.ref(widget)
        return widget

    def on_value_changed(self):
        val = self.get_value()
        if self.m_last_widget is not None:
            if val != self.m_last_widget().value():
                self.m_last_widget().setValue(val)
        return super().on_value_changed()


class AttrType_File(AttrType):

    def get_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 2, 10, 2)
        widget.setLayout(layout)
        edit = QLabel(self.get_value())
        edit.setToolTip(self.get_value())
        layout.addWidget(edit)
        button = QToolButton()
        button.setText("...")
        button.setSizePolicy(QSizePolicy.Policy.Maximum,
                             QSizePolicy.Policy.Preferred)
        connect_direct(button.clicked, self.on_click_select_file)
        layout.addWidget(button)
        self.m_last_widget = weakref.ref(edit)
        return widget

    def on_click_select_file(self):
        file, _filter = QFileDialog.getOpenFileName(None, self.get_value())
        if file and file != self.get_value():
            self.set_value(val=file)

    def on_value_changed(self):
        val = self.get_value()
        if self.m_last_widget is not None:
            if val != self.m_last_widget().text():
                self.m_last_widget().setText(self.get_value())
                self.m_last_widget().setToolTip(self.get_value())
        return super().on_value_changed()


class QPSLWaveGenerator(QObject):
    sig_wave_changed = pyqtSignal()
    sig_wave_changed_to = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.m_attrs: List[AttrType] = []
        self.m_wave: np.ndarray = None

    def to_json(self):
        res = dict()
        res.update({"Type": self.get_name()})
        for attr in self.get_attrs():
            res.update({attr.get_name(): attr.get_value()})
        return res

    @classmethod
    def get_name(cls):
        return "Wave"

    def add_attr(self, attr: AttrType):
        self.m_attrs.append(attr)
        connect_direct(attr.sig_value_changed, self.generate_wave)
        return attr

    def get_attrs(self):
        return self.m_attrs

    def set_attrs(self, dic: Dict[str, Any]):
        for attr in self.get_attrs():
            if attr.get_name() in dic:
                attr.set_value(val=dic[attr.get_name()])

    def generate_wave(self):
        pass

    def get_wave(self):
        return self.m_wave

    def set_wave(self, wave: np.ndarray):
        self.m_wave = wave
        self.sig_wave_changed.emit()
        self.sig_wave_changed_to.emit(wave)


class QPSLConstantValueWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_value = self.add_attr(attr=AttrType_Float(
            name="Value", initial=0, _range=(-10, 10), decimals=4))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=2, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "Constant Value"

    def generate_wave(self):
        self.set_wave(
            np.repeat(self.m_attr_value.get_value(),
                      self.m_attr_length.get_value()))


class QPSLSineWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_min = self.add_attr(attr=AttrType_Float(
            name="Min", initial=-10, _range=(-10, 10), decimals=4))
        self.m_attr_max = self.add_attr(attr=AttrType_Float(
            name="Max", initial=10, _range=(-10, 10), decimals=4))
        self.m_attr_cycle = self.add_attr(attr=AttrType_Integer(
            name="Cycle", initial=1000, _range=(2, 2000000)))
        self.m_attr_phase = self.add_attr(attr=AttrType_Integer(
            name="Phase", initial=500, _range=(0, 2000000)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=3000, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "Sine Wave"

    def generate_wave(self):
        phase = self.m_attr_phase.get_value()
        cycle = self.m_attr_cycle.get_value()
        length = self.m_attr_length.get_value()
        min = self.m_attr_min.get_value()
        max = self.m_attr_max.get_value()
        self.set_wave(
            np.sin(
                np.linspace(start=phase % cycle * (np.pi * 2 / cycle),
                            stop=(phase % cycle + length) *
                            (np.pi * 2 / cycle),
                            num=length,
                            endpoint=False)) * ((max - min) / 2) +
            ((max + min) / 2))


class QPSLSquareWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_min = self.add_attr(attr=AttrType_Float(
            name="Min", initial=-10, _range=(-10, 10), decimals=4))
        self.m_attr_max = self.add_attr(attr=AttrType_Float(
            name="Max", initial=10, _range=(-10, 10), decimals=4))
        self.m_attr_cycle = self.add_attr(attr=AttrType_Integer(
            name="Cycle", initial=1000, _range=(2, 2000000)))
        self.m_attr_bottom_part = self.add_attr(attr=AttrType_Integer(
            name="Bottom Part", initial=300, _range=(0, 2000000)))
        self.m_attr_phase = self.add_attr(attr=AttrType_Integer(
            name="Phase", initial=100, _range=(0, 2000000)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=3000, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "Square Wave"

    def generate_wave(self):
        phase = self.m_attr_phase.get_value()
        cycle = self.m_attr_cycle.get_value()
        bottom_part = self.m_attr_bottom_part.get_value()
        length = self.m_attr_length.get_value()
        min = self.m_attr_min.get_value()
        max = self.m_attr_max.get_value()
        self.set_wave(
            np.where(
                np.arange(
                    start=phase % cycle, stop=phase % cycle + length, step=1) %
                cycle < bottom_part, min, max))


class QPSLTriangleWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_min = self.add_attr(attr=AttrType_Float(
            name="Min", initial=-10, _range=(-10, 10), decimals=4))
        self.m_attr_max = self.add_attr(attr=AttrType_Float(
            name="Max", initial=10, _range=(-10, 10), decimals=4))
        self.m_attr_cycle = self.add_attr(attr=AttrType_Integer(
            name="Cycle", initial=1000, _range=(2, 2000000)))
        self.m_attr_up_part = self.add_attr(attr=AttrType_Integer(
            name="Up Part", initial=300, _range=(0, 2000000)))
        self.m_attr_phase = self.add_attr(attr=AttrType_Integer(
            name="Phase", initial=100, _range=(0, 2000000)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=3000, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "Triangle Wave"

    def generate_wave(self):
        phase = self.m_attr_phase.get_value()
        cycle = self.m_attr_cycle.get_value()
        up_part = self.m_attr_up_part.get_value()
        length = self.m_attr_length.get_value()
        min = self.m_attr_min.get_value()
        max = self.m_attr_max.get_value()
        self.set_wave(
            np.tile(
                np.roll(
                    np.hstack((np.linspace(start=min,
                                           stop=max,
                                           num=up_part,
                                           endpoint=False),
                               np.linspace(start=max,
                                           stop=min,
                                           num=cycle - up_part,
                                           endpoint=False))), -phase % cycle),
                (length + cycle - 1) // cycle)[:length])


class QPSLTrapezoidWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_min = self.add_attr(attr=AttrType_Float(
            name="Min", initial=-10, _range=(-10, 10), decimals=4))
        self.m_attr_max = self.add_attr(attr=AttrType_Float(
            name="Max", initial=10, _range=(-10, 10), decimals=4))
        self.m_attr_cycle = self.add_attr(attr=AttrType_Integer(
            name="Cycle", initial=1000, _range=(2, 2000000)))
        self.m_attr_stage_number = self.add_attr(attr=AttrType_Integer(
            name="Stage Number", initial=300, _range=(0, 2000000)))
        self.m_attr_phase = self.add_attr(attr=AttrType_Integer(
            name="Phase", initial=100, _range=(0, 2000000)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=3000, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "Trapezoid Wave"

    def generate_wave(self):
        phase = self.m_attr_phase.get_value()
        cycle = self.m_attr_cycle.get_value()
        stage_number = self.m_attr_stage_number.get_value()
        length = self.m_attr_length.get_value()
        min = self.m_attr_min.get_value()
        max = self.m_attr_max.get_value()
        self.set_wave(
            np.tile(
                np.roll(
                    np.repeat(np.linspace(start=min,
                                          stop=max,
                                          num=stage_number,
                                          endpoint=False),
                              repeats=cycle // stage_number), -phase % cycle),
                (length + cycle - 1) // cycle)[:length])


class QPSLBiTrapezoidWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_min = self.add_attr(attr=AttrType_Float(
            name="Min", initial=-10, _range=(-10, 10), decimals=4))
        self.m_attr_max = self.add_attr(attr=AttrType_Float(
            name="Max", initial=10, _range=(-10, 10), decimals=4))
        self.m_attr_cycle = self.add_attr(attr=AttrType_Integer(
            name="Cycle", initial=1000, _range=(2, 2000000)))
        self.m_attr_stage_number = self.add_attr(attr=AttrType_Integer(
            name="Stage Number", initial=300, _range=(0, 2000000)))
        self.m_attr_phase = self.add_attr(attr=AttrType_Integer(
            name="Phase", initial=100, _range=(0, 2000000)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=3000, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "BiTrapezoid Wave"

    def generate_wave(self):
        phase = self.m_attr_phase.get_value()
        cycle = self.m_attr_cycle.get_value()
        stage_number = self.m_attr_stage_number.get_value()
        length = self.m_attr_length.get_value()
        min = self.m_attr_min.get_value()
        max = self.m_attr_max.get_value()
        self.set_wave(
            np.tile(
                np.roll(
                    np.repeat(np.hstack((np.linspace(start=min,
                                                     stop=max,
                                                     num=stage_number,
                                                     endpoint=False),
                                         np.linspace(start=max,
                                                     stop=min,
                                                     num=stage_number,
                                                     endpoint=False))),
                              repeats=cycle // (2 * stage_number)),
                    -phase % cycle), (length + cycle - 1) // cycle)[:length])


class QPSLFileWaveGenerator(QPSLWaveGenerator):

    def __init__(self):
        super().__init__()
        self.m_attr_file = self.add_attr(attr=AttrType_File(
            name="File",
            initial="{0}/Resources/wave.txt".format(QPSL_Working_Directory)))
        self.m_attr_length = self.add_attr(attr=AttrType_Integer(
            name="Length", initial=200, _range=(2, 2000000)))
        self.generate_wave()

    @classmethod
    def get_name(cls):
        return "File Wave"

    def generate_wave(self):
        arr = []
        file = self.m_attr_file.get_value()
        length = self.m_attr_length.get_value()
        with open(file, "rt") as f:
            for line in f.readlines():
                arr.extend(map(float, line.strip().split()))
        arr = np.tile(arr, (length + len(arr) - 1) // len(arr))
        self.set_wave(wave=arr)


class QPSLWaveDialog(QPSLDialog):
    sig_wave_changed = pyqtSignal()
    sig_wave_changed_to = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.m_wave: np.ndarray = None
        self.m_curve: pyqtgraph.PlotCurveItem = None

    def load_attr(self,
                  wave: Optional[Dict[str, Union[int, float, str]]] = None,
                  size: Optional[QSize] = None,
                  window_title: Optional[str] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(window_title=window_title,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        connect_direct(self.finished, self.to_delete)
        if wave is None:
            wave = self.default_wave()
        if size is None:
            size = self.default_size()
        self.setup_logic()
        for i in range(self.combobox_wave_type.count()):
            generator: QPSLWaveGenerator = self.combobox_wave_type.itemData(i)
            if generator.get_name() == wave.get("Type"):
                self.combobox_wave_type.setCurrentIndex(i)
                generator.set_attrs(dic=wave)
                break
        self.resize(size)
        return self

    @classmethod
    def default_window_title(cls):
        return "Set Wave"

    @classmethod
    def default_size(cls):
        return QSize(500, 300)

    @classmethod
    def default_wave(cls):
        return {"Type": "Constant Value", "Value": 3.1415926}

    def setup_logic(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.combobox_wave_type = QComboBox()
        self.table = QTableWidget()
        self.plot = pyqtgraph.PlotWidget()
        buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                     | QDialogButtonBox.StandardButton.Cancel)
        buttonbox.setSizePolicy(QSizePolicy.Policy.Preferred,
                                QSizePolicy.Policy.Preferred)
        layout.addWidget(self.combobox_wave_type)
        layout.addWidget(self.table)
        layout.addWidget(self.plot)
        layout.addWidget(buttonbox)

        self.combobox_wave_type.setSizePolicy(QSizePolicy.Policy.Preferred,
                                              QSizePolicy.Policy.Preferred)
        connect_direct(self.combobox_wave_type.currentIndexChanged,
                       self.on_wave_generator_changed)
        self.table.setColumnCount(1)
        self.table.horizontalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        connect_direct(buttonbox.accepted, self.accept)
        connect_direct(buttonbox.rejected, self.reject)

        self.register_wave_generator(QPSLConstantValueWaveGenerator)
        self.register_wave_generator(QPSLSineWaveGenerator)
        self.register_wave_generator(QPSLSquareWaveGenerator)
        self.register_wave_generator(QPSLTriangleWaveGenerator)
        self.register_wave_generator(QPSLTrapezoidWaveGenerator)
        self.register_wave_generator(QPSLBiTrapezoidWaveGenerator)
        self.register_wave_generator(QPSLFileWaveGenerator)

    def register_wave_generator(self, generator_type: type):
        generator: QPSLWaveGenerator = generator_type()
        generator.setParent(self)
        self.combobox_wave_type.addItem(generator.get_name(), generator)
        connect_direct(generator.sig_wave_changed_to, self.on_wave_changed)

    def on_wave_generator_changed(self, index: int):
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0) is not None:
                widget: QWidget = self.table.cellWidget(i, 0)
                widget.deleteLater()
                self.table.removeCellWidget(i, 0)
        generator: QPSLWaveGenerator = self.combobox_wave_type.itemData(index)
        self.table.clear()
        self.table.setRowCount(len(generator.get_attrs()))
        names = []
        for i, attr in enumerate(generator.get_attrs()):
            names.append(attr.get_name())
            self.table.setCellWidget(i, 0, attr.get_widget())
        self.table.setVerticalHeaderLabels(names)
        self.on_wave_changed(generator.get_wave())

    def on_wave_changed(self, wave: np.ndarray):
        if self.m_curve is None:
            self.m_curve = pyqtgraph.PlotCurveItem()
            self.plot.addItem(self.m_curve)
        self.m_wave = wave
        self.m_curve.setData(wave)
        self.sig_wave_changed.emit()
        self.sig_wave_changed_to.emit(wave)


class QWaveDialog(QPSLWaveDialog):

    def __init__(self,
                 initial: Dict[str, Union[int, float, str]],
                 parent: Optional[QWidget] = None):
        super().__init__()
        self.load_attr(wave=initial)

    def get_wave(self):
        return self.m_wave

    @classmethod
    def generate_wave_from_dict(cls, wave: Dict):
        for cls in [
                QPSLConstantValueWaveGenerator, QPSLSineWaveGenerator,
                QPSLSquareWaveGenerator, QPSLTriangleWaveGenerator,
                QPSLTrapezoidWaveGenerator, QPSLBiTrapezoidWaveGenerator,
                QPSLFileWaveGenerator
        ]:
            if cls.get_name() == wave.get("Type"):
                generator: QPSLWaveGenerator = cls()
                generator.set_attrs(dic=wave)
                QApplication.processEvents()
                return generator.get_wave()

    def get_generator_dict(self):
        generator: QPSLWaveGenerator = self.combobox_wave_type.currentData()
        generator.setParent(None)
        return generator