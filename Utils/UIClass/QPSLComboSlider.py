from QPSLClass.Base import *
from ..BaseClass import *
from .QPSLLabel import QPSLLabel
from .QPSLSlider import QPSLFloatSlider


class QPSLComboSlider(QPSLFloatSlider):

    def __init__(self):
        super().__init__()
        self.m_tooltip = QPSLLabel()
        self.m_tooltip.setWindowFlags(Qt.WindowType.CustomizeWindowHint
                                      | Qt.WindowType.FramelessWindowHint)
        self.m_tooltip.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground)
        self.set_tooltip_invisible()
        connect_direct(self.sig_value_mouse_hovered_at, self.set_tooltip)
        connect_direct(self.sig_entered, self.set_tooltip_visible)
        connect_direct(self.sig_left, self.set_tooltip_invisible)

    def set_tooltip_visible(self):
        self.m_tooltip.setVisible(True)

    def set_tooltip_invisible(self):
        self.m_tooltip.setVisible(False)

    def set_tooltip(self, value: float):
        self.m_tooltip.setText("{0:.{1}g}".format(value, self.m_decimals))
        self.m_tooltip.adjustSize()
        self.m_tooltip.move(QCursor.pos() - QPoint(0, 40))
        self.m_tooltip.raise_()