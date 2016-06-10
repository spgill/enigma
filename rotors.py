# stdlib module imports
import sys

# third-party module imports
import colorama


def vbprint(template, args=[], kwargs={}):
    """Format and print a message to stderr if verbosity is enabled"""
    global ENIGMA_verbose
    if ENIGMA_verbose:
        sys.stderr.write(template.format(*args, **kwargs) + '\n')


def stringToRotor(s):
    '''Turn a string into an instantiated rotor'''
    # Get all immediate subclasses of the rotor base class
    classes = _RotorBase.__subclasses__()

    # split the argument into name and settings
    split = s.split(':')

    # lookup the rotor
    name = split[0]
    rotor = None
    for c in classes:
        if name == c._short:
            rotor = c
            break
    if not rotor:
        raise ValueError(name + ' is not a valid rotor short-name')

    # extract the other settings
    setting = split[1].upper() if len(split) > 1 else None
    notches = split[2].upper() if len(split) > 2 else None

    # Instantiate the rotor
    return rotor(setting=setting, notches=notches)


def stringToReflector(s):
    '''Turn a string into an instantiated reflector'''
    # Get all immediate subclasses of the reflector base class
    classes = _ReflectorBase.__subclasses__()
    reflector = None
    for c in classes:
        if s == c._short:
            reflector = c
            break
    if not reflector:
        raise ValueError(s + ' is not a valid reflector short-name')

    # Instantiate the reflector
    return reflector()


class _RotorBase:
    '''Base rotor class. Inherited by all proper rotors. NOT FOR CRYPTO USE!'''

    # class variables
    _name = 'BASE ROTOR'
    _short = 'base'
    _abet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _wiring = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _notches = 'A'

    def __init__(self, setting=None, notches=None):
        '''Instantiate a new Rotor with custom or default settings'''
        # Initial rotor setting. 0 if not defined.
        if setting:
            self.setting = self._abet.index(setting)
        else:
            self.setting = 0  # A

        # Initial verbosity flag
        self.verbose = False

        # Initialize and program wiring matrices
        self.wiring_forward = list(range(26))
        self.wiring_reverse = list(range(26))

        for i in range(26):
            x = i
            y = self._abet.index(self._wiring[i])
            self.wiring_forward[x] = y - x
            self.wiring_reverse[y] = x - y

        # sys.stderr.write(repr(self._wiring) + '\n')
        # sys.stderr.write(repr(self.wiring_forward) + '\n')
        # sys.stderr.write(repr(self.wiring_reverse) + '\n\n')

        # Initialize the notch matrix
        self.notches = []
        for notch in notches or self._notches:
            self.notches.append(self._abet.index(notch))

    def _shift(self, s, n=1):
        '''Shift a string by n characters'''
        return s[n:] + s[0:n]

    def _loop(self, n):
        '''Constrain a number N such that 0 <= N <= 25'''
        while n < 0 or n > 25:
            if n > 25:
                n -= 26
            if n < 0:
                n += 26
        return n

    def vprint(self, template, args=[], kwargs={}):
        """Format and print a message to stderr if verbosity is enabled"""
        if self.verbose:
            kwargs.update({
                'self': self,
                'B': colorama.Back,
                'F': colorama.Fore,
                'S': colorama.Style
            })
            pre = '|{F.GREEN}{self._short:>10}{F.WHITE}:'
            sys.stderr.write((pre + template).format(*args, **kwargs) + '\n')

    def verbose_soundoff(self):
        self.vprint('Verbosity enabled')

    def step(self):
        '''
        Step the rotor by one letter.
        Returns True if the rotor hit its notch and the
        next rotor in the series should be advanced by one letter as well
        '''
        # check for notches
        notch = False
        if self.setting in self.notches:
            notch = True

        # increment rotor index, checking for loop condition
        self.setting = self._loop(self.setting + 1)

        # return the flag
        return notch

    def translate_forward(self, pin_in):
        '''Translate one pin through this rotor in first pass mode.'''
        # char = self.abet[pin_in]
        # pin_out = self.wiring.index(char)
        # return pin_out
        mod = self.wiring_forward[self._loop(pin_in + self.setting)]
        return self._loop(pin_in + self.setting + mod)

    def translate_reverse(self, pin_in):
        '''Translate one pin through this rotor in reverse pass mode.'''
        # char = self.wiring[pin_in]
        # pin_out = self.abet.index(char)
        # return pin_out
        mod = self.wiring_reverse[self._loop(pin_in + self.setting)]
        return self._loop(pin_in + self.setting + mod)


