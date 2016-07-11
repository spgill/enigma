# stdlib imports
import enum
import io
import pickle
import random
import sys

# third party imports
import colorama

# local module imports
import rotors


class Mode(enum.Enum):
    """Enumeration class for Enigma Machine modes."""
    classic = 0
    modern = 1
    byte = 2


class Machine:
    def __init__(
            self,
            mode=Mode.classic,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None,
            stateSeed='',
            verbose=False
            ):
        """Initialize a new Enigma Machine.

        Keyword arguments;
        -   mode: Which mode the enigma machine will operate in.
            MUST use the enum class to specify mode. Default is classic.
            Classic mode will only process characters A through Z, will
            capitalize lowercase letters, and will remove invalid ones.
            Modern mode will preserve case, and invalid characters
            will pass through unchanged (without affecting rotors).
            Byte mode will process any 8-bit character, but REQUIRES that
            byte-compatible rotors and reflectors be passed into the machine.
        """
        # Initialize the empty variables
        self.mode = mode
        self.plugboard = []
        self.rotors = []
        self.reflector = None
        self.verbose = verbose

        # Unpack the state
        if state:
            self.stateSet(state)

        # If seed is present, generate randomized state
        elif stateSeed:
            self.stateRandom(stateSeed)

        # or unpack the args into the class
        else:
            self._initPlugboard(plugboardStack)
            self._initRotors(rotorStack)
            self._initReflector(reflector)

        # initialize verbosity
        self._initVerbosity()

        # go ahead and set a break point
        self.breakSet()

    def _initPlugboard(self, stack):
        '''Initialize the plugboard translation matrix'''
        size = 256 if self.mode is Mode.byte else 26

        # Start with an untampered matrix
        self.plugboard = list(range(size))

        # Swap up the mappings for each desired pair
        for pair in stack:
            x = pair[0]
            y = pair[1]
            if self.mode is not Mode.byte:
                x = rotors._RotorBase._abet.index(x.upper())
                y = rotors._RotorBase._abet.index(y.upper())
            self.plugboard[x] = y
            self.plugboard[y] = x

    def _initRotors(self, stack):
        '''Check the passed rotors to see if they're strings or real rotors'''
        for i, entry in enumerate(stack):

            rotor = None

            # if it's an actual rotor instance, keep on swimming
            if isinstance(entry, rotors._RotorBase):
                rotor = entry

            # if it's a string, turn it into a rotor
            if isinstance(entry, str):
                rotor = rotors.stringToRotor(entry)

            # Must be invalid then
            if rotor is None:
                raise TypeError(
                    'Unknown type of rotor passed into the machine'
                )

            # Make sure the rotor matches the mode
            if self.mode == Mode.byte and rotor._byte_compatible is False:
                raise ValueError(
                    'Byte-compatible rotors MUST be used with byte mode'
                )
            if self.mode != Mode.byte and rotor._byte_compatible is True:
                raise ValueError(
                    'Byte-compatible rotors may not be used with text modes'
                )

            # Append it, yo
            self.rotors.append(rotor)

    def _initReflector(self, reflector):
        '''Check to make sure a real reflector was passed in'''
        # if it's an actual reflector instance, keep on swimming
        if isinstance(reflector, rotors._ReflectorBase):
            self.reflector = reflector

        # if it's a string, turn it into a reflector
        if isinstance(reflector, str):
            self.reflector = rotors.stringToReflector(reflector)

        # Must be invalid then
        if self.reflector is None:
            raise TypeError(
                'Unknown type of reflector passed into the machine'
            )

        # Make sure the reflector matches the mode
        if self.mode == Mode.byte and self.reflector._byte_compatible is False:
            raise ValueError(
                'Byte-compatible reflectors MUST be used with byte mode'
            )
        if self.mode != Mode.byte and self.reflector._byte_compatible is True:
            raise ValueError(
                'Byte-compatible reflectors may not be used with text modes'
            )

    def _initVerbosity(self):
        """Copy the machine's verbose flag to the rotors and the reflector"""
        # Let 'em know
        self.vprint('Verbosity enabled')

        # copy to rotors and the reflector
        self.vprint('Copying verbose flag to rotors and the reflector')
        colorama.init()
        for r in self.rotors:
            r.verbose = self.verbose
            r.verbose_soundoff()
        self.reflector.verbose = self.verbose
        self.reflector.verbose_soundoff()

    def _checkByte(self, b):
        '''Sanitize a single character'''
        # Uppercase alpha. Good to go.
        if b >= 65 and b <= 90:
            return b

        # Lowercase alpha. Let's capitalize it.
        elif b >= 97 and b <= 122:
                return b - 32

        # Invalid character.
        else:
            return False

    def vprint(self, template, args=[], kwargs={}):
        """Format and print a message to stderr if verbosity is enabled"""
        if not self.verbose:
            return False

        kwargs.update({
            'self': self,
            'B': colorama.Back,
            'F': colorama.Fore,
            'S': colorama.Style
        })
        pre = '|{F.GREEN}   machine{F.WHITE}:'
        sys.stderr.write((pre + template).format(*args, **kwargs) + '\n')
        return True

    def stateGet(self):
        '''Get a serialized state of the machine. (the 'settings')'''
        return pickle.dumps((
            self.plugboard,
            self.rotors,
            self.reflector
        ), -1)

    def stateSet(self, state):
        '''Set the state of the machine from a serialized input'''
        (
            self.plugboard,
            self.rotors,
            self.reflector
        ) = pickle.loads(state)

    def stateRandom(self, seed):
        """Randomly generate a state from a string seed"""
        # Seed the random generator
        random.seed(seed)

        # Generate a random plugboard
        plugboardStack = []
        abet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        for i in range(random.randint(0, 13)):
            pair = ''
            for j in range(2):
                k = random.randrange(0, len(abet))
                pair += abet[k]
                del abet[k]
            plugboardStack.append(pair)
        self._initPlugboard(plugboardStack)

        # Generate random rotors (there will always be three)
        rotorStack = []
        abet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        rotorNames = sorted(
            [r._short for r in rotors._RotorBase.__subclasses__()]
        )
        rotorNames.remove('base-ref')
        for i in range(3):
            rotor = '{0}:{1}:{2}'.format(
                random.choice(rotorNames),
                random.choice(abet),
                random.choice(abet)
            )
            rotorStack.append(rotor)
        self._initRotors(rotorStack)

        # Pick a random reflector
        reflNames = sorted(
            [r._short for r in rotors._ReflectorBase.__subclasses__()]
        )
        reflector = random.choice(reflNames)
        self._initReflector(reflector)

    def breakSet(self):
        '''Save the current state to be easily returned to later'''
        self._breakstate = self.stateGet()

    def breakGo(self):
        '''Return to the saved break state'''
        assert hasattr(self, '_breakstate')
        self.stateSet(self._breakstate)

    def stepRotors(self):
        """Step the machine's rotors once, in order."""
        step = True
        for rotor in self.rotors:
            if step:
                step = rotor.step()
                if not step:
                    break

    def translatePin(self, pin):
        """
        Translate a singular pin (as an integer) through the plugboard,
        rotors, reflector, and back again.
        """
        # Forward through the plugboard
        pin = self.plugboard[pin]

        # Forward through the rotors
        for rotor in self.rotors:
            pin = rotor.translateForward(pin)

        # Reflect it
        pin = self.reflector.translateForward(pin)

        # Backwards through the rotors
        for rotor in reversed(self.rotors):
            pin = rotor.translateReverse(pin)

        # Backwards through the plugboard
        pin = self.plugboard[pin]

        # Step the rotors
        self.stepRotors()

        # Return the fruits of our labor
        return pin

    def translateChunk(self, chunk_in):
        """
        Translate a non-empty bytes or bytearray object through the machine.
        """
        # Initialize the outgoing chunk
        chunk_out = bytearray()

        # Byte mode switch
        if self.mode is Mode.byte:
            for byte_in in chunk_in:
                chunk_out.append(self.translatePin(byte_in))

        # Text modes
        else:
            for byte_in in chunk_in:
                # Check the byte
                byte_out = self._checkByte(byte_in)
                if not byte_out:
                    if self.mode is Mode.modern:
                        chunk_out.append(byte_in)
                    continue

                # Convert the byte to a pin
                byte_out -= 65

                # Run it through the machine
                byte_out = self.translatePin(byte_out)

                # Convert it back into a byte
                byte_out += 65
                if self.mode is Mode.modern and byte_in > 90:
                    byte_out += 32

                # Append it to the array
                chunk_out.append(byte_out)

        # Return the processed chunk
        return chunk_out

    def translateString(self, s, **kwargs):
        """Lazy method to translate a string"""
        return str(self.translateChunk(bytes(s), **kwargs))

    def _readChunks(self, stream, chunkSize):
        """Yield discrete chunks from a stream."""
        while True:
            data = stream.read(chunkSize)
            if not data:
                break
            yield data

    def _streamSize(self, stream):
        """Return the size of a stream in bytes"""
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(0)
        return size

    def translateStream(
            self,
            stream_in,
            stream_out=None,
            progressCallback=None,
            chunkSize=128,
            **kwargs
            ):
        """Translate a stream (file-like object) chunk by chunk."""
        # Figure out the size of the input stream
        stream_in_size = self._streamSize(stream_in)

        # If no outgoing stream is specified, make one
        if not stream_out:
            stream_out = io.BytesIO()
        stream_out_size = 0

        # Make the initial call to the progress function
        if progressCallback:
            progressCallback(stream_out_size, stream_in_size)

        # Iterate through chunks
        for chunk_in in self._readChunks(stream_in, chunkSize):
            chunk_out = self.translateChunk(chunk_in, **kwargs)
            stream_out.write(chunk_out)
            stream_out_size += chunkSize
            if progressCallback:
                progressCallback(stream_out_size, stream_in_size)

        # Return the outgoing stream (in case one wasn't passed in)
        return stream_out
