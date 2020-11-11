from __future__ import annotations

import typing
from typing import Generic, Literal, Optional, Type, TypeVar, Union, overload

from ._internal_namespace import get_value

if typing.TYPE_CHECKING:
    from .namespace import Namespace
    NAMESPACE = TypeVar('NAMESPACE', bound=Namespace)
    SELF = TypeVar('SELF', bound='BaseComponent')

TYPE = TypeVar('TYPE')
RESULT = TypeVar('RESULT')


class BaseComponent(Generic[TYPE, RESULT]):
    def __init__(
            self,
            *,
            help: Optional[str],  # pylint: disable=redefined-builtin
    ) -> None:
        self._help = help

    @property
    def help(self) -> Optional[str]:
        return self._help

    @overload
    def __get__(self: SELF, owner: Literal[None],
                inst: Type[NAMESPACE]) -> SELF:
        ...

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) -> RESULT:
        ...

    def __get__(
            self, owner: Optional[NAMESPACE], inst: Type[NAMESPACE]
    ) -> Union[BaseComponent[TYPE, RESULT], RESULT]:
        if owner is None:
            return self
        return get_value(owner, self)

    def __set__(self, owner: NAMESPACE, value: TYPE) -> None:
        raise AttributeError