class _ReflectorBase(_RotorBase):
    '''Simple adapter to the Rotor base class for defining reflectors'''

    # class variables
    _name = 'BASE REFLECTOR'
    _short = 'base-ref'
    _abet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _wiring = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # def __init__(self):
    #     '''More or less completely cutting out the useless class vars'''
    #     pass

    def nono(self):
        '''Throw an error because this is not valid for reflectors'''
        raise RuntimeError('YOU CANNOT DO THAT TO A REFLECTOR. CHECK YO SELF.')

    # Equate the bad functions as 'no-no' functions so they'll throw errors
    step = nono
    translate_reverse = nono


# # # rotors # # #
class CommercialI(_RotorBase):
    _name = 'Commercial Enigma - Rotor I'
    _short = 'com1'
    _wiring = 'DMTWSILRUYQNKFEJCAZBPGXOHV'
    _notches = 'Q'


class CommercialII(_RotorBase):
    _name = 'Commercial Enigma - Rotor II'
    _short = 'com2'
    _wiring = 'HQZGPJTMOBLNCIFDYAWVEUSRKX'
    _notches = 'E'


class CommercialIII(_RotorBase):
    _name = 'Commercial Enigma - Rotor III'
    _short = 'com3'
    _wiring = 'UQNTLSZFMREHDPXKIBVYGJCWOA'
    _notches = 'V'


class RailwayI(_RotorBase):
    _name = 'Railway Enigma - Rotor I'
    _short = 'rail1'
    _wiring = 'JGDQOXUSCAMIFRVTPNEWKBLZYH'
    _notches = 'Q'


class RailwayII(_RotorBase):
    _name = 'Railway Enigma - Rotor II'
    _short = 'rail2'
    _wiring = 'NTZPSFBOKMWRCJDIVLAEYUXHGQ'
    _notches = 'E'


class RailwayIII(_RotorBase):
    _name = 'Railway Enigma - Rotor III'
    _short = 'rail3'
    _wiring = 'JVIUBHTCDYAKEQZPOSGXNRMWFL'
    _notches = 'V'


class SwissI(_RotorBase):
    _name = 'Swiss K Enigma - Rotor I'
    _short = 'swiss1'
    _wiring = 'PEZUOHXSCVFMTBGLRINQJWAYDK'
    _notches = 'Q'


class SwissII(_RotorBase):
    _name = 'Swiss K Enigma - Rotor II'
    _short = 'swiss2'
    _wiring = 'ZOUESYDKFWPCIQXHMVBLGNJRAT'
    _notches = 'E'


class SwissIII(_RotorBase):
    _name = 'Swiss K Enigma - Rotor III'
    _short = 'swiss3'
    _wiring = 'EHRVXGAOBQUSIMZFLYNWKTPDJC'
    _notches = 'V'


class EnigmaI(_RotorBase):
    _name = 'Enigma I - Rotor I'
    _short = 'enig1'
    _wiring = 'EKMFLGDQVZNTOWYHXUSPAIBRCJ'
    _notches = 'Q'


class EnigmaII(_RotorBase):
    _name = 'Enigma I - Rotor II'
    _short = 'enig2'
    _wiring = 'AJDKSIRUXBLHWTMCQGZNPYFVOE'
    _notches = 'E'


