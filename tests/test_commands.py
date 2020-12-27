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
