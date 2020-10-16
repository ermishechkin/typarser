from __future__ import annotations

from typing import Generic, Literal, Optional, Type, TypeVar, overload

NAMESPACE = TypeVar('NAMESPACE')
TYPE = TypeVar('TYPE')
SELF = TypeVar('SELF', bound='Option')
RESULT = TypeVar('RESULT')


class Option(Generic[TYPE, RESULT]):
    # pylint: disable=redefined-builtin

    @overload
    def __init__(
        self: Option[TYPE, Optional[TYPE]],
        *,
        type: Type[TYPE],
        required: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, TYPE],
        *,
        type: Type[TYPE],
        required: Literal[True],
        help: Optional[str] = None,
    ):
        ...

    # pylint: enable=redefined-builtin

    def __init__(
            self,
            *,
            type: Type[TYPE],  # pylint: disable=redefined-builtin
            required: bool = False,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        self._type = type
        self._required = required
        self._help = help

    @overload
    def __get__(self: SELF, owner: Literal[None], inst: Type[NAMESPACE]) \
            -> SELF:
        ...

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) -> RESULT:
        ...

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

    @property
    def required(self) -> bool:
        return self._required
