# stdlib imports
import argparse

# local module imports
import enigma.machine as machine


parser = argparse.ArgumentParser(
    description='Process some data through a simulated Enigma machine'
)

parser.add_argument(
    '--rotors', '-ro',
    nargs='+',
    type=str,
    required=True
)

parser.add_argument(
    '--reflector', '-rf',
    type=str,
    required=True
)

parser.add_argument(
    'input',
    type=str
)


args = parser.parse_args()
print()
print(args)

m = machine.Machine(None, args.rotors, args.reflector)
print(m.transcodeString(args.input))
