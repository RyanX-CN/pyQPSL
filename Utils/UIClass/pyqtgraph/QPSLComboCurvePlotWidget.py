from QPSLClass.Base import *
from ...BaseClass import *
from ..QPSLFrameList import QPSLHFrameList, QPSLVFrameList
from ..QPSLPushButton import QPSLPushButton
from ..QPSLScrollArea import QPSLHScrollArea
from .QPSLCurveDeque import QPSLCurveDeque
from .QPSLPlotCurveItem import QPSLPlotCurveItem
from .QPSLPlotWidget import QPSLPlotWidget


class QPSLComboCurvePlotWidget(QPSLVFrameList):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__()
        self.m_action_clear_data = QAction("clear data")
        connect_direct(self.m_action_clear_data.triggered, self.clear_data)
        self.m_action_clear_curves = QAction("clear curves")
        connect_direct(self.m_action_clear_curves.triggered, self.clear_curves)
        self.action_dict.update(
            {self.m_action_clear_data.text(): self.m_action_clear_data})
        self.action_dict.update(
            {self.m_action_clear_curves.text(): self.m_action_clear_curves})

    def load_attr(self,
                  spacing: Optional[int] = None,
                  margins: Optional[Tuple[int, int, int, int]] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(spacing=spacing,
                          margins=margins,
                          frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        self.add_widget(widget=QPSLPlotWidget().load_attr())
        self.add_widget(widget=QPSLHFrameList().load_attr())
        self.get_widget(1).add_widget(widget=QPSLHScrollArea().load_attr())
        self.get_widget(1).add_widget(widget=QPSLPushButton().load_attr(
            text="add"))
        self.get_widget(1).add_widget(widget=QPSLPushButton().load_attr(
            text="remove"))
        self.get_widget(1).add_widget(widget=QPSLPushButton().load_attr(
            text="clear"))
        self.setup_logic()
        return self

    def setup_logic(self):
        self.plot_widget: QPSLPlotWidget = self.get_widget(0).remove_type()
        self.scroll: QPSLHScrollArea = self.get_widget(1).get_widget(
            0).remove_type()
        self.button_add_deque: QPSLPushButton = self.get_widget(1).get_widget(
            1).remove_type()
        self.button_remove_deque: QPSLPushButton = self.get_widget(
            1).get_widget(2).remove_type()
        for deque in self.scroll.get_widgets():
            deque: QPSLCurveDeque
            connect_direct(deque.sig_curve_added, self.add_curve)
            connect_direct(deque.sig_curve_removed, self.remove_curve)
        connect_direct(self.button_add_deque.sig_clicked,
                       self.on_click_add_deque)
        connect_direct(self.button_remove_deque.sig_clicked,
                       self.on_click_remove_deque)

    def add_deque(self, deque: QPSLCurveDeque):
        self.scroll.add_widget(widget=deque)
        connect_direct(deque.sig_curve_added, self.add_curve)
        connect_direct(deque.sig_curve_removed, self.remove_curve)

    def remove_deque(self, deque: QPSLCurveDeque):
        self.scroll.remove_widget_and_delete(widget=deque)

    def get_deques(self) -> List[QPSLCurveDeque]:
        return self.scroll.get_widgets()

    def get_deque(self, index: int) -> QPSLCurveDeque:
        return self.scroll.get_widget(index=index)

    def insert_deque(self, deque: QPSLCurveDeque, index: int):
        self.scroll.insert_widget(widget=deque, index=index)

    def clear_curves(self):
        for deque in self.get_deques():
            deque.clear_curves()

    def clear_data(self):
        for deque in self.get_deques():
            deque.clear_data()

    def add_curve(self, curve: QPSLPlotCurveItem):
        self.plot_widget.add_item(item=curve)

    def remove_curve(self, curve: QPSLPlotCurveItem):
        self.plot_widget.remove_item(item=curve)

    def on_click_add_deque(self):
        self.add_deque(deque=QPSLCurveDeque().load_attr())

    def on_click_remove_deque(self):
        self.remove_deque(deque=self.get_deques()[-1])
