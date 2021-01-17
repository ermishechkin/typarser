from __future__ import annotations

import typing
from argparse import Action as ArgparseAction
from argparse import ArgumentParser
from argparse import Namespace as ArgparseNamespace
from dataclasses import dataclass
from itertools import count
from typing import (Any, Dict, Generic, Iterator, List, NamedTuple, Optional,
                    Sequence, Tuple, Type, TypeVar, Union)

from ._internal_namespace import get_namespace, get_value, set_value
from .namespace import Namespace

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from ._internal_namespace import COMPONENT, NamespaceInternals
    from .action import Action
    from .command import Commands
    from .parser import Parser
    MAP = Dict[  # type: ignore  # mypy doesn't suport cyclic types
        str, Union[COMPONENT, '_Subcommands']]  # type: ignore
    # pylint: enable=cyclic-import

ARGS = TypeVar('ARGS', bound=Namespace)


def create_native_parser(
        parser: Parser[ARGS],
        namespace_class: Type[ARGS]) -> Tuple[ArgumentParser, State[ARGS]]:
    class CustomNamespace(ArgparseNamespace):
        pass

    internals = get_namespace(namespace_class)
    native_parser = ArgumentParser(**_format_parser_options(internals))
    state = State(
        parser=parser,
        current_namespace=None,
        current_map=None,
        native_namespace=CustomNamespace(),
        subcommands_dict={},
        root_namespace_class=namespace_class,
        root_map={},
    )
    names_map = _fill_parser(namespace_class, native_parser, count(start=1),
                             state)
    state.root_map = names_map
    return native_parser, state


def _fill_parser(namespace: Type[Namespace], parser: ArgumentParser,
                 counter: Iterator[int], state: State[Any]) -> MAP:
    internals = get_namespace(namespace)
    names_map: MAP = {}
    _fill_options(internals, parser, names_map, counter, state)
    _fill_arguments(internals, parser, names_map, counter, state)
    _fill_commands(internals, parser, names_map, counter, state)
    return names_map


def _fill_options(internals: NamespaceInternals, parser: ArgumentParser,
                  names_map: MAP, counter: Iterator[int],
                  state: State[Any]) -> None:
    for option, names in internals.options.items():
        names_prefixed = [
            f'-{name}' if len(name) == 1 else f'--{name}' for name in names
        ]
        key = f'opt_{next(counter)}'
        calc_metavar = option.metavar if option.metavar else names[0].upper()
        parser.add_argument(
            *names_prefixed,
            type=option.type,
            required=option.required,
            nargs=option.nargs,  # type: ignore
            choices=option.choices,  # type: ignore
            default=option.default,
            metavar=calc_metavar,
            action=(create_action_proxy(option.action, option, state)
                    if option.action is not None else
                    create_store_action(state, option) if not option.multiple
                    else create_append_action(state, option)),
            help=option.help,
            dest=key,
        )
        names_map[key] = option


def _fill_arguments(internals: NamespaceInternals, parser: ArgumentParser,
                    names_map: MAP, counter: Iterator[int],
                    state: State[Any]) -> None:
    for argument, name in internals.arguments.items():
        key = f'opt_{next(counter)}'
        calc_metavar = argument.metavar if argument.metavar else name
        parser.add_argument(
            type=argument.type,
            nargs=argument.nargs,  # type: ignore
            choices=argument.choices,  # type: ignore
            default=argument.default,
            metavar=calc_metavar,
            action=(create_action_proxy(argument.action, argument, state)
                    if argument.action is not None else create_store_action(
                        state, argument)),
            help=argument.help,
            dest=key,
        )
        names_map[key] = argument


