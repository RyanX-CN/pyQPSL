from PyQt5.QtWidgets import QAbstractItemView
from .EnumManager import EnumManager

selection_mode_enum_manager = EnumManager(
    names=[
        "NoSelection", "SingleSelection", "MultiSelection",
        "ExtendedSelection", "ContiguousSelection"
    ],
    values=[
        QAbstractItemView.SelectionMode.NoSelection,
        QAbstractItemView.SelectionMode.SingleSelection,
        QAbstractItemView.SelectionMode.MultiSelection,
        QAbstractItemView.SelectionMode.ExtendedSelection,
        QAbstractItemView.SelectionMode.ContiguousSelection
    ])