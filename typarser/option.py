from __future__ import annotations

from typing import (Generic, List, Literal, Optional, Type, TypeVar, Union,
                    overload)

NAMESPACE = TypeVar('NAMESPACE')
TYPE = TypeVar('TYPE')
SELF = TypeVar('SELF', bound='Option')
RESULT = TypeVar('RESULT')
NARGS = Union[int, Literal['*'], Literal['+'], Literal['?']]


class Option(Generic[TYPE, RESULT]):
    # pylint: disable=redefined-builtin

    @overload
    def __init__(
        self: Option[TYPE, Optional[TYPE]],
        *,
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
        type: Type[TYPE],
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
            type: Type[TYPE],  # pylint: disable=redefined-builtin
            required: bool = False,
            nargs: Optional[NARGS] = None,
            multiple: bool = False,
            help: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        self._type = type
        self._required = required
        self._nargs: Optional[NARGS] = nargs
        self._multiple = multiple
        self._help = help

    @overload
    def __get__(self: SELF, owner: Literal[None], inst: Type[NAMESPACE]) \
            -> SELF:
        ...

    @overload
    def __get__(self, owner: NAMESPACE, inst: Type[NAMESPACE]) -> RESULT:
        ...

    def __get__(self: SELF, owner: Optional[NAMESPACE],
                inst: Type[NAMESPACE]) -> Union[SELF, RESULT]:
        raise NotImplementedError

    def __set__(self, owner: NAMESPACE, value: TYPE):
        raise AttributeError('Attributes are read-only')

    @property
    def type(self) -> Type[TYPE]:
        return self._type

    @property
    def help(self) -> Optional[str]:
        return self._help

    @property
    def required(self) -> bool:
        return self._required

    @property
    def nargs(self) -> Optional[NARGS]:
        return self._nargs

    @property
    def multiple(self) -> bool:
        return self._multiple
