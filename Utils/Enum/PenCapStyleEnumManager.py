from PyQt5.QtCore import Qt
from .EnumManager import EnumManager

pen_cap_style_enum_manager = EnumManager(
    names=["FlatCap", "SquareCap", "RoundCap", "MPenCapStyle"],
    values=[
        Qt.PenCapStyle.FlatCap, Qt.PenCapStyle.SquareCap,
        Qt.PenCapStyle.RoundCap, Qt.PenCapStyle.MPenCapStyle
    ])