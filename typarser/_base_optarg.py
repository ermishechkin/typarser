from __future__ import annotations

import typing
from typing import Callable, Literal, Optional, Union

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
            help: Optional[str],  # pylint: disable=redefined-builtin
    ) -> None:
        super().__init__(help=help)
        self._type = type
        self._nargs = nargs

    @property
    def type(self) -> Callable[[str], TYPE]:
        return self._type

    @property
    def nargs(self) -> Optional[NARGS]:
        return self._nargs

    def __set__(self, owner: NAMESPACE, value: TYPE):
        set_value(owner, self, value)
