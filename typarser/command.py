from __future__ import annotations

from typing import (Any, Generic, Literal, Mapping, Optional, Type, TypeVar,
                    Union, overload)

from ._internal_namespace import register_commands
from .namespace import Namespace

NAMESPACE = TypeVar('NAMESPACE', bound=Namespace)
CMDS = TypeVar('CMDS', bound=Namespace, covariant=True)
RESULT = TypeVar('RESULT')
SELF = TypeVar('SELF', bound='Commands')


class Commands(Generic[CMDS, RESULT]):
    @overload
    def __init__(
        self: Commands[CMDS, CMDS],
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[True],
    ) -> None:
        ...

    @overload
    def __init__(
        self: Commands[CMDS, Optional[CMDS]],
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[False] = False,
    ) -> None:
        ...

    def __init__(self,
                 cmds: Mapping[str, Type[CMDS]],
                 *,
                 required: bool = False) -> None:
        self._cmds = cmds
        self._required = required

    @overload
    def __get__(self: SELF, owner: Literal[None], inst: Type[NAMESPACE]) \
            -> SELF:
        ...

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) \
            -> RESULT:
        ...

    def __get__(self: SELF, owner: Optional[NAMESPACE],
                inst: Type[NAMESPACE]) -> Union[SELF, RESULT]:
        raise NotImplementedError

    @property
    def entries(self) -> Mapping[str, Type[CMDS]]:
        return self._cmds

    @property
    def required(self) -> bool:
        return self._required

    def __set_name__(self, owner: Type[Namespace], name: str):
        register_commands(self, owner, name)

    # HACK: __init__ overloading doesn't work correctly for some linters.
    # Duplicate signatures for __new__ method.

    @overload
    def __new__(
        cls,
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[True],
    ) -> Commands[CMDS, CMDS]:
        ...

    @overload
    def __new__(
        cls,
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[False] = False,
    ) -> Commands[CMDS, Optional[CMDS]]:
        ...

    def __new__(cls, *args: Any, **kwargs: Any):
        # pylint: disable=unused-argument
        return object.__new__(cls)