def _fill_commands(internals: NamespaceInternals, parser: ArgumentParser,
                   names_map: MAP, counter: Iterator[int],
                   state: State[Any]) -> None:
    if internals.command_containers:
        for command_container in internals.command_containers:
            if command_container.required:
                command_required = True
                break
        else:
            command_required = False

        metavar = None
        for command_container in internals.command_containers:
            if command_container.metavar is not None:
                metavar = command_container.metavar

        key = f'opt_{next(counter)}'
        subparsers = parser.add_subparsers(
            required=command_required,
            dest=key,
            metavar=metavar,
        )
        setattr(type(state.native_namespace), key, ProxyMember(key, state))
        names_submap: Dict[str, _Subcommand] = {}
        names_map[key] = _Subcommands(next(iter(internals.command_containers)),
                                      names_submap)
        for name, subnamespace in internals.commands.items():
            subnamespace_internals = get_namespace(subnamespace)
            subparser = subparsers.add_parser(
                name, **_format_parser_options(subnamespace_internals))
            names_submap[name] = _Subcommand(
                _fill_parser(subnamespace, subparser, counter, state),
                subnamespace)


def _format_parser_options(internals: NamespaceInternals) -> Dict[str, Any]:
    return {
        'prog': internals.prog,
        'usage': internals.usage,
        'description': internals.description,
        'epilog': internals.epilog,
        'add_help': False,
    }


def parse_args(native_parser: ArgumentParser, state: State[ARGS],
               args: List[str]) -> ARGS:
    root_namespace = state.reset()
    native_parser.parse_args(args, state.native_namespace)
    return root_namespace


class _Subcommand(NamedTuple):
    submap: MAP
    namespace: Type[Namespace]


class _Subcommands(NamedTuple):
    component: Commands[Any, Any]
    cmds: Dict[str, _Subcommand]


@dataclass
class State(Generic[ARGS]):
    parser: Parser[ARGS]
    current_namespace: Optional[Namespace]
    current_map: Optional[MAP]
    native_namespace: ArgparseNamespace
    subcommands_dict: Dict[str, str]
    root_namespace_class: Type[ARGS]
    root_map: MAP

    def reset(self) -> ARGS:
        root_namespace = self.root_namespace_class()
        self.current_namespace = root_namespace
        self.current_map = self.root_map
        self.native_namespace.__dict__.clear()
        self.subcommands_dict.clear()
        return root_namespace


def create_action_proxy(action: Action, component: COMPONENT,
                        state: State[Any]):
    class ProxyAction(ArgparseAction):
        def __init__(self, option_strings: List[str], *args: Any,
                     **kwargs: Any) -> None:
            super().__init__(option_strings, *args, **kwargs)
            action.bind(option_strings, component)

        def __call__(
            self,
            native_parser: ArgumentParser,
            native_namespace: ArgparseNamespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            assert state.parser is not None
            action(state.parser, state.current_namespace, values,
                   option_string)

    return ProxyAction


def create_store_action(state: State[Any], component: COMPONENT):
    class StoreAction(ArgparseAction):
        def __call__(
            self,
            native_parser: ArgumentParser,
            native_namespace: ArgparseNamespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            assert state.current_namespace is not None
            set_value(state.current_namespace, component, values)

    return StoreAction


def create_append_action(state: State[Any], component: COMPONENT):
    class AppendAction(ArgparseAction):
        def __call__(
            self,
            native_parser: ArgumentParser,
            native_namespace: ArgparseNamespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            assert state.current_namespace is not None
            src_value = get_value(state.current_namespace, component)
            value: List[Any] = [] if src_value is None else src_value
            value.append(values)
            set_value(state.current_namespace, component, value)

    return AppendAction


class ProxyMember:
    def __init__(self, key: str, state: State[Any]):
        self.key = key
        self.state = state

    def __get__(self, owner: Any, inst: Any):
        return self.state.subcommands_dict.get(self.key)

    def __set__(self, owner: Any, value: Any):
        assert self.state.current_map is not None
        assert self.state.current_namespace is not None
        info = self.state.current_map[self.key]
        assert isinstance(info, _Subcommands)
        cmd_name: str = value
        cmd = info.cmds[cmd_name]
        new_namespace = cmd.namespace()
        set_value(self.state.current_namespace, info.component, new_namespace)
        self.state.current_namespace = new_namespace
        self.state.current_map = cmd.submap
        self.state.subcommands_dict[self.key] = cmd_name
