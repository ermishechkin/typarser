from __future__ import annotations

import typing
from argparse import Action as ArgparseAction
from argparse import ArgumentParser
from argparse import Namespace as ArgparseNamespace
from dataclasses import dataclass
from itertools import count
from typing import (Any, Dict, Generic, Iterator, List, Optional, Sequence,
                    Text, Tuple, Type, TypeVar, Union)

from ._internal_namespace import get_namespace, get_value, set_value
from .errors import ParseError
from .namespace import Namespace

if typing.TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from ._internal_namespace import COMPONENT, NamespaceInternals
    from .action import Action
    from .command import Commands
    from .parser import Parser

    # pylint: enable=cyclic-import

ARGS = TypeVar('ARGS', bound=Namespace, covariant=True)


def create_native_parser(
        parser: Parser[ARGS],
        namespace_class: Type[ARGS]) -> Tuple[ArgumentParser, State[ARGS]]:

    internals = get_namespace(namespace_class)
    native_parser = ArgumentParserEx(**_format_parser_options(internals))
    root_namespace_info = ContainerInfo(None, namespace_class, None)
    state = State(
        parser=parser,
        root_namespace_info=root_namespace_info,
        parents_map={},
        current_namespace=None,
        ns_seq=[],
    )
    _fill_parser(namespace_class, native_parser, root_namespace_info,
                 count(start=1), state)
    return native_parser, state


def _fill_parser(namespace: Type[Namespace], parser: ArgumentParser,
                 container: ContainerInfo[Namespace], counter: Iterator[int],
                 state: State[Any]):
    internals = get_namespace(namespace)
    _fill_options(internals, parser, container, counter, state)
    _fill_arguments(internals, parser, container, counter, state)
    _fill_commands(internals, parser, container, counter, state)


def _fill_options(internals: NamespaceInternals, parser: ArgumentParser,
                  container: ContainerInfo[Namespace], counter: Iterator[int],
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
            action=(create_action_proxy(option.action, option, key, state)
                    if option.action is not None else create_store_action(
                        state, option, key) if not option.multiple else
                    create_append_action(state, option, key)),
            help=option.help,
            dest=key,
        )
        state.parents_map[key] = container


def _fill_arguments(internals: NamespaceInternals, parser: ArgumentParser,
                    container: ContainerInfo[Namespace],
                    counter: Iterator[int], state: State[Any]) -> None:
    for argument, name in internals.arguments.items():
        key = f'opt_{next(counter)}'
        calc_metavar = argument.metavar if argument.metavar else name
        parser.add_argument(
            type=argument.type,
            nargs=argument.nargs,  # type: ignore
            choices=argument.choices,  # type: ignore
            default=argument.default,
            metavar=calc_metavar,
            action=(create_action_proxy(argument.action, argument, key, state)
                    if argument.action is not None else create_store_action(
                        state, argument, key)),
            help=argument.help,
            dest=key,
        )
        state.parents_map[key] = container


