from __future__ import annotations

from typing import (Any, Dict, Literal, Mapping, Optional, Type, TypeVar,
                    overload)

from ._base import BaseComponent
from ._internal_namespace import register_component, register_library_class
from .errors import (CommandAlreayExistsError, CommandNotExistError,
                     InvalidCommandNameError)
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
        metavar: Optional[str] = None,
        help: Optional[str] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: Commands[CMDS, Optional[CMDS]],
        cmds: Mapping[str, Type[CMDS]],
        *,
        required: Literal[False] = False,
        metavar: Optional[str] = None,
        help: Optional[str] = None,
    ) -> None:
        ...

    # pylint: enable=redefined-builtin

    def __init__(
            self,
            cmds: Mapping[str, Type[CMDS]],
            *,
            required: bool = False,
            metavar: Optional[str] = None,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> None:
        super().__init__(help=help)
        self._required = required
        self._metavar = metavar
        self._cmds: Dict[str, Type[CMDS]] = {}
        for cmd_name, cmd_namespace in cmds.items():
            self.add(cmd_name, cmd_namespace)

    @property
    def entries(self) -> Mapping[str, Type[CMDS]]:
        return self._cmds

    @property
    def required(self) -> bool:
        return self._required

    @property
    def metavar(self) -> Optional[str]:
        return self._metavar

    def add(self, name: str, command: Type[CMDS]) -> None:
        if not is_valid_command_name(name):
            raise InvalidCommandNameError(name)
        if name in self._cmds:
            raise CommandAlreayExistsError(name)
        self._cmds[name] = command

    def remove(self, name: str) -> None:
        if name not in self._cmds:
            raise CommandNotExistError(name)
        del self._cmds[name]

    def __set_name__(self, owner: Type[Namespace], name: str):
        register_component(owner, name, self)

    # HACK: __init__ overloading doesn't work correctly for some linters.
    # Duplicate signatures for __new__ method.

    # pylint: disable=redefined-builtin,arguments-differ

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

    # pylint: enable=redefined-builtin,arguments-differ

    def __new__(cls, *args: Any, **kwargs: Any):
        # pylint: disable=unused-argument
        return object.__new__(cls)


def is_valid_command_name(name: str) -> bool:
    return name.isidentifier()


register_library_class('Commands', Commands)
