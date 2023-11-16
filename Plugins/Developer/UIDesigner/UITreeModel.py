from Tool import *


class TreeModel(QAbstractItemModel):

    def __init__(self, parent: QPSLHFrameList):
        super().__init__()
        self.m_root_widget = parent

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.DisplayRole:
            item: QPSLWidgetBase = index.internalPointer()
            if index.column() == 0:
                return item.__class__.__name__
            else:
                return item.objectName()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section == 0:
                    return "class name"
                else:
                    return "object name"

    def index(self,
              row: int,
              column: int,
              parent: QModelIndex = ...) -> QModelIndex:
        if not parent.isValid():
            parent_widget = self.m_root_widget
        else:
            parent_widget = parent.internalPointer()
        if row >= len(parent_widget.get_widgets()):
            return QModelIndex()
        return self.createIndex(row, column,
                                parent_widget.get_widget(index=row))

    def parent(self, index: QModelIndex) -> QModelIndex:
        widget: QPSLWidgetBase = index.internalPointer()
        if widget == self.m_root_widget:
            return QModelIndex()
        parent_widget: QPSLWidgetBase = widget.qpsl_parent()
        if parent_widget == self.m_root_widget:
            return self.createIndex(-1, 0, parent_widget)
        parent_parent_widget: QPSLWidgetBase = parent_widget.qpsl_parent()
        return self.createIndex(parent_parent_widget.index_of(parent_widget),
                                0, parent_widget)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if not parent.isValid():
            parent_widget = self.m_root_widget
        else:
            parent_widget = parent.internalPointer()
        return len(parent_widget.get_widgets())

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1