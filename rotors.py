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
    classes = _RotorBase.__subclasses__() + _ByteRotorBase.__subclasses__()

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
    classes = _ReflectorBase.__subclasses__() + _ByteReflectorBase.__subclasses__()
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
    _byte_compatible = False

    def __init__(self, setting=None, notches=None):
        '''Instantiate a new Rotor with custom or default settings'''
        # Initial rotor setting. 0 if not defined.
        if setting:
            if self._byte_compatible:
                self.setting = setting
            else:
                self.setting = self._abet.index(setting)
        else:
            self.setting = 0  # A

        # Initial verbosity flag
        self.verbose = False

        # Calculate the size information
        self.wiring_size = len(self._wiring)
        self.wiring_start = 0
        self.wiring_end = self.wiring_size - 1

        # Initialize and program wiring matrices
        self.wiring_forward = list(range(self.wiring_size))
        self.wiring_reverse = list(range(self.wiring_size))

        for i in range(self.wiring_size):
            x = i
            y = self._wiring[i]
            if not self._byte_compatible:
                y = self._abet.index(y)
            self.wiring_forward[x] = y - x
            self.wiring_reverse[y] = x - y

        # Initialize the notch matrix
        self.notches = []
        for notch in notches or self._notches:
            if self._byte_compatible:
                self.notches.append(notch)
            else:
                self.notches.append(self._abet.index(notch))

    def _shift(self, s, n=1):
        '''Shift a string by n characters'''
        return s[n:] + s[0:n]

    def _loop(self, n):
        '''Constrain a number N such that 0 <= i <= N in a circular fashion'''
        while n < self.wiring_start or n > self.wiring_end:
            if n > self.wiring_end:
                n -= self.wiring_size
            if n < self.wiring_start:
                n += self.wiring_size
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

    def translateForward(self, pin_in):
        '''Translate one pin through this rotor in first pass mode.'''
        modifier = self.wiring_forward[self._loop(pin_in + self.setting)]
        out = self._loop(pin_in + modifier)
        return out

    def translateReverse(self, pin_in):
        '''Translate one pin through this rotor in reverse pass mode.'''
        modifier = self.wiring_reverse[self._loop(pin_in + self.setting)]
        out = self._loop(pin_in + modifier)
        return out


class _ByteRotorBase(_RotorBase):
    """Base class for byte-compatible rotors."""
    _name = 'BASE BYTE ROTOR'
    _short = 'basebyte'
    _wiring = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
    _notches = 'A'
    _byte_compatible = True


class _ReflectorBase(_RotorBase):
    '''Simple adapter to the Rotor base class for defining reflectors'''

    # class variables
    _name = 'BASE REFLECTOR'
    _short = 'base-ref'
    _abet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _wiring = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _byte_compatible = False

    def nono(self):
        '''Throw an error because this is not valid for reflectors'''
        raise RuntimeError('YOU CANNOT DO THAT TO A REFLECTOR, YO.')

    # Make the bad functions 'no-no' functions so they'll throw errors
    step = nono
    translateReverse = nono


class _ByteReflectorBase(_ReflectorBase):
    """Base class for byte-compatible reflectors."""

    # class variables
    _name = 'BASE BYTE REFLECTOR'
    _short = 'basebyte-ref'
    _wiring = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
    _byte_compatible = True


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


# # # BYTE-COMPATIBLE ROTORS # # #
class ByteI(_ByteRotorBase):
    _name = 'Byte Rotor I'
    _short = 'byte1'
    _wiring = b'\x9e\xe0\xee\x0e#\x89\xf1\x8f\x8d\xd1g\xfb l\xc0\xa61\x03\xb45I\x97s\xa3]\xbd\n_\xef\xc9\xb5\xc6:G\xecBm\xf3\x01\xca\xd0\xcdO\x17\x00\x10\xafc\xa9biFf\xd3W`\xb0w\xeb\xd5\x1d^\x050\x82\xe7C\xfeo\xfc;"r\t\'\x9d\xbb\x16\x99\xab\\4Ej$\rH\xbed\x88\xb7\x8bU\xc4\xa2t\xf2\xdc2V\xea\x18\xc2\xb6\xcc\xdb\xce!\xf5\x8e)\xb8\xfd\xf6AR\x1b\xbcq&\x1a-\x87\x06+\xc1\xdf\x02e\xaez\xba\xcb\x19\xe8\x13<\x9f\xe17\xe3\xb1\xd8\x94\xa19\xcfn\xdd\xd7%p}\x80\xff(\x15\x8a86\xde\xc7\xfa\x93\x83\x91\x0f\xb3L\x92\x81x{\x98\xb2\x04M\xd4\xbf\xd9\x0cv\x7fy\x90ka\xf8\xc5\xf9X\x08u\xe4\xa4\x96J@K\xa8\xc8\x85>\x1e\x9a\x1cD\x9b[\x1f\x86\xed\xd2\xa5,Q?\xd63\xa0\x0b/\xf4\xc3~\xb9\x14=Y.*\x11P\x9c\xad\xe2h\x84\xa7ZN\xda\x12\xf7\xe5\x07\xe6\x8c|\x95ST\xe9\xf0\xaa\xac'
    _notches = b'*'


