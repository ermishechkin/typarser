from __future__ import annotations

from typing import Generic, Literal, Optional, Type, TypeVar, overload

NAMESPACE = TypeVar('NAMESPACE')
TYPE = TypeVar('TYPE')
SELF = TypeVar('SELF', bound='Option')


class Option(Generic[TYPE]):
    def __init__(
            self,
            *,
            type: Type[TYPE],  # pylint: disable=redefined-builtin
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        self._type = type
        self._help = help

    @overload
    def __get__(self: SELF, owner: Literal[None], inst: Type[NAMESPACE]) \
            -> SELF:
        pass

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) -> TYPE:
        pass

    def __get__(self, owner: Optional[NAMESPACE], inst: Type[NAMESPACE]):
        pass

    def __set__(self, owner: NAMESPACE, value: TYPE):
        raise AttributeError('Attributes are read-only')

    @property
    def type(self) -> Type[TYPE]:
        return self._type

    @property
    def help(self) -> Optional[str]:
        return self._help
