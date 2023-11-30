from QPSLClass.Base import *
from ..BaseClass import *


class QPSLTableWidget(QTableWidget, QPSLFrameBase):

    def load_by_json(self, json: Dict):
        super().load_by_json(json)
        row = json.get("row")
        column = json.get("column")
        if row is None:
            row = self.default_row()
        if column is None:
            column = self.default_column()
        self.setRowCount(row)
        self.setColumnCount(column)

    def to_json(self):
        res: Dict = super().to_json()
        if self.rowCount() != self.default_row():
            res.update({"row": self.rowCount()})
        if self.columnCount() != self.default_column():
            res.update({"column": self.columnCount()})
        return res

    def load_attr(self,
                  row: Optional[int] = None,
                  column: Optional[int] = None,
                  frame_shape: Optional[QFrame.Shape] = None,
                  frame_shadow: Optional[QFrame.Shadow] = None,
                  h_size_policy: Optional[QSizePolicy.Policy] = None,
                  v_size_policy: Optional[QSizePolicy.Policy] = None):
        super().load_attr(frame_shape=frame_shape,
                          frame_shadow=frame_shadow,
                          h_size_policy=h_size_policy,
                          v_size_policy=v_size_policy)
        if row is None:
            row = self.default_row()
        if column is None:
            column = self.default_column()
        self.setRowCount(row)
        self.setColumnCount(column)
        return self

    @classmethod
    def default_row(cls):
        return 5

    @classmethod
    def default_column(cls):
        return 2

    @register_multi_integers_attribute(action_name="set row and column count")
    def row_and_column_count_attr(self):

        def callback(values: Tuple[int, int]):
            self.setRowCount(values[0])
            self.setColumnCount(values[1])

        return (
            self.rowCount(),
            self.columnCount()), [(1, 100)] * 2, "Set Row And Column Count", [
                "row count", "column count"
            ], callback, QSize(400, 120)