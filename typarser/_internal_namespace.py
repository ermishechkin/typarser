from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import (Any, Dict, Literal, MutableMapping, Optional, Set, Tuple,
                    Type, TypeVar, Union, cast, overload)
from weakref import WeakKeyDictionary

from .errors import NamespaceNotRegisteredError

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from ._base import BaseComponent
    from .argument import Argument
    from .command import Commands
    from .namespace import Namespace
    from .option import Option
    COMPONENT = BaseComponent[Any, Any]
    VALUES = Dict[Union[COMPONENT, Type['_CommandsKey']], Any]
    TYPE = TypeVar('TYPE', bound=BaseComponent)
    # pylint: enable=cyclic-import


@dataclass
class NamespaceInternals:
    namespace_class: Type[Namespace]
    own_components: Dict[COMPONENT, Set[str]] = \
        field(default_factory=lambda: {})
    usage: Optional[str] = None
    registered: bool = False

    @property
    def parents(self) -> Tuple[NamespaceInternals, ...]:
        return _list_parents(self.namespace_class)

    @property
    def components(self) -> Dict[COMPONENT, Set[str]]:
        result: Dict[COMPONENT, Set[str]] = {}
        for parent in self.parents:
            for component, names in parent.components.items():
                all_names = result.setdefault(component, set())
                all_names.update(names)

        for component, names in result.items():
            for name in names.copy():
                if getattr(self.namespace_class, name, None) is not component:
                    names.remove(name)

        for component, names in list(result.items()):
            if not names:
                del result[component]

        for component, names in self.own_components.items():
            all_names = result.setdefault(component, set())
            all_names.update(names)

        return result

    @property
    def options(self) -> Set[Option[Any, Any]]:
        return self._filter_components(_Option)

    @property
    def arguments(self) -> Set[Argument[Any, Any]]:
        return self._filter_components(_Argument)

    @property
    def command_containers(self) -> Set[Commands[Any, Any]]:
        return self._filter_components(_Commands)

    @property
    def commands(self) -> Dict[str, Type[Namespace]]:
        result: Dict[str, Type[Namespace]] = {}
        for container in self.command_containers:
            result.update(container.entries)
        return result

    def add_component(self, name: str, component: BaseComponent[Any, Any]):
        names = self.own_components.setdefault(component, set())
        names.add(name)

    def create_values(self) -> VALUES:
        result: VALUES = {}
        result.update({option: None for option in self.options})
        result.update({argument: None for argument in self.arguments})
        if self.command_containers:
            result[_CommandsKey] = None
        return result

    def _filter_components(self, base: Type[TYPE]) -> Set[TYPE]:
        result: Set[TYPE] = set(
            cast(TYPE, comp) for comp in self.components
            if isinstance(comp, base))
        return result


def init_namespace(namespace: Type[Namespace], *, usage: Optional[str]):
    internals = get_namespace(namespace, create=True)
    internals.usage = usage
    internals.registered = True


def get_namespace(namespace: Type[Namespace],
                  create: bool = False) -> NamespaceInternals:
    try:
        result = _namespaces[namespace]
    except KeyError:
        if not create:
            raise NamespaceNotRegisteredError(namespace) from None
        result = _namespaces[namespace] = NamespaceInternals(namespace)
    return result


def register_component(namespace: Type[Namespace], name: str,
                       component: BaseComponent[Any, Any]):
    internals = get_namespace(namespace, create=True)
    internals.add_component(name, component)


def get_value(namespace: Namespace, component: COMPONENT) -> Any:
    internals = get_namespace(type(namespace))
    values = _values.get(namespace)
    if values is None:
        values = _values[namespace] = internals.create_values()
    if component in internals.command_containers:
        return values[_CommandsKey]
    return values[component]


def set_value(namespace: Namespace, component: COMPONENT, value: Any):
    internals = get_namespace(type(namespace))
    values = _values.get(namespace)
    if values is None:
        values = _values[namespace] = internals.create_values()
    if component in internals.command_containers:
        values[_CommandsKey] = value
    values[component] = value


_Option: Type[Option[Any, Any]]
_Argument: Type[Argument[Any, Any]]
_Commands: Type[Commands[Any, Any]]


@overload
def register_library_class(class_name: Literal['Option'],
                           cls: Type[Option[Any, Any]]):
    ...


@overload
def register_library_class(class_name: Literal['Argument'],
                           cls: Type[Argument[Any, Any]]):
    ...


@overload
def register_library_class(class_name: Literal['Commands'],
                           cls: Type[Commands[Any, Any]]):
    ...


def register_library_class(class_name: str, cls: Type[Any]):
    # pylint: disable=global-statement,invalid-name
    if class_name == 'Commands':
        global _Commands
        _Commands = cls
    elif class_name == 'Option':
        global _Option
        _Option = cls
    elif class_name == 'Argument':
        global _Argument
        _Argument = cls


def _list_parents(
        namespace: Type[Namespace]) -> Tuple[NamespaceInternals, ...]:
    bases: Tuple[Type[Any], ...] = namespace.__bases__
    return tuple(_namespaces[base] for base in bases if base in _namespaces)


class _CommandsKey:
    pass


_namespaces: MutableMapping[Type[Namespace], NamespaceInternals] = \
    WeakKeyDictionary()

_values: MutableMapping[Namespace, VALUES] = WeakKeyDictionary()
