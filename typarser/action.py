from __future__ import annotations

import typing
from typing import Any, List, Optional, TypeVar, Union

from ._internal_namespace import set_value

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from ._base import TYPE, BaseComponent
    from ._internal_namespace import COMPONENT
    from .namespace import Namespace
    from .parser import Parser
    ARGS = TypeVar('ARGS', bound=Namespace)

    # pylint: enable=cyclic-import


class Action:
    def bind(self, names: List[str], component: BaseComponent[Any, Any]):
        # pylint: disable=attribute-defined-outside-init
        self.names = names
        self.component = component

    @staticmethod
    def set_value(namespace: Namespace, component: COMPONENT, value: Any):
        set_value(namespace, component, value)

    def __call__(self,
                 parser: Parser[ARGS],
                 namespace: ARGS,
                 values: Union[None, TYPE, List[TYPE]],
                 option_string: Optional[str] = None) -> None:
        raise NotImplementedError


class ActionStore(Action):
    def __call__(self,
                 parser: Parser[ARGS],
                 namespace: ARGS,
                 values: Union[None, TYPE, List[TYPE]],
                 option_string: Optional[str] = None) -> None:
        self.set_value(namespace, self.component, values)


class ActionStoreConst(Action):
    def __init__(self, const: Any):
        self.const = const

    def __call__(self,
                 parser: Parser[ARGS],
                 namespace: ARGS,
                 values: Union[None, TYPE, List[TYPE]],
                 option_string: Optional[str] = None) -> None:
        self.set_value(namespace, self.component, self.const)


class ActionHelp(Action):
    def __call__(self,
                 parser: Parser[ARGS],
                 namespace: ARGS,
                 values: Union[None, TYPE, List[TYPE]],
                 option_string: Optional[str] = None) -> None:
        parser.print_help()