class ByteII(_ByteRotorBase):
    _name = 'Byte Rotor II'
    _short = 'byte2'
    _wiring = b'5\x82\xb9i\x95\x8c\xb2\xc8\xb7\x97\xb8`!\x04\xa3\xccb[Z\x1d7\x94\xaa\xb0\xde\xa0p\xbcD\xbf,M\xc4Y2\x07J\x9d\xee_\xfa@\x1e\'\xdd^ej\x88\x1f\x18\xf5\xff\x1c$\xbb}\x14;\\\x90&\xba\x9f\xc5+\xab\x80\xa4\x0c\xef\x02\x7f\x9ao\x0f6gs]\x8d\xf9>\xd6\xa5\x83C\tq\xc7\x12\xc6/\xeb\xd9\x9e\xd3A\xd04OSr\xe7k\xd1\xc2\x98 =\x17\xbe\xec\xc3<\xcb\xed(\xe1\xb5\x81Q\n\x03\x96\x93\x84\x85\xdb0\x06\xe9\xceE:P\xf8\xa9\xe2L\xbdl"\xc1\xac\x1bK)\xfb\r\x15t\xd7\xae\x8a\xf2RTh\xea\x0b~\xf6\xady\xd4\xa2\xc9\xcd\xe0*\x00c\x13\x8b\xb3\x92\xe4\xb13\x19\x9b\xe8\xb41If\xa8n\xf7\x86\x8f%BvV\xda\xfdH\x91\x01\x08\xe3\xd5W\xf4\x1a9\xfc\xd2\xcaz\x99\xaf\x89\xa6\xc0\x87.\xd8-\xe5x\x11\x9cd\xf3\xa1|?\xf1N\xcfG\xdf{8\xdcwF\xe6Ua\xa7\x16\x0e\x05#\xfe\x10u\xf0\x8e\xb6Xm'
    _notches = b'\x1d'


class ByteIII(_ByteRotorBase):
    _name = 'Byte Rotor III'
    _short = 'byte3'
    _wiring = b'\xfb\xbf\xb0\x04\xad\x82\x93\xee\xd7}\xe5~\x8b\xa2\xfew\xef\xcd\xe8\xb8*\x9a\x88h\xf0\']\xa4DA\x16F\xbc\x86\x89`\xcf\x81\xc1[\x91\xa8{2\xf3q\x87 \xbd\xf1\xa6\xb9\xa1\xb6\x15\xaa\xd6\xde\x13\xec&o\x8d\x92|\x02\x0c\xd0n;C\xf4\x98\t\xd16\xb4g\xb7\x14M:>ci\xcc\xd2.\xc5\x9b\x01N\x84\xd5R\x0eu\x96\nksfJ\xda\x94\xc6\x1d\xe6V\xaeK\xbb\xe2#"\xf7\xc2\x83\xf9\xdbL\x06pU\x05\x00\xca\x1c\xddb\xbe\xdf\x97l\xd8\xb1\xf8O\x90\x8c\x1b\xb3S\xa9-\xe9+z0\xce\xc7@\x80\xb54\x03,G\x9ddY\xba\xffm\xed8\xfc3\xea\x8f\r\xc9%\xf6\xc3\x1evP\x1a\x0bH\xa7_\xdc\x95\xf5W\xeb<\xe7$B\x08\x8e\x1fXje()a\xf2\xfa?=\x9fI\x07\x7f\\\xaf\xa5\x857Qy\x12T\xac\xa3\xc0\x10\xab\x9e\x9c\xe3\xe4x\xe1\x191\x17\x0ft9\xd4\xb2Z\xc4\xc8\x8a\xcb\x18!\xe0\x995\xfdr/E\xd9^\xa0\x11\xd3'
    _notches = b'F'


