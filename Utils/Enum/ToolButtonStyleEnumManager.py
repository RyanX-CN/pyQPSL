from PyQt5.QtCore import Qt
from .EnumManager import EnumManager

toolbutton_style_enum_manager = EnumManager(
    names=[
        "ToolButtonIconOnly", "ToolButtonTextOnly", "ToolButtonTextBesideIcon",
        "ToolButtonTextUnderIcon", "ToolButtonFollowStyle"
    ],
    values=[
        Qt.ToolButtonStyle.ToolButtonIconOnly,
        Qt.ToolButtonStyle.ToolButtonTextOnly,
        Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        Qt.ToolButtonStyle.ToolButtonFollowStyle
    ])
