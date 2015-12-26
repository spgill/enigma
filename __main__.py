# stdlib imports
import argparse
import sys

# local module imports
import machine_gui
import machine as machine
import rotors


def run_cli(args):
    """Run the Enigma Machine with the command-line interface"""
    # print(args.input)
    em = machine.Machine(None, args.rotors, args.reflector)
    # print(em.transcodeString(args.input))
    data = None
    if args.stdin:
        data = sys.stdin.read()
    else:
        data = args.input
    sys.stdout.write(em.transcodeString(data, skip_invalid=True, trace=False))


def run_gui(args):
    """Run the Enigma Machine using the Graphical User Interface"""
    machine_gui.main()


# Define the master parser
parser = argparse.ArgumentParser(
    description='Process some data through a simulated Enigma machine'
)
subparsers = parser.add_subparsers()

# Sub-parser for the command-line interface
parser_cli = subparsers.add_parser('cli')
parser_cli.add_argument(
    '--rotors', '-ro',
    nargs='+',
    type=str,
    required=True
)
parser_cli.add_argument(
    '--reflector', '-rf',
    type=str,
    required=True
)
parser_cli.add_argument(
    '--stdin',
    action='store_true',
    required=False
)
parser_cli.add_argument(
    '--input',
    type=str,
    required=False
)
parser_cli.set_defaults(func=run_cli)

# Sub-parser for the graphical user interface
parser_gui = subparsers.add_parser('gui')
parser_gui.set_defaults(func=run_gui)


args = parser.parse_args()
args.func(args)
