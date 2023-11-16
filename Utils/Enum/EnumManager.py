from typing import Generic, List, TypeVar, Union

QPSLEnumTypes = TypeVar("QPSLEnumTypes")


class EnumManager(Generic[QPSLEnumTypes]):

    def __init__(self, names: List[str], values: List[QPSLEnumTypes]) -> None:
        self.m_s2v = dict(zip(names, values))
        self.m_v2s = dict(zip(values, names))

    def get_name(self, value):
        return self.m_v2s.get(value)

    def get_value(self, name: str):
        return self.m_s2v.get(name)
