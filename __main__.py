# stdlib imports
import argparse
import bz2
import datetime
import io
import re
import sys

# local module imports
import machine_gui
import enigma.machine
import rotors


def _serialize_plugboard(stack):
    """Serialize a plugboard stack back into character pairings"""
    pairs = []
    for i in range(26):
        if stack[i] is None:
            continue
        if stack[i] != i:
            x = i
            y = stack[i]
            pairs.append(
                rotors._RotorBase._abet[x] + rotors._RotorBase._abet[y]
            )
            stack[y] = None
    return pairs


def run_cli(args):
    """Run the Enigma Machine with the command-line interface"""
    # Initialize the enigma machine using specified rotors or a state file
    machine = None
    if args.state_path and not args.state_create:
        state = bz2.open(args.state_path, 'rb').read()
        machine = enigma.machine.Machine(state=state)
    else:
        if not args.rotors or not args.reflector:
            raise ValueError('Rotors and reflectors were not provided')
        machine = enigma.machine.Machine(
            args.plugboard,
            args.rotors,
            args.reflector,
            verbose=args.verbose
        )

    # If a state file needs to be created, save it and exit
    if args.state_create:
        return bz2.open(args.state_path, 'wb').write(machine.stateGet())

    # If the state shall be printed, make it so, and exit
    if args.state_print:
        print('PLUGBOARD:', ' '.join(_serialize_plugboard(machine.plugboard)))
        for i, rotor in enumerate(machine.rotors):
            print(
                'ROTOR:', i + 1, rotor._name,
                'SETTING:', rotor._abet[rotor.setting],
                'NOTCHES:', rotor.notches
            )
        print('REFLECTOR:', machine.reflector._name)
        # print('RAW:', machine.stateGet())
        return

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
        input_file = io.BytesIO(bz2.decompress(input_file.read()))

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

    # Progress callback
    def callback(current, total):
        rs = ''.join([r._abet[r.setting] for r in machine.rotors])
        sys.stderr.write(
            'ROTORS: ' + rs + '    ' +
            'PROGRESS: ' + str(int(current / total * 100.0)) + '%\r'
        )

    # Flip it off if needed
    if args.no_progress:
        callback = None

    machine.translateStream(
        stream_in=input_file,
        stream_out=output_file,
        chunkSize=args.chunk_size,
        progressCallback=callback,
        sanitize=args.sanitize
    )

    # Final compression bit
    if args.output_bz2:
        output_file.seek(0)
        mid = bz2.compress(output_file.read())
        output_file_final.write(mid)

    # Collect time for benchmarking
    if args.benchmark:
        time_stop = datetime.datetime.utcnow()
        time_delta = (time_stop - time_start).total_seconds()
        bps = input_size / time_delta
        kbps = input_size / time_delta / 1024.0
        mbps = input_size / time_delta / 1024.0 / 1024.0
        sys.stderr.write("""
{0} BYTES in {1:.2f} SECONDS
{2:>10.2f} BYTES/s
{3:>10.2f} KILOBYTES/s
{4:>10.2f} MEGABYTES/s
        """.format(input_size, time_delta, bps, kbps, mbps).strip())

    # Write back to the state file if asked to
    if args.state_update:
        if args.state_path:
            open(args.state_path, 'wb').write(machine.stateGet())


def run_gui(args):
    """Run the Enigma Machine using the Graphical User Interface"""
    print('GUI is currently non-functional. Exiting...')
    exit()
    machine_gui.main()


def main():
    """Main method (seems kinda redundant in the main file bu w/e)"""
    # Define the master parser
    parser = argparse.ArgumentParser(
        description='Process some data through a simulated Enigma machine'
    )
    subparsers = parser.add_subparsers()

    # Sub-parser for the command-line interface
    parser_cli = subparsers.add_parser('cli')

    # Rotor args
    parser_cli.add_argument(
        '--plugboard', '-p',
        nargs='+',
        default=[],
        type=str,
        required=False,
        help="""
        Specify a list of character pairings for the plugboard.
        ex; AB CF HJ
        """
    )
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
        '--state-path', '-s',
        type=str,
        default='',
        required=False,
        help="""
        Path for the state file (loading or creating).
        Can be used in lieu of manually specifying rotors and reflectors.
        """
    )
    parser_cli.add_argument(
        '--state-create', '-sc',
        action='store_true',
        required=False,
        help='Take the rotor and reflector args and save it to the state file.'
    )
    parser_cli.add_argument(
        '--state-update', '-su',
        action='store_true',
        required=False,
        help="""
        After processing, save the changed rotor state back to the state file.
        This allows for a continuous rotor progression over multiple
        script invocations. THERE IS NO ROLLBACK, SO BACK IT UP.
        """
    )
    parser_cli.add_argument(
        '--state-print', '-sp',
        action='store_true',
        required=False,
        help="""
        Print the state information to stdout and exit.
        """
    )

    # Input args
    parser_cli.add_argument(
        '--input', '-i',
        type=str,
        default='',
        required=False,
        help="""
        Input a string via this command line argument.
        """
    )
    parser_cli.add_argument(
        '--input-std', '-is',
        action='store_true',
        required=False,
        help="""
        Read data from stdin pipe.
        """
    )
    parser_cli.add_argument(
        '--input-path', '-ip',
        type=str,
        default='',
        required=False,
        help="""
        Open and read data from file path.
        """
    )
    parser_cli.add_argument(
        '--input-bz2', '-iz',
        action='store_true',
        required=False,
        help="""
        Run input through BZ2 decompression before processing.
        """
    )

    # Output args
    parser_cli.add_argument(
        '--output-std', '-os',
        action='store_true',
        required=False,
        help="""
        Write output to the stdout pipe.
        """
    )
    parser_cli.add_argument(
        '--output-path', '-op',
        type=str,
        required=False,
        help="""
        Write output to the specified file path.
        """
    )
    parser_cli.add_argument(
        '--output-bz2', '-oz',
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
        '--benchmark', '-b',
        action='store_true',
        required=False,
        help="""
        Benchmark the processing time (prints results to stderr).
        """
    )
    parser_cli.add_argument(
        '--no-progress', '-np',
        action='store_true',
        required=False,
        help="""
        Suppress the progress meter that is normal written to stderr.
        """
    )
    parser_cli.add_argument(
        '--sanitize', '-sa',
        action='store_true',
        required=False,
        help="""
        Sanitize input to resemble typical enigma text (alpha, caps, and no space).
        """
    )
    parser_cli.add_argument(
        '--verbose', '-v',
        action='store_true',
        required=False,
        help="""
        Enable verbosity; printing LOTS of messages to stderr.
        """
    )

    parser_cli.set_defaults(func=run_cli)

    # Sub-parser for the graphical user interface
    parser_gui = subparsers.add_parser('gui')
    parser_gui.set_defaults(func=run_gui)

    if len(sys.argv) == 1:
        print('("--help" flag inferred from no args)\n')
        sys.argv.append('--help')
    args = parser.parse_args()
    args.func(args)

# Run if main
if __name__ == '__main__':
    main()
