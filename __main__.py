# stdlib imports
import argparse
import bz2
import datetime
import io
import sys

# local module imports
import machine_gui
import enigma.machine
import rotors


def run_cli(args):
    """Run the Enigma Machine with the command-line interface"""

    # Initialize the enigma machine using specified rotors or a state file
    machine = None
    if args.state_file and not args.state_create:
        state = open(args.state_file, 'rb').read()
        machine = enigma.machine.Machine(state=state)
    else:
        if not args.rotors or not args.reflector:
            raise ValueError('Rotors and reflectors were not provided')
        machine = enigma.machine.Machine(None, args.rotors, args.reflector)

    # If a state file needs to be created, save it and exit
    if args.state_create:
        return open(args.state_file, 'wb').write(machine.stateGet())

    # If the state shall be printed, make it so, and exit
    if args.state_print:
        print('PLUGBOARD:', machine.plugboard, '(NOT IMPLEMENTED)')
        for i, rotor in enumerate(machine.rotors):
            print(
                'ROTOR:', i, rotor._name,
                'SETTING:', rotor._abet[rotor.setting],
                'NOTCHES:', rotor.notches
            )
        print('REFLECTOR:', machine.reflector._name)
        print('RAW:', machine.stateGet())

    # Work out the input
    input_file = None

    # input from the command-line
    if args.input:
        input_file = io.BytesIO(args.input.encode())

    # input from stdin
    elif args.input_std:
        input_file = sys.stdin.buffer

    # input from a file
    elif args.input_path:
        input_file = open(args.input_path, 'rb')

    # Check for decompression flag
    if args.input_bz2:
        input_file = bz2.decompress(input_file)

    # Now let's work out the output
    output_file = None

    # output to stdout
    if args.output_std:
        output_file = sys.stdout.buffer

    # output to a file
    elif args.output_path:
        output_file = open(args.output_path, 'wb')

    # check for compression flag
    output_file_final = None
    if args.output_bz2:
        output_file_final = output_file
        output_file = io.BytesIO()

    # get the size of the input
    input_file.seek(0, 2)
    input_size = input_file.tell()
    input_file.seek(0)

    time_start = datetime.datetime.utcnow()

    # Now it's time to do the dirty work...
    byte_count = 0
    while True:
        # read a chunk and process it
        chunk = input_file.read(args.chunk_size)
        if chunk:
            byte_count += len(chunk)

            chunk = chunk.decode()
            chunk = machine.transcodeString(chunk, skip_invalid=True)
            chunk = chunk.encode()

            output_file.write(chunk)

            progress = int(byte_count / input_size * 100.0)
            sys.stderr.write('PROGRESS: ' + str(progress) + '%\r')

        # if no chunk was found, that means we're all done
        else:
            print()
            break

    # Final compression bit
    if args.output_bz2:
        output_file.seek(0)
        mid = bz2.compress(output_file.read())
        output_file_final.write(mid)

    time_stop = datetime.datetime.utcnow()
    time_delta = (time_stop - time_start).total_seconds()
    if args.benchmark:
        print(input_size, 'BYTES in', time_delta, 'SECONDS')
        print(input_size / time_delta, 'BYTES/s')
        print(input_size / time_delta / 1024.0, 'KILOBYTES/s')
        print(input_size / time_delta / 1024.0 / 1024.0, 'MEGABYTES/s')


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

# Rotor args
parser_cli.add_argument(
    '--rotors', '-ro',
    nargs='+',
    type=str,
    required=False,
    help="""
    Specify a list of rotors in the following format:
    SHORTNAME[:SETTING[:NOTCHES]]
    ex; com1:C:QV
    """
)
parser_cli.add_argument(
    '--reflector', '-rf',
    type=str,
    required=False
)

# State args
parser_cli.add_argument(
    '--state-file',
    type=str,
    default='',
    required=False,
    help="""
    Path for the state file (loading or creating).
    Can be used in lieu of manually specifying rotors and reflectors.
    """
)
parser_cli.add_argument(
    '--state-create',
    action='store_true',
    required=False,
    help='Take the rotor and reflector args and save it to the state file.'
)
parser_cli.add_argument(
    '--state-print',
    action='store_true',
    required=False,
    help="""
    Print the state information to stdout and exit.
    """
)

# Input args
parser_cli.add_argument(
    '--input',
    type=str,
    default='',
    required=False,
    help="""
    Input a string via this command line argument.
    """
)
parser_cli.add_argument(
    '--input-std',
    action='store_true',
    required=False,
    help="""
    Read data from stdin pipe.
    """
)
parser_cli.add_argument(
    '--input-path',
    type=str,
    default='',
    required=False,
    help="""
    Open and read data from file path.
    """
)
parser_cli.add_argument(
    '--input-bz2',
    action='store_true',
    required=False,
    help="""
    Run input through BZ2 decompression before processing.
    """
)

# Output args
parser_cli.add_argument(
    '--output-std',
    action='store_true',
    required=False,
    help="""
    Write output to the stdout pipe.
    """
)
parser_cli.add_argument(
    '--output-path',
    type=str,
    required=False,
    help="""
    Write output to the specified file path.
    """
)
parser_cli.add_argument(
    '--output-bz2',
    action='store_true',
    required=False,
    help="""
    Run output through BZ2 compression before writing.
    """
)

# Other arguments
parser_cli.add_argument(
    '--chunk-size', '-c',
    type=int,
    default=128,
    required=False,
    help="""
    Chunk size for reading and writing data.
    """
)
parser_cli.add_argument(
    '--benchmark',
    action='store_true',
    required=False
)

parser_cli.set_defaults(func=run_cli)

# Sub-parser for the graphical user interface
parser_gui = subparsers.add_parser('gui')
parser_gui.set_defaults(func=run_gui)


args = parser.parse_args()
args.func(args)