class ByteIV(_ByteRotorBase):
    _name = 'Byte Rotor IV'
    _short = 'byte4'
    _wiring = b'\'b\xa2\x8ah\x97~2\x17e \x08&\x7f\xbf\xf3\xac\x8d\xa3{\xbc\x07iy\x16\xf8\x01$\xc0\xcd\xc7\xec\xfa\xef\xa4G/\xed\x98\x93\xf2\xb9\x02\xd8\x0f\xfdR\x90E\xbb\xe7\x0b\xb7\x00(\xe5\x1a\xc3\x87r\xa0m\xeef\x188\xc2\x15M\x8c\xe6!\xba\xd2g\xc5\xe8\x99\xf7aV;\xd1\xca\x95\xc4c\xa5\xc13\x10\xa7\x96+N`\xd0\xfe<U\xdd\x9d\x04I%\x811Z|\xb8\xd9\xb5\x82\xb3B\xeb\x05"\x0c.\xcb\xc8l\xd5?\x8eFv]\xad-\xe1P\xf5\xb4w\xe0\x89\xfc\xaa\x1bu\xccdo\x88\xf6\xd3\xc6\xb1\x9b=9\x11\xf1_\xf4)\x86k\ts\x94\xae\xa6\xde\xafn\xe3\xe9O^\x06\n\x19\xd4\\p[5\xd7\xdb\xa9\r\x1cz\x1e*\xdc\x80\xfb40\x9f\xbdW\x9a\xe2\xb2\xa8\x1d#@\xbe\xf0K\x8f}\xceQ\x0e,6:A\x91\xc9\xa17\x03>\xb6\x83T\xfft\x85\x92S\x8b\x13\xcfxHL\x9e\xda\x1fX\x14Y\x9cD\xab\xf9\xd6J\x12Cj\xdf\xb0q\x84\xe4\xea'
    _notches = b'!'


class ByteV(_ByteRotorBase):
    _name = 'Byte Rotor V'
    _short = 'byte5'
    _wiring = b'\xd6\x1d\xe9\xe2\xf5t<\x98\xc8\x9bw \xda\x86\xf8%\x8b\xc9\xe5"\x180d\xd9\xa4\x9e\xa2.&\xb6\xdd\x979{\x10l\x13\xaf\xc2Gq\xa1\xb1\x7f:\x88\x8a5\nM\x92\x83\xab?s\x95@\x8ei\xcd\x03\xc4\x8c\xfeo\xcb\x96\xf4\x8f\x02fb\x05#\xa5\x1f+\\\xd8\xb5u\x94I\xc0\x84e\x1a8\xd5\x802\xf2[\xf9\x8d\xc6\xeay\xf6\xd7\xbe_\x1b\xad\xfaW\xb3\x89H/\x9fO\xa3\xde\x90r\xe0\x1c\x15\xd1\xe4\xb4=Q\x19P\xbc-\xdc\x00\x85}]\xa8\x16^\x04K\x91\xe7\xf7\xa7\x93\xb2C\x0e\x82\xffa\xfd\x9aS\xd2E\xb8v\xb7\x0b\x12\xac\xe1\x07Y\x14RN\xf3\xeex\x01\xbb\x08\xcc\x0f\t\'\xdb\x87\r\xf0,\xb07V\x1e>\xbdFJ$!\x17;~\xc5\xaa\xa9z\xec\xbf\xed\xe8g\xcaL\xce\xa6\x9c\xc7\xb96`m\xd3(\x99\xef\x9d\xeb3kAXn\xdfh1\xe6cTB\xc1|\xcf\xfb\xa0\xc3\xba*\xd4\xd0\x81\x06\xe3\x0cDZjp)\xfc\xf1\x11U4\xae'
    _notches = b'\xf2'


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


# # # BYTE-COMPATIBLE REFLECTORS # # #
class ByteReflectorA(_ByteReflectorBase):
    _name = 'Byte Reflector - A'
    _short = 'byteref-a'
    _wiring = b'\xf8w\xfdEgR\xce\xb4C\\D\xba\xecN\xf2\xb0\xd2=r\x8d(,\xf70\xe1u\xa1+F\xc0\x86h\x8f\x85\x9a\xac\xe5UJ\xe2\x14\xde`\x1b\x15[\xd4m\x17\xdd\xb8\x81\xbbd\xd6;\xb2b\xd77\xae\x11\xb9K\xc4yl\x08\n\x03\x1c\xa7\x9fq&?t\xd0\r\xf3\xea\x7f\x05\xe6\x92%f\xdb\xe8\x90\xee-\t\x93\xa5\xa0*\xa49\xbd5}V\x04\x1f\xc9\xa3\x95B/\xf1\xcb\xf9I\x12\x82L\x19\xfb\x01\xe3A\xe4\xff\xc6e\x8aQ\xbe3s\xc7\xa2!\x1e\x94\xfe\xe9~\x9b\xaf\x13\xdf Y\x98T]\x87k\xb1\xe7\x91\xf4"\x8b\xa9\xca\xabH_\x1a\x84ja^\xadG\xb6\x9c\xc3\x9e#\xa6<\x8c\x0f\x968\xbf\x07\xd1\xa8\xe02>\x0b4\xdac\x80\xb3\x1d\xeb\xef\xaa@\xfc|\x83\xf5i\x9do\xf6\xd9\x06\xedM\xb5\x10\xf0.\xfa6:\xdc\xcd\xbcW\xd81)\x8e\xb7\x18\'xz$S\x97X\x89P\xc1\x0c\xcfZ\xc2\xd3n\x0eO\x99\xc8\xcc\x16\x00p\xd5v\xc5\x02\x88{'


