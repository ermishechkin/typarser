from __future__ import annotations

import typing
from typing import (Any, Callable, List, Literal, Optional, Type, Union,
                    overload)

from ._base import RESULT, TYPE, BaseComponent
from ._internal_namespace import (register_library_class, register_option,
                                  set_value)
from .namespace import Namespace

if typing.TYPE_CHECKING:
    from ._base import NAMESPACE
    NARGS = Union[int, Literal['*'], Literal['+'], Literal['?']]


class Option(BaseComponent[TYPE, RESULT]):
    # pylint: disable=redefined-builtin

    @overload
    def __init__(
        self: Option[TYPE, Optional[TYPE]],
        *,
        type: Callable[[str], TYPE],
        required: Literal[False] = False,
        nargs: Literal[None] = None,
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, TYPE],
        *,
        type: Callable[[str], TYPE],
        required: Literal[True],
        nargs: Literal[None] = None,
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, Optional[TYPE]],
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal['?'],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, Optional[List[TYPE]]],
        *,
        type: Callable[[str], TYPE],
        required: Literal[False] = False,
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, List[TYPE]],
        *,
        type: Callable[[str], TYPE],
        required: Literal[True],
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, List[TYPE]],
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal[None] = None,
        multiple: Literal[True],
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, List[Optional[TYPE]]],
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal['?'],
        multiple: Literal[True],
        help: Optional[str] = None,
    ):
        ...

    @overload
    def __init__(
        self: Option[TYPE, List[List[TYPE]]],
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[True],
        help: Optional[str] = None,
    ):
        ...

    # pylint: enable=redefined-builtin

    def __init__(
            self,
            *,
            type: Callable[[str], TYPE],  # pylint: disable=redefined-builtin
            required: bool = False,
            nargs: Optional[NARGS] = None,
            multiple: bool = False,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        super().__init__(help=help)
        self._type = type
        self._required = required
        self._nargs: Optional[NARGS] = nargs
        self._multiple = multiple

    def __set__(self, owner: NAMESPACE, value: TYPE):
        set_value(owner, self, value)

    @property
    def type(self) -> Callable[[str], TYPE]:
        return self._type

    @property
    def required(self) -> bool:
        return self._required

    @property
    def nargs(self) -> Optional[NARGS]:
        return self._nargs

    @property
    def multiple(self) -> bool:
        return self._multiple

    def __set_name__(self, owner: Type[Namespace], name: str):
        register_option(self, owner, name)

    # HACK: __init__ overloading doesn't work correctly for some linters.
    # Duplicate signatures for __new__ method.

    # pylint: disable=redefined-builtin

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: Literal[False] = False,
        nargs: Literal[None] = None,
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Option[TYPE, Optional[TYPE]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: Literal[True],
        nargs: Literal[None] = None,
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Option[TYPE, TYPE]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal['?'],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Option[TYPE, Optional[TYPE]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: Literal[False] = False,
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Option[TYPE, Optional[List[TYPE]]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: Literal[True],
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[False] = False,
        help: Optional[str] = None,
    ) -> Option[TYPE, List[TYPE]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal[None] = None,
        multiple: Literal[True],
        help: Optional[str] = None,
    ) -> Option[TYPE, List[TYPE]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Literal['?'],
        multiple: Literal[True],
        help: Optional[str] = None,
    ) -> Option[TYPE, List[Optional[TYPE]]]:
        ...

    @overload
    def __new__(
        cls,
        *,
        type: Callable[[str], TYPE],
        required: bool = False,
        nargs: Union[int, Literal['*', '+']],
        multiple: Literal[True],
        help: Optional[str] = None,
    ) -> Option[TYPE, List[List[TYPE]]]:
        ...

    # pylint: enable=redefined-builtin

    def __new__(cls, *args: Any, **kwargs: Any):
        # pylint: disable=unused-argument
        return object.__new__(cls)


register_library_class('Option', Option)
