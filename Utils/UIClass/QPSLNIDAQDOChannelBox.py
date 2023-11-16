from Tool import *   
from .QPSLFrameList import QPSLHFrameList, QPSLVFrameList
from .pyqtgraph.QPSLPlotWidget import QPSLPlotWidget
from .QPSLComboBox import QPSLComboBox
from .QPSLSpinBox import QPSLSpinBox,QPSLDoubleSpinBox


class QPSLNIDAQDOChannelBox(QPSLHFrameList):
    
    def __init__(self, 
                 parent: QWidget, 
                 object_name: str, 
                 title: str = "",
                 text="line:"):
        super().__init__(parent=parent, object_name=object_name, title=title)
        self.add_widget(widget=QPSLPlotWidget(
            self,object_name="plot_data"))
        self.add_widget(widget=QPSLVFrameList(
            self,object_name="plot_config"))
        self.plot_config.add_widget(widget=QPSLComboBox(
            self,object_name="cbox_line",text=text))
        self.plot_config.add_widget(widget=QPSLSpinBox(self.plot_config,
                                    object_name="spin_cycle",
                                    prefix="cycle:",
                                    min=0,
                                    max=1000,
                                    value=50))
        self.plot_config.add_widget(widget=QPSLDoubleSpinBox(self.plot_config,
                                    object_name="spin_rate",
                                    prefix="duty rate: ",
                                    min=0,
                                    max=1,
                                    decimals=2,
                                    value=0.5))
        self.plot_config.add_widget(widget=QPSLSpinBox(self.plot_config,
                                    object_name="spin_delay",
                                    prefix="dealy: ",
                                    min=0,
                                    value=0))
        self.set_stretch(sizes=(3,2))
        self.spin_rate.setSingleStep(0.1)
        self.update_wave()
        for spin in self.spins:
            connect_direct(spin.sig_editing_finished,self.update_wave)

    def make_wave(self):
        cycle,delay,ratio = self.spin_cycle.value(
        ),self.spin_delay.value(),self.spin_rate.value()
        if ratio > 1:
            return None
        return numpy_array_shift(array=np.array([0] * int(ratio*cycle) + 
                                                [1] *(cycle - int(ratio*cycle))),
                                 right_shift=delay + cycle - int(ratio * cycle))
    
    def update_wave(self):
        arr =self.make_wave()
        if arr is None:
            return False
        self.plot_data.set_data(arr=arr)
        return True
        
    @property
    def plot_data(self) -> QPSLPlotWidget:
        return self.get_widget(0)

    @property
    def plot_config(self) -> QPSLVFrameList:
        return self.get_widget(1)
    
    @property
    def cbox_line(self) -> QPSLComboBox:
        return self.plot_config.get_widget(0)

    @property
    def spin_cycle(self) -> QPSLSpinBox:
        return self.plot_config.get_widget(1)

    @property
    def spin_rate(self) -> QPSLDoubleSpinBox:
        return self.plot_config.get_widget(2)

    @property
    def spin_delay(self) -> QPSLSpinBox:
        return self.plot_config.get_widget(3)
    
    @property
    def spins(self) -> List[Union[QPSLSpinBox,QPSLDoubleSpinBox]]:
        return [self.spin_cycle,self.spin_rate,self.spin_delay]