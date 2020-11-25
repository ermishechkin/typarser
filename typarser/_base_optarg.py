from __future__ import annotations

import typing
from typing import Callable, Iterable, Literal, Optional, Tuple, Union

from ._base import RESULT, TYPE, BaseComponent
from ._internal_namespace import set_value

if typing.TYPE_CHECKING:
    from ._base import NAMESPACE
    NARGS = Union[int, Literal['*'], Literal['+'], Literal['?']]


class BaseOptArg(BaseComponent[TYPE, RESULT]):
    def __init__(
            self,
            *,
            type: Callable[[str], TYPE],  # pylint: disable=redefined-builtin
            nargs: Optional[NARGS],
            choices: Optional[Iterable[TYPE]],
            default: Optional[TYPE],
            metavar: Optional[Union[str, Tuple[str, ...]]],
            help: Optional[str],  # pylint: disable=redefined-builtin
    ) -> None:
        super().__init__(help=help)
        self._type = type
        self._nargs = nargs
        self._choices = tuple(choices) if choices else None
        self._default = default
        self._metavar = metavar

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
    def default(self) -> Optional[TYPE]:
        return self._default

    @property
    def metavar(self) -> Optional[Union[str, Tuple[str, ...]]]:
        return self._metavar

    def __set__(self, owner: NAMESPACE, value: TYPE):
        set_value(owner, self, value)