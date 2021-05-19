from __future__ import annotations

import typing
from typing import Callable, Generic, Iterable, Literal, Optional, Tuple, Union

from ._base import RESULT, TYPE, BaseComponent
from ._internal_namespace import set_value

if typing.TYPE_CHECKING:
    from ._base import Namespace
    from .action import Action
    NARGS = Union[int, Literal['*'], Literal['+'], Literal['?']]


class BaseOptArg(BaseComponent[TYPE, RESULT], Generic[TYPE, RESULT]):
    def __init__(
            self,
            *,
            type: Callable[[str], TYPE],  # pylint: disable=redefined-builtin
            nargs: Optional[NARGS],
            choices: Optional[Iterable[TYPE]],
            default: Optional[Union[RESULT, str]],
            metavar: Optional[Union[str, Tuple[str, ...]]],
            action: Optional[Action] = None,
            help: Optional[str],  # pylint: disable=redefined-builtin
    ) -> None:
        super().__init__(help=help)
        self._type = type
        self._nargs = nargs
        self._choices = tuple(choices) if choices else None
        self._default = default
        self._metavar = metavar
        self._action = action

    @property
    def type(self) -> Callable[[str], TYPE]:
        return self._type

    @property
    def nargs(self) -> Optional[NARGS]:
        return self._nargs

    @property
    def choices(self) -> Optional[Tuple[TYPE, ...]]:
        return self._choices

    @property
    def default(self) -> Optional[Union[RESULT, str]]:
        return self._default

    @property
    def metavar(self) -> Optional[Union[str, Tuple[str, ...]]]:
        return self._metavar

    @property
    def action(self) -> Optional[Action]:
        return self._action

    def __set__(self, owner: Namespace, value: TYPE):
        set_value(owner, self, value)
