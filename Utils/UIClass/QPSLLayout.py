from QPSLClass.Base import *
from ..BaseClass import *


class QPSLBoxLayoutBase(QPSLObjectBase):

    def __init__(self):
        super().__init__()
        self.m_widgets: List[QPSLWidgetBase] = []

    def add_widget(self, widget: QPSLWidgetBase):
        self.m_widgets.append(widget)
        QBoxLayout.addWidget(self, widget)

    def add_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.add_widget(widget=widget)

    def insert_widget(self, widget: QPSLWidgetBase, index: int):
        self.m_widgets.insert(index, widget)
        QBoxLayout.insertWidget(self, index, widget)

    def remove_widget(self, widget: QPSLWidgetBase):
        self.m_widgets.remove(widget)
        QBoxLayout.removeWidget(self, widget)

    def remove_widgets(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget(widget=widget)

    def remove_widget_and_delete(self, widget: QPSLWidgetBase):
        self.m_widgets.remove(widget)
        QBoxLayout.removeWidget(self, widget)
        widget.to_delete()
        widget.deleteLater()

    def remove_widgets_and_delete(self, widgets: List[QPSLWidgetBase]):
        for widget in widgets:
            self.remove_widget_and_delete(widget=widget)

    def clear_widgets(self):
        self.remove_widgets_and_delete(self.m_widgets.copy())

    def index_of(self, widget: QPSLWidgetBase):
        return self.m_widgets.index(widget)

    def set_stretch(self, sizes: Tuple[int, ...]):
        for i, size in enumerate(sizes):
            QBoxLayout.setStretch(self, i, size)

    def get_widget(self, index: int):
        return self.m_widgets[index]

    def get_widgets(self):
        return self.m_widgets


class QPSLHBoxLayout(QHBoxLayout, QPSLBoxLayoutBase):
    pass


class QPSLVBoxLayout(QVBoxLayout, QPSLBoxLayoutBase):
    pass


def QPSLBoxLayout(orientation: Qt.Orientation):
    if orientation == Qt.Orientation.Vertical:
        return QPSLVBoxLayout
    else:
        return QPSLHBoxLayout
