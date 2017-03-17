# stdlib imports
import array
import enum
import io
import pickle
import random

# third party imports

# local module imports
import enigma.rotors as rotors


class OUTPUT(enum.Enum):
    PENTAGRAPH = 1
    CONTINUOUS = 2


class Machine:
    def __init__(
            self,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None,
            stateSeed='',
            outputMode=OUTPUT.PENTAGRAPH
            ):
        """Initialize a new Enigma Machine.
        """
        # Initialize the empty variables
        self.plugboard = []
        self.rotors = []
        self.reflector = None

        self.pentacount = 0

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

        # Link all of the rotors and reflectors together
        self._link()

        # Go ahead and set a break point
        self.breakSet()

        # Store the mode
        self.mode = outputMode

    def _initPlugboard(self, stack):
        '''Initialize the plugboard translation matrix'''
        # Start with an 1:1 mapping
        self.plugboard = array.array('b', [i for i in range(26)])

        # Swap up the mappings for each desired pair
        for pair in stack:
            x = pair[0]
            y = pair[1]
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

    def _link(self):
        """Link the rotors and reflectors together in a node-like fashion"""
        # Link the rotors forward
        for i in range(len(self.rotors))[:-1]:
            self.rotors[i].next = self.rotors[i + 1]

        # Link the rotors backwards
        for i in range(len(self.rotors))[1:]:
            self.rotors[i].previous = self.rotors[i - 1]

        # Link the reflector into the loop
        self.rotors[-1].next = self.reflector
        self.reflector.previous = self.rotors[-1]

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

    def translatePin(self, pin):
        """
        Translate a singular pin (as an integer) through the plugboard,
        rotors, reflector, and back again.
        """
        # Isolate the first (maybe only) rotor
        rotor = self.rotors[0]

        # Forward through the plugboard
        pin = self.plugboard[pin]

        # Send the pin through the rotors
        pin = rotor.translate(pin)

        # Backwards through the plugboard
        pin = self.plugboard[pin]

        # Step the rotors
        rotor.step()

        # Return the fruits of our labor
        return pin

    def translateChunk(self, chunk_in):
        """
        Translate a non-empty bytes or bytearray object through the machine.
        """
        # Initialize the outgoing chunk
        chunk_out = bytearray()

        # Text modes
        for byte_in in chunk_in:
            # Check the byte
            byte_out = self._checkByte(byte_in)
            if not byte_out:
                continue

            # Convert the byte to a pin
            byte_out -= 65

            # Run it through the machine
            byte_out = self.translatePin(byte_out)

            # Convert it back into a byte
            byte_out += 65

            # Append it to the array
            chunk_out.append(byte_out)

            # If pentagraph mode is on, increment and Check
            if self.mode == OUTPUT.PENTAGRAPH:
                self.pentacount += 1
                if self.pentacount == 5:
                    chunk_out.append(0x20)
                    self.pentacount = 0

        # Return the processed chunk
        return chunk_out

    def translateString(self, s, **kwargs):
        """Lazy method to translate a string"""
        # Reset the pentagraph counter
        self.pentacount = 0

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
        # Reset the pentagraph counter
        self.pentacount = 0

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
