from __future__ import annotations

from typing import Any, Literal, Mapping, Optional, Type, TypeVar, overload

from ._base import BaseComponent
from ._internal_namespace import register_commands, register_library_class
from .namespace import Namespace

CMDS = TypeVar('CMDS', bound=Namespace, covariant=True)
RESULT = TypeVar('RESULT')


class Commands(BaseComponent[CMDS, RESULT]):
    # pylint: disable=redefined-builtin

    @overload
    def __init__(
        self: Commands[CMDS, CMDS],
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[True],
        help: Optional[str] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: Commands[CMDS, Optional[CMDS]],
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[False] = False,
        help: Optional[str] = None,
    ) -> None:
        ...

    # pylint: enable=redefined-builtin

    def __init__(
            self,
            cmds: Mapping[str, Type[CMDS]],
            *,
            required: bool = False,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> None:
        super().__init__(help=help)
        self._cmds = cmds
        self._required = required

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

    # pylint: disable=redefined-builtin

    @overload
    def __new__(
        cls,
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[True],
        help: Optional[str] = None,
    ) -> Commands[CMDS, CMDS]:
        ...

    @overload
    def __new__(
        cls,
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Commands[CMDS, Optional[CMDS]]:
        ...

    # pylint: enable=redefined-builtin

    def __new__(cls, *args: Any, **kwargs: Any):
        # pylint: disable=unused-argument
        return object.__new__(cls)


register_library_class('Commands', Commands)
