# stdlib imports
import argparse
import bz2
import datetime
import io
import sys

# local module imports
import machine as emachine
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

def main():
    """Main method (seems kinda redundant in the main file but w/e)"""
    # Define the master parser
    parser = argparse.ArgumentParser(
        description='Process some data through a simulated Enigma machine'
    )

    # Rotor args
    parser.add_argument(
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
    parser.add_argument(
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
    parser.add_argument(
        '--reflector', '-rf',
        type=str,
        required=False
    )

    # State args
    parser.add_argument(
        '--state', '-s',
        type=str,
        default='',
        required=False,
        help="""
        Path for the state file (loading or creating).
        Can be used in lieu of manually specifying rotors and reflectors.
        """
    )
    parser.add_argument(
        '--state-create', '-sc',
        action='store_true',
        required=False,
        help='Take the rotor and reflector args and save it to the state file.'
    )
    parser.add_argument(
        '--state-update', '-su',
        action='store_true',
        required=False,
        help="""
        After processing, save the changed rotor state back to the state file.
        This allows for a continuous rotor progression over multiple
        script invocations. THERE IS NO ROLLBACK, SO BACK IT UP.
        """
    )
    parser.add_argument(
        '--state-print', '-sp',
        action='store_true',
        required=False,
        help="""
        Print the state information to stdout and exit.
        """
    )
    parser.add_argument(
        '--state-seed', '-ss',
        type=str,
        default='',
        required=False,
        help="""
        String seed for a randomly generated state.
        """
    )

    # Input args
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='',
        required=False,
        help="""
        Input a string via this command line argument.
        """
    )
    parser.add_argument(
        '--input-std', '-is',
        action='store_true',
        required=False,
        help="""
        Read data from stdin pipe.
        """
    )
    parser.add_argument(
        '--input-path', '-ip',
        type=str,
        default='',
        required=False,
        help="""
        Open and read data from file path.
        """
    )
    parser.add_argument(
        '--input-bz2', '-iz',
        action='store_true',
        required=False,
        help="""
        Run input through BZ2 decompression before processing.
        """
    )

    # Output args
    parser.add_argument(
        '--output-std', '-os',
        action='store_true',
        required=False,
        help="""
        Write output to the stdout pipe.
        """
    )
    parser.add_argument(
        '--output-path', '-op',
        type=str,
        required=False,
        help="""
        Write output to the specified file path.
        """
    )
    parser.add_argument(
        '--output-bz2', '-oz',
        action='store_true',
        required=False,
        help="""
        Run output through BZ2 compression before writing.
        """
    )

    # Mode argument(s)
    parser.add_argument(
        '--mode', '-m',
        default='classic',
        choices=['classic', 'modern', 'byte'],
        required=False,
        help="""
        Which mode the enigma machine will operate in. (default: classic)
        Classic mode will only process characters A through Z, will
        capitalize lowercase letters, and will remove invalid ones.
        Modern mode will preserve case, and invalid characters
        will pass through unchanged (without affecting rotors).
        Byte mode will process any 8-bit character, but REQUIRES that
        byte-compatible rotors and reflectors be passed into the machine.
        """
    )

    # Other arguments
    parser.add_argument(
        '--chunk-size', '-c',
        type=int,
        default=128,
        required=False,
        help="""
        Chunk size for reading and writing data.
        """
    )
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        required=False,
        help="""
        Benchmark the processing time (prints results to stderr).
        """
    )
    parser.add_argument(
        '--no-progress', '-np',
        action='store_true',
        required=False,
        help="""
        Suppress the progress meter that is normal written to stderr.
        """
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        required=False,
        help="""
        Enable verbosity; printing LOTS of messages to stderr.
        """
    )
    parser.add_argument(
        '--typewriter', '-t',
        action='store_true',
        required=False,
        help="""
        Enable typewriter mode. Press a key, and the translated key is written
        to the console; similar to an actual enigma machine. Not particularly
        useful, just really cool to play with. (currently Windows only)
        """
    )

    if len(sys.argv) == 1:
        print('("--help" flag inferred from no args)\n')
        sys.argv.append('--help')
    args = parser.parse_args()

    # Initialize the enigma machine using specified rotors or a state file
    machine = None
    if args.state and not args.state_create:
        state = bz2.open(args.state, 'rb').read()
        machine = emachine.Machine(mode=emachine.Mode[args.mode], state=state)
    elif args.state_seed:
        machine = emachine.Machine(stateSeed=args.state_seed)
    else:
        if not args.rotors or not args.reflector:
            raise ValueError('Rotors and reflectors were not provided')
        machine = emachine.Machine(
            mode=emachine.Mode[args.mode],
            plugboardStack=args.plugboard,
            rotorStack=args.rotors,
            reflector=args.reflector,
            verbose=args.verbose
        )

    # If a state file needs to be created, save it and exit
    if args.state_create:
        return bz2.open(args.state, 'wb').write(machine.stateGet())

    # If the state shall be printed, make it so, and exit
    if args.state_print:
        print('PLUGBOARD:', ' '.join(_serialize_plugboard(machine.plugboard)))
        for i, rotor in enumerate(machine.rotors):
            print(
                'ROTOR:', i + 1, rotor._name,
                'SETTING:', rotor._abet[rotor.setting],
                'NOTCHES:', ', '.join([rotor._abet[n] for n in rotor.notches])
            )
        print('REFLECTOR:', machine.reflector._name)
        # print('RAW:', machine.stateGet())
        return

    # Typewriter mode
    if args.typewriter:
        print('Welcome to typewriter mode! To begin transcoding, just type!')
        print('Press Ctrl+C to exit. (backspace and arrow keys will not work)')
        print()

        import msvcrt
        char_in = msvcrt.getch()

        while char_in != b'\x03':

            char_out = char_in

            if char_in == b'\r':
                char_out = b'\r\n'

            elif char_in == b'\x08':
                char_out = b''

            else:
                char_out = machine.translateChunk(
                    char_in,
                    sanitize=args.sanitize
                )

            sys.stdout.buffer.write(char_out)
            sys.stdout.flush()
            char_in = msvcrt.getch()

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
        progressCallback=callback
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
        if args.state:
            open(args.state, 'wb').write(machine.stateGet())

# Run if main
if __name__ == '__main__':
    main()
