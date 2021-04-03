from __future__ import annotations

import typing
from typing import Any, Literal, NoReturn, Optional, Type, Union, overload

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from .namespace import Namespace

    # pylint: enable=cyclic-import


class RemovedComponent:
    @overload
    def __get__(self, owner: Literal[None],
                inst: Type[Namespace]) -> RemovedComponent:
        ...

    @overload
    def __get__(self, owner: Namespace, inst: Type[Namespace]) -> NoReturn:
        ...

    def __get__(self, owner: Optional[Namespace],
                inst: Type[Namespace]) -> Union[NoReturn, RemovedComponent]:
        if owner is None:
            return self
        raise AttributeError

    def __set__(self, owner: Namespace, value: Any) -> None:
        raise AttributeError
