from typing import Any

import pytest
from typarser import Namespace, Option, Parser


def test_defaults():
    class Args(Namespace):
        arg = Option(type=int)

    assert Args.arg.required is False
    assert Args.arg.nargs is None
    assert Args.arg.multiple is False
    assert Args.arg.choices is None
    assert Args.arg.default is None
    assert Args.arg.metavar is None
    assert Args.arg.help is None


def test_immutability():
    class Args(Namespace):
        arg = Option(type=int)

    with pytest.raises(AttributeError):
        Args.arg.required = True
    with pytest.raises(AttributeError):
        Args.arg.nargs = 2
    with pytest.raises(AttributeError):
        Args.arg.multiple = True
    with pytest.raises(AttributeError):
        Args.arg.choices = [1, 5]
    with pytest.raises(AttributeError):
        Args.arg.default = 7
    with pytest.raises(AttributeError):
        Args.arg.metavar = 'VALUE'
    with pytest.raises(AttributeError):
        Args.arg.help = 'Help message'


def test_required_good():
    class Args(Namespace):
        optional = Option(type=int)
        mandatory = Option(type=int, required=True)

    assert Args.optional.required is False
    assert Args.mandatory.required is True

    args = Parser(Args).parse(['--mandatory', '123'])
    assert args.optional is None
    assert isinstance(args.mandatory, int)
    assert args.mandatory == 123


def test_required_missed():
    class Args(Namespace):
        mandatory = Option(type=int, required=True)

    with pytest.raises(SystemExit):
        Parser(Args).parse([])


def test_nargs_good():
    class Args(Namespace):
        single = Option(type=int)
        one = Option(type=int, nargs=1)
        three = Option(type=int, nargs=3)
        any = Option(type=int, nargs='*')
        any2 = Option(type=int, nargs='*')
        opt = Option(type=int, nargs='?')
        opt2 = Option(type=int, nargs='?')
        some = Option(type=int, nargs='+')

    args = Parser(Args).parse([
        '--single', '1',
        '--one', '2',
        '--three', '3', '4', '5',
        '--any',
        '--any2', '6', '7',
        '--opt',
        '--opt2', '8',
        '--some', '9', '10',
    ])  # yapf: disable

    assert args.single == 1
    assert args.one == [2]
    assert args.three == [3, 4, 5]
    assert args.any == []
    assert args.any2 == [6, 7]
    assert args.opt is None
    assert args.opt2 == 8
    assert args.some == [9, 10]


def test_multiple():
    class Args(Namespace):
        single = Option(type=int)
        multiple = Option(type=int, multiple=True)
        combo = Option(type=int, multiple=True, nargs=3)
        combo_single = Option(type=int, multiple=True, nargs=1)

    assert Args.single.multiple is False
    assert Args.multiple.multiple is True
    assert Args.combo.multiple is True

    args = Parser(Args).parse([
        '--single', '1',
        '--multiple', '2', '--multiple', '3',
        '--combo', '4', '5', '6', '--combo', '7', '8', '9',
        '--combo_single', '10', '--combo_single', '11',
    ])  # yapf: disable

    assert args.single == 1
    assert args.multiple == [2, 3]
    assert args.combo == [[4, 5, 6], [7, 8, 9]]
    assert args.combo_single == [[10], [11]]


def test_choices():
    class Args(Namespace):
        arg = Option(type=int, choices=[2, 3, 5])

    args = Parser(Args).parse(['--arg', '5'])
    assert args.arg == 5

    with pytest.raises(SystemExit):
        Parser(Args).parse(['--arg', '4'])


def test_default() -> Any:
    class Args(Namespace):
        arg = Option(type=int, default=5)
        arg2 = Option(type=int, nargs=2, default=[6, 7])

    args = Parser(Args).parse([])
    assert args.arg == 5
    assert args.arg2 == [6, 7]

    args = Parser(Args).parse(['--arg', '99'])
    assert args.arg == 99
