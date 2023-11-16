from PyQt5.QtWidgets import QFrame
from .EnumManager import EnumManager

frame_shape_enum_manager = EnumManager(
    names=[
        "NoFrame", "Box", "Panel", "WinPanel", "HLine", "VLine", "StyledPanel"
    ],
    values=[
        QFrame.Shape.NoFrame, QFrame.Shape.Box, QFrame.Shape.Panel,
        QFrame.Shape.WinPanel, QFrame.Shape.HLine, QFrame.Shape.VLine,
        QFrame.Shape.StyledPanel
    ])
