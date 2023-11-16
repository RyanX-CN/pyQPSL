from PyQt5.QtCore import Qt
from .EnumManager import EnumManager

pen_style_enum_manager = EnumManager(
    names=[
        "NoPen", "SolidLine", "DashLine", "DotLine", "DashDotLine",
        "DashDotDotLine", "CustomDashLine", "MPenStyle"
    ],
    values=[
        Qt.PenStyle.NoPen, Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine,
        Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine,
        Qt.PenStyle.DashDotDotLine, Qt.PenStyle.CustomDashLine,
        Qt.PenStyle.MPenStyle
    ])