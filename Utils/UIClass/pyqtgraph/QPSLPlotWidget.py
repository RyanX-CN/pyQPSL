from QPSLClass.Base import *
from ...BaseClass import *
from ...Enum import *
from .QPSLPlotItem import QPSLPlotItem
from .QPSLViewBox import QPSLViewBox


class QPSLPlotWidget(pyqtgraph.PlotWidget, QGraphicsView, QPSLWidgetBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        self.setup_logic()

    def __init__(self):
        super().__init__(plotItem=QPSLPlotItem().load_attr())

    def load_attr(self,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        self.setup_logic()
        return self

    def setup_logic(self):
        pass

    def add_item(self, item: pyqtgraph.PlotItem):
        self.plot_item().getViewBox().addItem(item)

    def remove_item(self, item: pyqtgraph.PlotItem):
        self.plot_item().getViewBox().removeItem(item)

    def plot_item(self) -> QPSLPlotItem:
        return self.getPlotItem()

    def viewbox(self) -> QPSLViewBox:
        return self.plot_item().viewbox()

    def scene(self) -> pyqtgraph.GraphicsScene:
        return super().scene()

    def prepare_custom_context_menu(self, menu: QMenu):
        super().prepare_custom_context_menu(menu)
        menu.addMenu(self.viewbox().make_context_menu())