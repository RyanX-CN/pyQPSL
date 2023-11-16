from PyQt5.QtCore import Qt
from .EnumManager import EnumManager

h_alignment_enum_manager = EnumManager(
    names=[
        "AlignLeft", "AlignRight", "AlignHCenter", "AlignJustify",
        "AlignHorizontal_Mask"
    ],
    values=[
        Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignRight,
        Qt.AlignmentFlag.AlignHCenter, Qt.AlignmentFlag.AlignJustify,
        Qt.AlignmentFlag.AlignHorizontal_Mask
    ])
v_alignment_enum_manager = EnumManager(names=[
    "AlignTop", "AlignBottom", "AlignVCenter", "AlignBaseline",
    "AlignVertical_Mask"
],
                                       values=[
                                           Qt.AlignmentFlag.AlignTop,
                                           Qt.AlignmentFlag.AlignBottom,
                                           Qt.AlignmentFlag.AlignVCenter,
                                           Qt.AlignmentFlag.AlignBaseline,
                                           Qt.AlignmentFlag.AlignVertical_Mask
                                       ])
