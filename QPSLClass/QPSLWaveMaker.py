from QPSLClass.Base import *
from QPSLClass.QPSLGroupList import QPSLHorizontalGroupList, QPSLVerticalGroupList
from Utils.UIClass.QPSLComboBox import QPSLComboBox
from Utils.UIClass.QPSLSpinBox import QPSLSpinBox, QPSLDoubleSpinBox
from QPSLClass.QPSLStaticPlot import QPSLStaticPlot


class QPSLWaveMaker(QPSLHorizontalGroupList):

    def __init__(self, parent: QWidget, object_name: str):
        super(QPSLWaveMaker, self).__init__(parent=parent,
                                            object_name=object_name)
        self.setupUi()
        self.setupLogic()
        self.on_choose_wave_type(wave_type="constant")

    def setupUi(self):
        self.add_widget(widget=QPSLStaticPlot(self, object_name="plot"))
        self.add_widget(widget=QPSLVerticalGroupList(self, object_name="box_para"))
        self.box_para.add_widget(
            widget=QPSLComboBox(self.box_para, object_name="cbox_wave_type"))
        self.cbox_wave_type.set_texts(texts=[
            "constant", "sine", "rect", "triangle", "trapezoid", "bitrapezoid"
        ])
        self.box_para.add_widget(
            widget=QPSLDoubleSpinBox(self.box_para,
                                     object_name="spin_min",
                                     min=-10,
                                     max=10,
                                     value=-2,
                                     prefix="min:"))
        self.box_para.add_widget(
            widget=QPSLDoubleSpinBox(self.box_para,
                                     object_name="spin_max",
                                     min=-10,
                                     max=10,
                                     value=4,
                                     prefix="max:"))
        self.box_para.add_widget(widget=QPSLSpinBox(self.box_para,
                                                    object_name="spin_cycle",
                                                    min=1,
                                                    max=10000000,
                                                    value=1000,
                                                    prefix="cycle:"))
        self.box_para.add_widget(widget=QPSLSpinBox(self.box_para,
                                                    object_name="spin_phase",
                                                    min=0,
                                                    max=10000000,
                                                    value=1000,
                                                    prefix="phase:"))
        self.box_para.add_widget(widget=QPSLSpinBox(self.box_para,
                                                    object_name="spin_phase",
                                                    min=1,
                                                    max=10000000,
                                                    value=1000,
                                                    prefix="phase:"))
        self.box_para.set_stretch(sizes=(1, 1, 1, 1, 1, 1))

    def setupLogic(self):
        connect_direct(self.cbox_wave_type.currentTextChanged[str],
                       self.on_choose_wave_type)
        for spin in self.spins:
            connect_direct(spin.sig_value_changed, self.update_wave)

    def on_choose_wave_type(self, wave_type: str):
        if wave_type == "constant":
            self.spin_min.setPrefix("val:")
            self.spin_max.hide()
            self.spin_cycle.hide()
            self.spin_phase.hide()
            self.spin_para.hide()
        else:
            self.spin_min.setPrefix("min:")
            self.spin_max.show()
            self.spin_cycle.show()
            self.spin_phase.show()
            if wave_type == "sine":
                self.spin_para.hide()
            else:
                self.spin_para.show()
                if wave_type == "trapezoid" or wave_type == "bitrapezoid":
                    self.spin_para.setPrefix("stage number:")
                elif wave_type == "rect" or wave_type == "triangle":
                    self.spin_para.setPrefix("ratio:")
        self.update_wave()

    def make_wave(self) -> Optional[np.ndarray]:
        wave_type = self.cbox_wave_type.currentText()
        if wave_type == "constant":
            return np.array([self.spin_min.value()] * self.spin_cycle.value())
        elif wave_type == "sine":
            min, max, cycle, phase = self.spin_min.value(
            ), self.spin_max.value(), self.spin_cycle.value(
            ), self.spin_phase.value()
            return numpy_array_shift(array=np.sin(
                np.linspace(start=0, stop=np.pi * 2, num=cycle,
                            endpoint=False)) * (max - min) / 2 +
                                     (min + max) / 2,
                                     right_shift=cycle - phase)
        elif wave_type == "rect":
            min, max, cycle, phase, ratio = self.spin_min.value(
            ), self.spin_max.value(), self.spin_cycle.value(
            ), self.spin_phase.value(), self.spin_para.value()
            if ratio > cycle: return None
            return numpy_array_shift(array=np.array([min] * ratio + [max] *
                                                    (cycle - ratio)),
                                     right_shift=cycle - phase)
        elif wave_type == "triangle":
            min, max, cycle, phase, ratio = self.spin_min.value(
            ), self.spin_max.value(), self.spin_cycle.value(
            ), self.spin_phase.value(), self.spin_para.value()
            if ratio > cycle: return None
            return numpy_array_shift(array=np.hstack(
                (np.linspace(start=min, stop=max, num=ratio, endpoint=False),
                 np.linspace(start=max,
                             stop=min,
                             num=cycle - ratio,
                             endpoint=False))),
                                     right_shift=cycle - phase)
        elif wave_type == "trapezoid":
            min, max, cycle, phase, stage_num = self.spin_min.value(
            ), self.spin_max.value(), self.spin_cycle.value(
            ), self.spin_phase.value(), self.spin_para.value()
            if cycle % stage_num != 0: return None
            return numpy_array_shift(array=np.repeat(
                np.linspace(start=min, stop=max, num=stage_num, endpoint=True),
                cycle // stage_num),
                                     right_shift=cycle - phase)
        elif wave_type == "bitrapezoid":
            min, max, cycle, phase, stage_num = self.spin_min.value(
            ), self.spin_max.value(), self.spin_cycle.value(
            ), self.spin_phase.value(), self.spin_para.value()
            if cycle % (stage_num * 2) != 0: return None
            return numpy_array_shift(array=np.hstack(
                (np.repeat(
                    np.linspace(start=min,
                                stop=max,
                                num=stage_num,
                                endpoint=True), cycle // (stage_num * 2)),
                 np.repeat(
                     np.linspace(start=max,
                                 stop=min,
                                 num=stage_num,
                                 endpoint=True), cycle // (stage_num * 2)))),
                                     right_shift=cycle - phase)
        else:
            return None

    def update_wave(self):
        arr = self.make_wave()
        if arr is None:
            return False
        self.graph.set_data(arr=arr)
        return True

    @property
    def graph(self) -> QPSLStaticPlot:
        return self.get_widget(0)

    @property
    def box_para(self) -> QPSLVerticalGroupList:
        return self.get_widget(1)

    @property
    def cbox_wave_type(self) -> QPSLComboBox:
        return self.box_para.get_widget(0)

    @property
    def spin_min(self) -> QPSLDoubleSpinBox:
        return self.box_para.get_widget(1)

    @property
    def spin_max(self) -> QPSLDoubleSpinBox:
        return self.box_para.get_widget(2)

    @property
    def spin_cycle(self) -> QPSLSpinBox:
        return self.box_para.get_widget(3)

    @property
    def spin_phase(self) -> QPSLSpinBox:
        return self.box_para.get_widget(4)

    @property
    def spin_para(self) -> QPSLSpinBox:
        return self.box_para.get_widget(5)

    @property
    def spins(self) -> List[Union[QPSLSpinBox, QPSLDoubleSpinBox]]:
        return [
            self.spin_min, self.spin_max, self.spin_cycle, self.spin_phase,
            self.spin_para
        ]
