from typarser import Argument, Commands, Namespace, Option, Parser


def test_dynamic_addition():
    class AddCmd(Namespace):
        name = Argument(type=str)
        surname = Argument(type=str)
        age = Argument(type=int)

    class SearchCmd(Namespace):
        name = Option(type=str)
        surname = Option(type=str)
        age = Option(type=int)

    class DeleteCmd(Namespace):
        id = Argument(type=int)

    class Args(Namespace):
        db = Option(type=str, default='data.bin')
        cmd = Commands(
            {
                'add': AddCmd,
                'search': SearchCmd,
                'delete': DeleteCmd,
            },
            required=True)

    parser = Parser(Args)

    args = parser.parse(['--db', 'new.bin', 'search', '--name', 'Martin'])
    assert args.db == 'new.bin'
    assert type(args.cmd) is SearchCmd
    assert args.cmd.name == 'Martin'
    assert args.cmd.surname is None
    assert args.cmd.age is None

    args = parser.parse(['add', 'John', 'Smith', '23'])
    assert args.db == 'data.bin'
    assert type(args.cmd) is AddCmd
    assert args.cmd.name == 'John'
    assert args.cmd.surname == 'Smith'
    assert args.cmd.age == 23


def test_multilevel_commands():
    class Cmd1_1(Namespace):
        arg1 = Argument(type=str)

    class Cmd2_1(Namespace):
        pass

    class Cmd2_2(Namespace):
        arg1 = Argument(type=int)
        arg2 = Argument(type=int)

    class Cmd1(Namespace):
        cmd = Commands({'sub': Cmd1_1})

    class Cmd2(Namespace):
        cmd = Commands({'sub1': Cmd2_1, 'sub2': Cmd2_2})

    class Args(Namespace):
        cmd = Commands({'cmd1': Cmd1, 'cmd2': Cmd2})

    parser = Parser(Args)

    args = parser.parse(['cmd2', 'sub2', '1', '2'])
    assert type(args.cmd) is Cmd2
    assert type(args.cmd.cmd) is Cmd2_2
    assert args.cmd.cmd.arg1 == 1
    assert args.cmd.cmd.arg2 == 2
