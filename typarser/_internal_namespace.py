from __future__ import annotations

import typing
from dataclasses import dataclass, field
from keyword import iskeyword
from typing import (Any, Dict, List, Literal, MutableMapping, Optional, Set,
                    Tuple, Type, TypeVar, Union, cast, overload)
from weakref import WeakKeyDictionary

from ._removed_component import RemovedComponent
from .errors import (ComponentAlreayExistsError, ComponentNotExistError,
                     ComponentOverrideForbiddenError,
                     InvalidComponentNameError, InvalidComponentTypeError,
                     NamespaceNotRegisteredError)

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from ._base import BaseComponent
    from .argument import Argument
    from .command import Commands
    from .namespace import Namespace
    from .option import Option
    COMPONENT = BaseComponent[Any, Any]
    VALUES = Dict[Union[COMPONENT, Type['_CommandsKey']], Any]
    TYPE = TypeVar('TYPE', bound=BaseComponent[Any, Any])
    # pylint: enable=cyclic-import


@dataclass
class NamespaceInternals:  # pylint: disable=too-many-instance-attributes
    namespace_class: Type[Namespace]
    own_components: Dict[str, COMPONENT] = field(default_factory=lambda: {})
    removed_names: Set[str] = field(default_factory=set)
    prog: Optional[str] = None
    usage: Optional[str] = None
    description: Optional[str] = None
    epilog: Optional[str] = None
    allow_abbrev: bool = False
    registered: bool = False

    @property
    def parents(self) -> Tuple[NamespaceInternals, ...]:
        return _list_parents(self.namespace_class)

    @property
    def inherited_components(self) -> Dict[str, COMPONENT]:
        result: Dict[str, COMPONENT] = {}
        for parent in self.parents:
            result.update(parent.components)

        for name in self.removed_names:
            result.pop(name, None)

        for name, component in result.copy().items():
            if getattr(self.namespace_class, name, None) is not component:
                del result[name]

        return result

    @property
    def components(self) -> Dict[str, COMPONENT]:
        result = self.inherited_components
        result.update(self.own_components)
        return result

    @property
    def options(self) -> Dict[Option[Any, Any], List[str]]:
        return self._filter_components(_Option)

    @property
    def arguments(self) -> Dict[Argument[Any, Any], str]:
        return {
            component: next(iter(names))  # MUST contain exactly one name
            for component, names in self._filter_components(_Argument).items()
        }

    @property
    def command_containers(self) -> Dict[Commands[Any, Any], List[str]]:
        return self._filter_components(_Commands)

    @property
    def commands(self) -> Dict[str, Type[Namespace]]:
        result: Dict[str, Type[Namespace]] = {}
        for container in self.command_containers:
            result.update(container.entries)
        return result

    def add_component(self, name: str, component: BaseComponent[Any, Any], *,
                      allow_overwrite: bool, allow_override: bool):
        if not isinstance(component,
                          (_Argument, _Commands, _Option)):  # type: ignore
            raise InvalidComponentTypeError()
        if not allow_override and name in self.inherited_components:
            raise ComponentOverrideForbiddenError(name)
        if name in self.own_components:
            if not allow_overwrite:
                raise ComponentAlreayExistsError(name)
        if not is_valid_component_name(name):
            raise InvalidComponentNameError(name)
        setattr(self.namespace_class, name, component)
        self.own_components[name] = component

    def remove_component(self, name: str):
        if name in self.own_components:
            del self.own_components[name]
            delattr(self.namespace_class, name)
        elif name in self.inherited_components:
            setattr(self.namespace_class, name, RemovedComponent())
            self.removed_names.add(name)
        else:
            raise ComponentNotExistError(name)

    def create_values(self) -> VALUES:
        result: VALUES = {}
        result.update({
            option: (option.default if option.default is not None else
                     [] if option.multiple else None)
            for option in self.options
        })
        result.update({
            argument: None if argument.default is None else argument.default
            for argument in self.arguments
        })
        if self.command_containers:
            result[_CommandsKey] = None
        return result

    def _filter_components(self, base: Type[TYPE]) -> Dict[TYPE, List[str]]:
        result = {
            cast('TYPE', comp): names
            for comp, names in _aggregate_components(self.components).items()
            if isinstance(comp, base)  # type: ignore
        }
        return result


def init_namespace(namespace: Type[Namespace], *, prog: Optional[str],
                   usage: Optional[str], description: Optional[str],
                   epilog: Optional[str], allow_abbrev: bool):
    internals = get_namespace(namespace, create=True)
    internals.prog = prog
    internals.usage = usage
    internals.description = description
    internals.epilog = epilog
    internals.allow_abbrev = allow_abbrev
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


def register_component(namespace: Type[Namespace],
                       name: str,
                       component: BaseComponent[Any, Any],
                       *,
                       allow_override: bool = True,
                       allow_overwrite: bool = True):
    internals = get_namespace(namespace, create=True)
    internals.add_component(name,
                            component,
                            allow_override=allow_override,
                            allow_overwrite=allow_overwrite)


def unregister_component(namespace: Type[Namespace], name: str):
    internals = get_namespace(namespace, create=True)
    internals.remove_component(name)


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


def _aggregate_components(
        components: Dict[str, COMPONENT]) -> Dict[COMPONENT, List[str]]:
    result: Dict[COMPONENT, List[str]] = {}
    for name, component in components.items():
        all_names = result.setdefault(component, [])
        if name not in all_names:
            all_names.append(name)
    return result


def is_valid_component_name(name: str) -> bool:
    return name.isidentifier() and not iskeyword(name)


class _CommandsKey:
    pass


_namespaces: MutableMapping[Type[Namespace], NamespaceInternals] = \
    WeakKeyDictionary()

_values: MutableMapping[Namespace, VALUES] = WeakKeyDictionary()
