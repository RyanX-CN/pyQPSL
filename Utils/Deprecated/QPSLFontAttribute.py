from QPSLClass.Base import *


class QPSLFontAttribute:

    def __init__(self, default_font: Union[str, QFont] = "Arial"):
        self.m_dict: Dict[QObject, Union[str, QFont]] = dict()
        self.m_default_font = default_font

    def __set_name__(self, owner: type, name: str):
        pass

    def __get__(self, instance: QObject, owner: type):
        return self.m_dict.get(instance, self.m_default_font)

    def __set__(self, instance: QObject, font: Union[str, QFont]):
        self.m_dict[instance] = font
