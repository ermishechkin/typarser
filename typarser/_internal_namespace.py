from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import Any, Dict, List, MutableMapping, Optional, Set, Type, Union
from weakref import WeakKeyDictionary

from .errors import NamespaceNotRegisteredError

if typing.TYPE_CHECKING:
    from .command import Commands
    from .namespace import Namespace
    from .option import Option
    COMPONENT = Union[Namespace, Option[Any, Any], Commands[Any, Any]]


@dataclass
class NamespaceInternals:
    components: Dict[COMPONENT, List[str]] = field(default_factory=lambda: {})
    options: Set[Option[Any, Any]] = field(default_factory=set)
    command_containers: Set[Commands[Any, Any]] = \
        field(default_factory=set)
    commands: Dict[str, Type[Namespace]] = field(default_factory=lambda: {})
    usage: Optional[str] = None
    registered: bool = False

    def add_option(self, name: str, option: Option[Any, Any]):
        self.options.add(option)
        self.components.setdefault(option, [])
        self.components[option].append(name)

    def add_commands(self, name: str, commands: Commands[Any, Any]):
        self.command_containers.add(commands)
        self.components.setdefault(commands, [])
        self.components[commands].append(name)
        self._update_command_list()

    def _update_command_list(self):
        self.commands = {}
        for container in self.command_containers:
            for name, namespace in container.entries.items():
                self.commands[name] = namespace


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
        result = _namespaces[namespace] = NamespaceInternals()
    return result


def register_option(option: Option[Any, Any], namespace: Type[Namespace],
                    name: str):
    internals = get_namespace(namespace, create=True)
    internals.add_option(name, option)


def register_commands(commands: Commands[Any, Any], namespace: Type[Namespace],
                      name: str):
    internals = get_namespace(namespace, create=True)
    internals.add_commands(name, commands)


_namespaces: MutableMapping[Type[Namespace], NamespaceInternals] = \
    WeakKeyDictionary()
