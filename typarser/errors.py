from typing import Any, Type


class NamespaceNotRegisteredError(Exception):
    def __init__(self, namespace_type: Type[Any]) -> None:
        super().__init__(f'Type {namespace_type} was not registered.'
                         ' Maybe __init_subclass__ was not called?')