class ByteReflectorB(_ByteReflectorBase):
    _name = 'Byte Reflector - B'
    _short = 'byteref-b'
    _wiring = b'!\x90m\xde\x88n\xdda\xd2\xb7q\x10\x87*i9\x0bR\x15\x81X\x12W?J\xffw/\xe5-\xe0\xfd\xfc\x00Y\xb5DNgT\x8f{\r\xfe\xcc\x1d\xa5\x1b\xbe\xf3\xab=|\x95\xa1\xb0l\x0f\xb4\xc0\x843I\x17\xf4\xea[\\$\xc5\x97\xa6\xc7>\x18\xa0\xb8f%z]t\x11\xa2\'du\x16\x14"pBCP\xef\xba\xe1\x07\xf2\xd0U\xd4M&\xb6\x0ex\xf08\x02\x05\xf5Z\n\x9e\x93QV\x9a\x1aj\xf8O)4\xdf\x9b\xda\xc6\x13\x96\xc8<\xdc\xad\x0c\x04\x9c\x8e\xd8\x99\xdb\x8a(\x01\xaa\xcfs\xc35\x82F\xed\x8cv~\x89\xe3r\xf1K6S\xa9\xbd.G\xe8\xd3\xa3\x912\xb2\x86\xc2\xd77\xf6\xac\xe4:#h\tL\xd1_\xe9\xc1\xa40\xe6;\xbc\xae\x94\xf7E\x80H\x83\xeb\xcb\xca,\xf9\xee\x92c\xb9\x08\xa8e\xd9\xfb\xaf\x8b\xd5\x7f\x8d\x85\x06\x03}\x1e`\xe7\x9d\xb3\x1c\xbf\xe2\xa7\xbbA\xc9\xfa\x98\xce^k\x9fb1@o\xb1\xc4y\xcd\xec\xd6 \x1f+\x19'


class ByteReflectorC(_ByteReflectorBase):
    _name = 'Byte Reflector - C'
    _short = 'byteref-c'
    _wiring = b'\xa6\xf3\xe9\x8f2\x83\x9e5\x89l\xbb\xfb%~^\x9f0\x1e\xd0\x8a\xfa}\xc7sT/46\xb2\x8d\x11\xe1\xf0-\xe2,&\x0c$v\xe4\xa0m\xad#!\xda\x19\x10y\x04\xba\x1a\x07\x1b87\xc9\x94\xbdd\xff\xcd\xec\xdd\xd7Xag\xcf\xcec\xc0r\xea\x87\xa5\xdc\xd1\xb8\xb7_ej\x18\xd4\xc1|B\xe8u\x97\xfe\xca\x0eQ\xb4C\x80G<R\xbcD\xe5\xb3S\xc4\t*\xf2q\xb1oI\x17wZ\'t\x851\xe7\xccW\x15\r\xd3b\xa9\xc5\x05\x8ex\xf5K\x8c\x08\x13\x9c\x88\x1d\x84\x03\xa7\xf4\x95\xae:\x92\xe0[\xab\xde\xa2\xe6\x8b\xee\x06\x0f)\xbe\x9a\xf6\xf8L\x00\x90\xed\x81\xbf\x98\xeb+\x93\xd5\xc2p\x1ci`\xb9\xd9PO\xb53\nf;\xa1\xaaHV\xb0\xdfk\x82\xfc\x16\xf79]\xf1{>FE\x12N\xdb\x7fU\xaf\xfdA\xf9\xb6.\xd2M@\x99\xc3\x96\x1f"\xef(h\x9bzY\x02J\xac?\xa8\x9d\xe3 \xcbn\x01\x91\x86\xa3\xc8\xa4\xd8\x14\x0b\xc6\xd6\\='