def _fill_commands(internals: NamespaceInternals, parser: ArgumentParser,
                   container: ContainerInfo[Namespace], counter: Iterator[int],
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

        container.subcommands = SubcommandsInfo(
            next(iter(internals.command_containers)), key, {})

        state.parents_map[key] = container
        for name, subnamespace in internals.commands.items():
            subnamespace_internals = get_namespace(subnamespace)
            subparser = subparsers.add_parser(
                name, **_format_parser_options(subnamespace_internals))
            nested_container = ContainerInfo(container, subnamespace, None)
            container.subcommands.commands_map[name] = nested_container
            _fill_parser(subnamespace, subparser, nested_container, counter,
                         state)


def _format_parser_options(internals: NamespaceInternals) -> Dict[str, Any]:
    return {
        'prog': internals.prog,
        'usage': internals.usage,
        'description': internals.description,
        'epilog': internals.epilog,
        'add_help': False,
        'allow_abbrev': internals.allow_abbrev,
    }


def parse_args(native_parser: ArgumentParser, state: State[ARGS],
               args: List[str]) -> ARGS:
    root_namespace = state.reset()
    native_namespace = native_parser.parse_args(args)
    state.adjust_post_parse(native_namespace)
    return root_namespace


@dataclass
class ContainerInfo(Generic[ARGS]):
    parent: Optional[ContainerInfo[ARGS]]
    namespace_class: Type[ARGS]
    subcommands: Optional[SubcommandsInfo]


@dataclass(frozen=False)
class SubcommandsInfo:
    commands_component: Commands[Any, Any]
    native_key: str
    commands_map: Dict[str, ContainerInfo[Namespace]]


@dataclass
class State(Generic[ARGS]):
    parser: Parser[ARGS]
    root_namespace_info: ContainerInfo[ARGS]
    parents_map: Dict[str, ContainerInfo[Namespace]]
    current_namespace: Optional[Namespace]
    ns_seq: List[Tuple[ContainerInfo[Namespace], Namespace]]

    def adjust_namespace(self, comp_key: str):
        parents: List[ContainerInfo[Namespace]] = []
        parent_info: Optional[ContainerInfo[Namespace]]
        parent_info = self.parents_map[comp_key]
        while parent_info is not None:
            parents.insert(0, parent_info)
            parent_info = parent_info.parent

        # sanity check
        for (actual, _), expected in zip(self.ns_seq, parents):
            assert actual is expected

        prev_container, prev_namespace = self.ns_seq[-1]
        for parent_info in parents[len(self.ns_seq):]:
            created_namespace = parent_info.namespace_class()
            self.ns_seq.append((parent_info, created_namespace))
            assert prev_container.subcommands is not None
            set_value(prev_namespace,
                      prev_container.subcommands.commands_component,
                      created_namespace)
            prev_container, prev_namespace = parent_info, created_namespace

        self.current_namespace = self.ns_seq[len(parents) - 1][1]

    def adjust_post_parse(self, native_namespace: ArgparseNamespace):
        container, namespace = self.ns_seq[-1]
        while container.subcommands is not None:
            subcommands: SubcommandsInfo = container.subcommands
            cmd_name: Optional[str] = getattr(native_namespace,
                                              subcommands.native_key)
            if cmd_name is None:
                break
            next_container_info = subcommands.commands_map[cmd_name]
            next_namespace = next_container_info.namespace_class()
            set_value(namespace, subcommands.commands_component,
                      next_namespace)
            container = next_container_info
            namespace = next_namespace

        self.current_namespace = namespace

    def reset(self) -> ARGS:
        root_namespace = self.root_namespace_info.namespace_class()
        self.current_namespace = root_namespace
        self.ns_seq = [(self.root_namespace_info, root_namespace)]
        return root_namespace


def create_action_proxy(action: Action, component: COMPONENT, native_key: str,
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
            state.adjust_namespace(native_key)
            assert state.parser is not None
            action(state.parser, state.current_namespace, values,
                   option_string)

    return ProxyAction


def create_store_action(state: State[Any], component: COMPONENT,
                        native_key: str):
    class StoreAction(ArgparseAction):
        def __call__(
            self,
            native_parser: ArgumentParser,
            native_namespace: ArgparseNamespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            state.adjust_namespace(native_key)
            assert state.current_namespace is not None
            set_value(state.current_namespace, component, values)

    return StoreAction


def create_append_action(state: State[Any], component: COMPONENT,
                         native_key: str):
    class AppendAction(ArgparseAction):
        def __call__(
            self,
            native_parser: ArgumentParser,
            native_namespace: ArgparseNamespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            state.adjust_namespace(native_key)
            assert state.current_namespace is not None
            src_value = get_value(state.current_namespace, component)
            value: List[Any] = [] if src_value is None else src_value
            value.append(values)
            set_value(state.current_namespace, component, value)

    return AppendAction


class ArgumentParserEx(ArgumentParser):
    def error(self, message: Text):
        raise ParseError(message)
