from PyQt5.QtWidgets import QFrame
from .EnumManager import EnumManager

frame_shadow_enum_manager = EnumManager(
    names=["Plain", "Raised", "Sunken"],
    values=[QFrame.Shadow.Plain, QFrame.Shadow.Raised, QFrame.Shadow.Sunken])
