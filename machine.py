# stdlib imports
import io
import pickle
import sys

# third party imports
import colorama

# local module imports
import enigma.rotors as rotors


class Machine:
    '''Start a new machine with clean states and rotors'''

    def __init__(
            self,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None,
            verbose=False
            ):
        """Initialize Enigma Machine with all it's instantiated components"""
        # Initialize the empty variables
        self.plugboard = []
        self.rotors = []
        self.reflector = None
        self.verbose = verbose

        # Unpack the state
        if state:
            self.stateSet(state)

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
        # Start with an untampered matrix
        self.plugboard = list(range(26))

        # Swap up the mappings for each desired pair
        for pair in stack:
            x = rotors._RotorBase._abet.index(pair.upper()[0])
            y = rotors._RotorBase._abet.index(pair.upper()[1])
            self.plugboard[x] = y
            self.plugboard[y] = x

    def _initRotors(self, stack):
        '''Check the passed rotors to see if they're strings or real rotors'''
        for i, entry in enumerate(stack):

            # if it's an actual rotor instance, keep on swimming
            if isinstance(entry, rotors._RotorBase):
                self.rotors.append(entry)
                continue

            # if it's a string, turn it into a rotor
            if isinstance(entry, str):
                self.rotors.append(rotors.stringToRotor(entry))
                continue

            # else, throw a hissy
            print('OBJ', entry, 'TYPE', type(entry))
            raise TypeError('Unknown type of rotor passed into the machine')

    def _initReflector(self, reflector):
        '''Check to make sure a real reflector was passed in'''
        self.reflector = reflector

        # if it's an actual reflector instance, keep on swimming
        if isinstance(self.reflector, rotors._ReflectorBase):
            return

        # if it's a string, turn it into a reflector
        if isinstance(self.reflector, str):
            self.reflector = rotors.stringToReflector(self.reflector)
            return

        # else, throw a hissy
        raise TypeError('Unknown type of reflector passed into the machine')

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

    def _checkChar(self, c):
        '''Sanitize a single character'''
        value = ord(c)

        # Uppercase alpha. Good to go.
        if value >= 65 and value <= 90:
            return chr(value)

        # Lowercase alpha. Let's capitalize it.
        elif value >= 97 and value <= 122:
            return chr(value - 32)

        # Invalid character.
        else:
            return False

    def vprint(self, template, args=[], kwargs={}):
        """Format and print a message to stderr if verbosity is enabled"""
        if not self.verbose: return False

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

    def breakSet(self):
        '''Save the current state to be easily returned to later'''
        self._breakstate = self.stateGet()

    def breakGo(self):
        '''Return to the saved break state'''
        assert hasattr(self, '_breakstate')
        self.stateSet(self._breakstate)

    def transcode(self, stream, sanitize=False, trace=False):
        '''
        Transcode any iterable object of string characters through
        the plugboard, rotors, reflector, and back out.

        Optionally, you can have the generator yield transformation
        traces instead of just the transformed characters.
        '''

        self.vprint('Stream received for transcoding')

        # start iterating through the incoming stream
        for char_in in stream:
            self.vprint('Character {0!r}', [char_in])

            # check the character
            char = self._checkChar(char_in)
            if not char:
                if not sanitize:
                    self.vprint('  Ignoring invalid character')
                    yield char_in
                else:
                    self.vprint('  Skipping invalid character')
                continue

            # convert it into a pin and run it through the plugboard
            pin = rotors._RotorBase._abet.index(char)
            self.vprint('  Converted to pin {0!r}', [pin])
            pin = self.plugboard[pin]
            self.vprint('  Plugboard to pin {0!r}', [pin])

            # iterate through roters in forward order
            stack = []
            for rotor in self.rotors:
                # translate the pin forward through the rotor
                self.vprint(
                    '  Sending pin {0!r} forward thru {F.GREEN}{1}{F.WHITE}',
                    [pin, rotor._short]
                )
                newpin = rotor.translate_forward(pin)
                self.vprint(
                    '  Received pin {0!r} from {F.GREEN}{1}{F.WHITE}',
                    [newpin, rotor._short]
                )

                # log the translation
                stack.append((pin, newpin))
                pin = newpin

            # reflect the pin through the reflector and log it
            self.vprint(
                '  Sending pin {0!r} thru {F.GREEN}{1}{F.WHITE}',
                [pin, self.reflector._short]
            )
            newpin = self.reflector.translate_forward(pin)
            self.vprint(
                '  Received pin {0!r} from {F.GREEN}{1}{F.WHITE}',
                [newpin, self.reflector._short]
            )
            stack.append((pin, newpin))
            pin = newpin

            # iterate through the rotors in reverse
            for rotor in reversed(self.rotors):
                # translate the pin in reverse
                self.vprint(
                    '  Sending pin {0!r} reverse thru {F.GREEN}{1}{F.WHITE}',
                    [pin, rotor._short]
                )
                newpin = rotor.translate_reverse(pin)
                self.vprint(
                    '  Received pin {0!r} from {F.GREEN}{1}{F.WHITE}',
                    [newpin, rotor._short]
                )

                # log the translation
                stack.append((pin, newpin))
                pin = newpin

            # step the rotors in order
            step = True
            for rotor in self.rotors:
                if step:
                    step = rotor.step()
                    if not step:
                        break

            # Run the pin back through the plugboard again
            pin = self.plugboard[pin]

            # get the resulting character
            char_out = rotors._RotorBase._abet[pin]
            if not sanitize and char_in.islower():
                char_out = char_out.lower()

            # if a trace is required, yield that
            if trace:
                yield stack + [char_out]

            # if a character is required, yield THAT
            else:
                yield char_out

    def transcodeString(self, s, **kwargs):
        """Transcode and return a string"""
        return ''.join(self.transcode(s, **kwargs))

    def _readChunks(self, stream, chunkSize):
        """Yield discrete chunks from a stream."""
        while True:
            data = stream.read(chunkSize)
            if not data:
                break
            yield data

    def transcodeStream(
            self,
            stream_in,
            stream_out=None,
            chunkSize=128,
            **kwargs
            ):
        """Transcode a stream (file-like object) chunk by chunk."""
        # If no outgoing stream is specified, make one
        if not stream_out:
            stream_out = io.StringIO()

        # Iterate through chunks
        for chunk_in in self._readChunks(stream_in, chunkSize):
            chunk_out = str()
            for char in self.transcode(chunk_in, **kwargs):
                chunk_out += char
            stream_out.write(chunk_out)

        # Return the outgoing stream (in case one wasn't passed in)
        return stream_out
