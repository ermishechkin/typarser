from __future__ import annotations

from typing import (Generic, Literal, Mapping, Optional, Type, TypeVar, Union,
                    overload)

from .namespace import Namespace

NAMESPACE = TypeVar('NAMESPACE', bound=Namespace)
CMDS = TypeVar('CMDS', bound=Namespace, covariant=True)
SELF = TypeVar('SELF', bound='Commands')


class Commands(Generic[CMDS]):
    def __init__(self, cmds: Mapping[str, Type[CMDS]]) -> None:
        self._cmds = cmds

    @overload
    def __get__(self: SELF, owner: Literal[None], inst: Type[NAMESPACE]) \
            -> SELF:
        ...

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) \
            -> CMDS:
        ...

    def __get__(self: SELF, owner: Optional[NAMESPACE],
                inst: Type[NAMESPACE]) -> Union[SELF, CMDS]:
        raise NotImplementedError

    @property
    def entries(self) -> Mapping[str, Type[CMDS]]:
        return self._cmds
