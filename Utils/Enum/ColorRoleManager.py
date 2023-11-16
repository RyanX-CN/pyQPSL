from PyQt5.QtGui import QPalette
from .EnumManager import EnumManager

color_role_enum_manager = EnumManager(
    names=[
        "WindowText", "Foreground", "Button", "Light", "Midlight", "Dark",
        "Mid", "Text", "BrightText", "ButtonText", "Base", "Window",
        "Background", "Shadow", "Highlight", "HighlightedText", "Link",
        "LinkVisited", "AlternateBase", "ToolTipBase", "ToolTipText",
        "PlaceholderText", "NoRole", "NColorRoles"
    ],
    values=[
        QPalette.ColorRole.WindowText, QPalette.ColorRole.Foreground,
        QPalette.ColorRole.Button, QPalette.ColorRole.Light,
        QPalette.ColorRole.Midlight, QPalette.ColorRole.Dark,
        QPalette.ColorRole.Mid, QPalette.ColorRole.Text,
        QPalette.ColorRole.BrightText, QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.Base, QPalette.ColorRole.Window,
        QPalette.ColorRole.Background, QPalette.ColorRole.Shadow,
        QPalette.ColorRole.Highlight, QPalette.ColorRole.HighlightedText,
        QPalette.ColorRole.Link, QPalette.ColorRole.LinkVisited,
        QPalette.ColorRole.AlternateBase, QPalette.ColorRole.ToolTipBase,
        QPalette.ColorRole.ToolTipText, QPalette.ColorRole.PlaceholderText,
        QPalette.ColorRole.NoRole, QPalette.ColorRole.NColorRoles
    ])