class EnigmaIII(_RotorBase):
    _name = 'Enigma I - Rotor III'
    _short = 'enig3'
    _wiring = 'BDFHJLCPRTXVZNYEIWGAKMUSQO'
    _notches = 'V'


class ArmyIV(_RotorBase):
    _name = 'M3 Army - Rotor IV'
    _short = 'army4'
    _wiring = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    _notches = 'J'


class ArmyV(_RotorBase):
    _name = 'M3 Army - Rotor V'
    _short = 'army5'
    _wiring = 'VZBRGITYUPSDNHLXAWMJQOFECK'
    _notches = 'Z'


class NavyVI(_RotorBase):
    _name = 'M3 & M4 Naval Enigma - Rotor VI'
    _short = 'navy6'
    _wiring = 'JPGVOUMFYQBENHZRDKASXLICTW'
    _notches = 'ZM'


class NavyVII(_RotorBase):
    _name = 'M3 & M4 Naval Enigma - Rotor VII'
    _short = 'navy7'
    _wiring = 'NZJHGRCXMYSWBOUFAIVLPEKQDT'
    _notches = 'ZM'


class NavyVIII(_RotorBase):
    _name = 'M3 & M4 Naval Enigma - Rotor VIII'
    _short = 'navy8'
    _wiring = 'FKQHTLXOCBJSPDZRAMEWNIUYGV'
    _notches = 'ZM'


# # # REFLECTORS # # #
class ReflectorRailway(_ReflectorBase):
    _name = 'Railway Enigma - Reflector'
    _short = 'rail-ref'
    _wiring = 'QYHOGNECVPUZTFDJAXWMKISRBL'


class ReflectorSwiss(_ReflectorBase):
    _name = 'Swiss K Enigma - Reflector'
    _short = 'swiss-ref'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


class ReflectorBeta(_ReflectorBase):
    _name = 'Reflector - Beta'
    _short = 'ref-beta'
    _wiring = 'LEYJVCNIXWPBQMDRTAKZGFUHOS'


class ReflectorGamma(_ReflectorBase):
    _name = 'Reflector - Gamma'
    _short = 'ref-gamma'
    _wiring = 'FSOKANUERHMBTIYCWLQPZXVGJD'


class ReflectorA(_ReflectorBase):
    _name = 'Reflector - A'
    _short = 'ref-a'
    _wiring = 'EJMZALYXVBWFCRQUONTSPIKHGD'


class ReflectorB(_ReflectorBase):
    _name = 'Reflector - B'
    _short = 'ref-b'
    _wiring = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'


class ReflectorC(_ReflectorBase):
    _name = 'Reflector - C'
    _short = 'ref-c'
    _wiring = 'FVPJIAOYEDRZXWGCTKUQSBNMHL'


class ReflectorBThin(_ReflectorBase):
    _name = 'Reflector - B Thin'
    _short = 'ref-bt'
    _wiring = 'ENKQAUYWJICOPBLMDXZVFTHRGS'


class ReflectorCThin(_ReflectorBase):
    _name = 'Reflector - A Thin'
    _short = 'ref-at'
    _wiring = 'RDOBJNTKVEHMLFCWZAXGYIPSUQ'


# # # Module main method # # #
if __name__ == '__main__':
    r = SwissIII()
    print(r._name)
    for i in range(26):
        print('\nSETTING', r._abet[r.setting])
        print('STEP!')
        print('NOTCHED?', r.step())

    print('TESTING_SHIFT_METHOD')
    s = '012345abcdef'
    print('ORIGINAL', s)
    print('SHIFT   ', r._shift(s))
    print('SHIFT_n1', r._shift(s, 1))
    print('SHIFT_n2', r._shift(s, 2))
    print('SHIFT_n3', r._shift(s, 3))
    print('SHIFT_n4', r._shift(s, 4))
    print('SHIFT_n5', r._shift(s, 5))
    print('SHIFT_n6', r._shift(s, 6))
