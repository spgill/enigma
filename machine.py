# stdlib imports
import pickle

# third party imports
# import colorama

# local module imports
import enigma.rotors as rotors


class Machine:
    '''Start a new machine with clean states and rotors'''

    def __init__(
            self,
            plugboardStack=[],
            rotorStack=[],
            reflector=None,
            state=None
            ):
        """Initialize Enigma Machine with all it's instantiated components"""
        # Initialize the empty variables
        self.plugboard = []
        self.rotors = []
        self.reflector = None

        # Unpack the state
        if state:
            self.stateSet(state)

        # or unpack the args into the class
        else:
            self._initPlugboard(plugboardStack)
            self._initRotors(rotorStack)
            self._initReflector(reflector)

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

    def _checkChar(self, c):
        '''Check a one-character string for enigma compatibility'''
        assert isinstance(c, str)
        assert len(c) == 1
        c = c.upper()

        # Check the character is in the alphabet
        if c not in rotors._RotorBase._abet:
            raise ValueError(c + ' is not an Enigma compatible character')

        return c

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

    def transcode(self, stream, skip_invalid=False, trace=False):
        '''
        Transcode any object of iterable strings through
        the plugboard, rotors, reflector, and back out.

        Optionally, you can have the generator yield transformation
        traces instead of just the transformed characters.
        '''

        # start iterating through the incoming stream
        for char_in in stream:
            # check the character
            if skip_invalid:
                try:
                    char = self._checkChar(char_in)
                except ValueError:
                    yield char_in
                    continue
            else:
                char = self._checkChar(char_in)

            # convert it into a pin and run it through the plugboard
            pin = rotors._RotorBase._abet.index(char)
            pin = self.plugboard[pin]

            # iterate through roters in forward order
            stack = []
            for rotor in self.rotors:
                # translate the pin forward through the rotor
                newpin = rotor.translate_forward(pin)

                # log the translation
                stack.append((pin, newpin))
                pin = newpin

            # reflect the pin through the reflector and log it
            newpin = self.reflector.translate_forward(pin)
            stack.append((pin, newpin))
            pin = newpin

            # iterate through the rotors in reverse
            for rotor in reversed(self.rotors):
                # translate the pin in reverse
                newpin = rotor.translate_reverse(pin)

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
            if char_in.islower():
                char_out = char_out.lower()

            # if a trace is required, yield that
            if trace:
                yield stack + [char_out]

            # if a character is required, yield THAT
            else:
                yield char_out

    def transcodeString(self, s, **kwargs):
        return ''.join(self.transcode(s, **kwargs))
