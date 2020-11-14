from __future__ import annotations

import typing
from typing import (Any, Callable, List, Literal, Optional, Type, Union,
                    overload)

from ._base_optarg import RESULT, TYPE, BaseOptArg
from ._internal_namespace import register_argument, register_library_class
from .namespace import Namespace

if typing.TYPE_CHECKING:
    from ._base_optarg import NARGS


class Argument(BaseOptArg[TYPE, RESULT]):
    # pylint: disable=redefined-builtin

    @overload
    def __init__(
        self: Argument[TYPE, TYPE],
        *,
        type: Callable[[str], TYPE],
        nargs: Literal[None] = None,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Argument[TYPE, Optional[TYPE]],
        *,
        type: Callable[[str], TYPE],
        nargs: Literal['?'],
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Argument[TYPE, List[TYPE]],
        *,
        type: Callable[[str], TYPE],
        nargs: Union[int, Literal['*'], Literal['+']],
        help: Optional[str] = None,
    ):
        ...

    # pylint: enable=redefined-builtin

    def __init__(
            self: Argument[TYPE, TYPE],
            *,
            type: Callable[[str], TYPE],  # pylint: disable=redefined-builtin
            nargs: Optional[NARGS] = None,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        super().__init__(type=type, nargs=nargs, help=help)

    def __set_name__(self, owner: Type[Namespace], name: str):
        register_argument(self, owner, name)

    # HACK: __init__ overloading doesn't work correctly for some linters.
    # Duplicate signatures for __new__ method.

    # pylint: disable=redefined-builtin

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        nargs: Literal[None] = None,
        help: Optional[str] = None,
    ) -> Argument[TYPE, TYPE]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        nargs: Literal['?'],
        help: Optional[str] = None,
    ) -> Argument[TYPE, Optional[TYPE]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        nargs: Union[int, Literal['*'], Literal['+']],
        help: Optional[str] = None,
    ) -> Argument[TYPE, List[TYPE]]:
        ...

    # pylint: enable=redefined-builtin

    def __new__(cls, *args: Any, **kwargs: Any):
        # pylint: disable=unused-argument
        return object.__new__(cls)


register_library_class('Argument', Argument)
