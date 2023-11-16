from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from .EnumManager import EnumManager

pen_join_style_enum_manager = EnumManager(names=[
    "MiterJoin", "BevelJoin", "RoundJoin", "MPenJoinStyle", "SvgMiterJoin"
],
                                         values=[
                                             Qt.PenJoinStyle.MiterJoin,
                                             Qt.PenJoinStyle.BevelJoin,
                                             Qt.PenJoinStyle.RoundJoin,
                                             Qt.PenJoinStyle.MPenJoinStyle,
                                             Qt.PenJoinStyle.SvgMiterJoin
                                         ])
