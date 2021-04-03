from __future__ import annotations

import typing
from typing import (Any, Generic, Literal, Optional, Type, TypeVar, Union,
                    overload)

from ._internal_namespace import get_value
from .errors import NamespaceNotRegisteredError

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from .namespace import Namespace
    SELF = TypeVar('SELF', bound='BaseComponent[Any, Any]')
    CLASS = TypeVar('CLASS')
    # pylint: enable=cyclic-import

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
                inst: Type[Namespace]) -> SELF:
        ...

    @overload
    def __get__(self, owner: Namespace, inst: Type[Namespace]) -> RESULT:
        ...

    @overload
    def __get__(self: SELF, owner: Optional[CLASS], inst: Type[CLASS]) -> SELF:
        ...

    def __get__(self: SELF, owner: Optional[Any],
                inst: Type[Any]) -> Union[SELF, RESULT]:
        if owner is None:
            return self
        try:
            return get_value(owner, self)
        except NamespaceNotRegisteredError:
            return self  # In case of usage outside namespace class

    def __set__(self, owner: Namespace, value: TYPE) -> None:
        raise AttributeError
