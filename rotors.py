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


# # # Enigma I # # #
# German Army and Air Force (Wehrmacht, Luftwaffe)
class I_I(_RotorBase):
    _name = 'Enigma I - Rotor I'
    _short = '11'
    _wiring = 'EKMFLGDQVZNTOWYHXUSPAIBRCJ'
    _notches = 'Y'


class I_II(_RotorBase):
    _name = 'Enigma I - Rotor II'
    _short = '12'
    _wiring = 'AJDKSIRUXBLHWTMCQGZNPYFVOE'
    _notches = 'M'


class I_III(_RotorBase):
    _name = 'Enigma I - Rotor III'
    _short = '13'
    _wiring = 'BDFHJLCPRTXVZNYEIWGAKMUSQO'
    _notches = 'D'


class I_IV(_RotorBase):
    _name = 'Enigma I - Rotor IV'
    _short = '14'
    _wiring = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    _notches = 'R'


class I_V(_RotorBase):
    _name = 'Enigma I - Rotor V'
    _short = '15'
    _wiring = 'VZBRGITYUPSDNHLXAWMJQOFECK'
    _notches = 'H'


class I_UKW_A(_ReflectorBase):
    _name = 'Enigma I - Reflector A'
    _short = '1a'
    _wiring = 'EJMZALYXVBWFCRQUONTSPIKHGD'


class I_UKW_B(_ReflectorBase):
    _name = 'Enigma I - Reflector B'
    _short = '1b'
    _wiring = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'


class I_UKW_C(_ReflectorBase):
    _name = 'Enigma I - Reflector C'
    _short = '1c'
    _wiring = 'FVPJIAOYEDRZXWGCTKUQSBNMHL'


# # # Norway Enigma # # #
# Postwar Usage
class Norway_I(_RotorBase):
    _name = 'Norway Enigma - Rotor I'
    _short = 'norway1'
    _wiring = 'WTOKASUYVRBXJHQCPZEFMDINLG'
    _notches = 'Y'


class Norway_II(_RotorBase):
    _name = 'Norway Enigma - Rotor II'
    _short = 'norway2'
    _wiring = 'GJLPUBSWEMCTQVHXAOFZDRKYNI'
    _notches = 'M'


class Norway_III(_RotorBase):
    _name = 'Norway Enigma - Rotor III'
    _short = 'norway3'
    _wiring = 'JWFMHNBPUSDYTIXVZGRQLAOEKC'
    _notches = 'D'


class Norway_IV(_RotorBase):
    _name = 'Norway Enigma - Rotor IV'
    _short = 'norway4'
    _wiring = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    _notches = 'R'


class Norway_V(_RotorBase):
    _name = 'Norway Enigma - Rotor V'
    _short = 'norway5'
    _wiring = 'HEJXQOTZBVFDASCILWPGYNMURK'
    _notches = 'H'


class Norway_UKW(_ReflectorBase):
    _name = 'Norway Enigma - Reflector'
    _short = 'norway'
    _wiring = 'MOWJYPUXNDSRAIBFVLKZGQCHET'


# # # Enigma M3 # # #
# German Navy (Kriegsmarine)
class M3_I(_RotorBase):
    _name = 'Enigma M3 - Rotor I'
    _short = 'm31'
    _wiring = 'EKMFLGDQVZNTOWYHXUSPAIBRCJ'
    _notches = 'Y'


class M3_II(_RotorBase):
    _name = 'Enigma M3 - Rotor II'
    _short = 'm32'
    _wiring = 'AJDKSIRUXBLHWTMCQGZNPYFVOE'
    _notches = 'M'


class M3_III(_RotorBase):
    _name = 'Enigma M3 - Rotor III'
    _short = 'm33'
    _wiring = 'BDFHJLCPRTXVZNYEIWGAKMUSQO'
    _notches = 'D'


class M3_IV(_RotorBase):
    _name = 'Enigma M3 - Rotor IV'
    _short = 'm34'
    _wiring = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    _notches = 'R'


class M3_V(_RotorBase):
    _name = 'Enigma M3 - Rotor V'
    _short = 'm35'
    _wiring = 'VZBRGITYUPSDNHLXAWMJQOFECK'
    _notches = 'H'


class M3_VI(_RotorBase):
    _name = 'Enigma M3 - Rotor VI'
    _short = 'm36'
    _wiring = 'JPGVOUMFYQBENHZRDKASXLICTW'
    _notches = 'HU'


class M3_VII(_RotorBase):
    _name = 'Enigma M3 - Rotor VII'
    _short = 'm37'
    _wiring = 'NZJHGRCXMYSWBOUFAIVLPEKQDT'
    _notches = 'HU'


class M3_VIII(_RotorBase):
    _name = 'Enigma M3 - Rotor VIII'
    _short = 'm38'
    _wiring = 'FKQHTLXOCBJSPDZRAMEWNIUYGV'
    _notches = 'HU'


class M3_UKW_B(_ReflectorBase):
    _name = 'Enigma M3 - Reflector B'
    _short = 'm3b'
    _wiring = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'


class M3_UKW_C(_ReflectorBase):
    _name = 'Enigma M3 - Reflector C'
    _short = 'm3c'
    _wiring = 'FVPJIAOYEDRZXWGCTKUQSBNMHL'


# # # Enigma M4 # # #
# U-Boot Enigma
class M4_I(_RotorBase):
    _name = 'Enigma M4 - Rotor I'
    _short = 'm41'
    _wiring = 'EKMFLGDQVZNTOWYHXUSPAIBRCJ'
    _notches = 'Y'


class M4_II(_RotorBase):
    _name = 'Enigma M4 - Rotor II'
    _short = 'm42'
    _wiring = 'AJDKSIRUXBLHWTMCQGZNPYFVOE'
    _notches = 'M'


class M4_III(_RotorBase):
    _name = 'Enigma M4 - Rotor III'
    _short = 'm43'
    _wiring = 'BDFHJLCPRTXVZNYEIWGAKMUSQO'
    _notches = 'D'


class M4_IV(_RotorBase):
    _name = 'Enigma M4 - Rotor IV'
    _short = 'm44'
    _wiring = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    _notches = 'R'


class M4_V(_RotorBase):
    _name = 'Enigma M4 - Rotor V'
    _short = 'm45'
    _wiring = 'VZBRGITYUPSDNHLXAWMJQOFECK'
    _notches = 'H'


class M4_VI(_RotorBase):
    _name = 'Enigma M4 - Rotor VI'
    _short = 'm46'
    _wiring = 'JPGVOUMFYQBENHZRDKASXLICTW'
    _notches = 'HU'


class M4_VII(_RotorBase):
    _name = 'Enigma M4 - Rotor VII'
    _short = 'm47'
    _wiring = 'NZJHGRCXMYSWBOUFAIVLPEKQDT'
    _notches = 'HU'


class M4_VIII(_RotorBase):
    _name = 'Enigma M4 - Rotor VIII'
    _short = 'm48'
    _wiring = 'FKQHTLXOCBJSPDZRAMEWNIUYGV'
    _notches = 'HU'


class M4_Beta(_RotorBase):
    _name = 'Enigma M4 - Rotor Beta (β)'
    _short = 'm4beta'
    _wiring = 'LEYJVCNIXWPBQMDRTAKZGFUHOS'
    _notches = ''

    def step(self):
        """This rotor does not step."""
        return False


class M4_Gamma(_RotorBase):
    _name = 'Enigma M4 - Rotor Gamma (γ)'
    _short = 'm4gamma'
    _wiring = 'FSOKANUERHMBTIYCWLQPZXVGJD'
    _notches = ''

    def step(self):
        """This rotor does not step."""
        return False


class M4_UKW_BThin(_ReflectorBase):
    _name = 'Enigma M4 - Reflector B Thin'
    _short = 'm4bthin'
    _wiring = 'ENKQAUYWJICOPBLMDXZVFTHRGS'


class M4_UKW_CThin(_ReflectorBase):
    _name = 'Enigma M4 - Reflector C Thin'
    _short = 'm4cthin'
    _wiring = 'RDOBJNTKVEHMLFCWZAXGYIPSUQ'


# # # Enigma G # # #
# Zählwerk Enigma A28 and G31
class G_I(_RotorBase):
    _name = 'Enigma G - Rotor I'
    _short = 'g1'
    _wiring = 'LPGSZMHAEOQKVXRFYBUTNICJDW'
    _notches = 'ACDEHIJKMNOQSTWXY'


class G_II(_RotorBase):
    _name = 'Enigma G - Rotor II'
    _short = 'g2'
    _wiring = 'SLVGBTFXJQOHEWIRZYAMKPCNDU'
    _notches = 'ABDGHIKLNOPSUVY'


class G_III(_RotorBase):
    _name = 'Enigma G - Rotor III'
    _short = 'g3'
    _wiring = 'CJGDPSHKTURAWZXFMYNQOBVLIE'
    _notches = 'CEFIMNPSUVZ'


class G_UKW(_ReflectorBase):
    _name = 'Enigma G - Reflector'
    _short = 'g'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma G-312 # # #
# G31 Abwehr Enigma
class G312_I(_RotorBase):
    _name = 'Enigma G312 - Rotor I'
    _short = 'g3121'
    _wiring = 'DMTWSILRUYQNKFEJCAZBPGXOHV'
    _notches = 'ACDEHIJKMNOQSTWXY'


class G312_II(_RotorBase):
    _name = 'Enigma G312 - Rotor II'
    _short = 'g3122'
    _wiring = 'HQZGPJTMOBLNCIFDYAWVEUSRKX'
    _notches = 'ABDGHIKLNOPSUVY'


class G312_III(_RotorBase):
    _name = 'Enigma G312 - Rotor III'
    _short = 'g3123'
    _wiring = 'UQNTLSZFMREHDPXKIBVYGJCWOA'
    _notches = 'CEFIMNPSUVZ'


class G312_UKW(_ReflectorBase):
    _name = 'Enigma G312 - Reflector'
    _short = 'g312'
    _wiring = 'RULQMZJSYGOCETKWDAHNBXPVIF'


# # # Enigma G-260 # # #
# G31 Abwehr Enigma
class G260_I(_RotorBase):
    _name = 'Enigma G260 - Rotor I'
    _short = 'g2601'
    _wiring = 'RCSPBLKQAUMHWYTIFZVGOJNEXD'
    _notches = 'ACDEHIJKMNOQSTWXY'


class G260_II(_RotorBase):
    _name = 'Enigma G260 - Rotor II'
    _short = 'g2602'
    _wiring = 'WCMIBVPJXAROSGNDLZKEYHUFQT'
    _notches = 'ABDGHIKLNOPSUVY'


class G260_III(_RotorBase):
    _name = 'Enigma G260 - Rotor III'
    _short = 'g2603'
    _wiring = 'FVDHZELSQMAXOKYIWPGCBUJTNR'
    _notches = 'CEFIMNPSUVZ'


class G260_UKW(_ReflectorBase):
    _name = 'Enigma G260 - Reflector'
    _short = 'g260'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma G-111 # # #
# G31 Hungarian Enigma
class G111_I(_RotorBase):
    _name = 'Enigma G111 - Rotor I'
    _short = 'g1111'
    _wiring = 'WLRHBQUNDKJCZSEXOTMAGYFPVI'
    _notches = 'ACDEHIJKMNOQSTWXY'


class G111_II(_RotorBase):
    _name = 'Enigma G111 - Rotor II'
    _short = 'g1112'
    _wiring = 'TFJQAZWMHLCUIXRDYGOEVBNSKP'
    _notches = 'ABDGHIKLNOPSUVY'


class G111_V(_RotorBase):
    _name = 'Enigma G111 - Rotor V'
    _short = 'g1115'
    _wiring = 'QTPIXWVDFRMUSLJOHCANEZKYBG'
    _notches = 'AEHNPUY'


class G111_UKW(_ReflectorBase):
    _name = 'Enigma G111 - Reflector'
    _short = 'g111'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma D # # #
# Commercial Enigma A26
class D_I(_RotorBase):
    _name = 'Enigma D - Rotor I'
    _short = 'd1'
    _wiring = 'LPGSZMHAEOQKVXRFYBUTNICJDW'
    _notches = 'G'


class D_II(_RotorBase):
    _name = 'Enigma D - Rotor II'
    _short = 'd2'
    _wiring = 'SLVGBTFXJQOHEWIRZYAMKPCNDU'
    _notches = 'M'


class D_III(_RotorBase):
    _name = 'Enigma D - Rotor III'
    _short = 'd3'
    _wiring = 'CJGDPSHKTURAWZXFMYNQOBVLIE'
    _notches = 'V'


class D_UKW(_ReflectorBase):
    _name = 'Enigma D - Reflector'
    _short = 'd'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma K # # #
# Commercial Enigma A27
class K_I(_RotorBase):
    _name = 'Enigma K - Rotor I'
    _short = 'k1'
    _wiring = 'LPGSZMHAEOQKVXRFYBUTNICJDW'
    _notches = 'G'


class K_II(_RotorBase):
    _name = 'Enigma K - Rotor II'
    _short = 'k2'
    _wiring = 'SLVGBTFXJQOHEWIRZYAMKPCNDU'
    _notches = 'M'


class K_III(_RotorBase):
    _name = 'Enigma K - Rotor III'
    _short = 'k3'
    _wiring = 'CJGDPSHKTURAWZXFMYNQOBVLIE'
    _notches = 'V'


class K_UKW(_ReflectorBase):
    _name = 'Enigma K - Reflector'
    _short = 'k'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma Swiss-K # # #
# Swiss Enigma K variant (Swiss Air Force)
class SwissK_I(_RotorBase):
    _name = 'Swiss Enigma K - Rotor I'
    _short = 'swissk1'
    _wiring = 'PEZUOHXSCVFMTBGLRINQJWAYDK'
    _notches = 'G'


class SwissK_II(_RotorBase):
    _name = 'Swiss Enigma K - Rotor II'
    _short = 'swissk2'
    _wiring = 'ZOUESYDKFWPCIQXHMVBLGNJRAT'
    _notches = 'M'


class SwissK_III(_RotorBase):
    _name = 'Swiss Enigma K - Rotor III'
    _short = 'swissk3'
    _wiring = 'EHRVXGAOBQUSIMZFLYNWKTPDJC'
    _notches = 'V'


class SwissK_UKW(_ReflectorBase):
    _name = 'Swiss Enigma K - Reflector'
    _short = 'swissk'
    _wiring = 'IMETCGFRAYSQBZXWLHKDVUPOJN'


# # # Enigma KD # # #
# Enigma K with UKW-D
class KD_I(_RotorBase):
    _name = 'Enigma KD - Rotor I'
    _short = 'kd1'
    _wiring = 'VEZIOJCXKYDUNTWAPLQGBHSFMR'
    _notches = 'ACGIMPTVY'


class KD_II(_RotorBase):
    _name = 'Enigma KD - Rotor II'
    _short = 'kd2'
    _wiring = 'HGRBSJZETDLVPMQYCXAOKINFUW'
    _notches = 'ACGIMPTVY'


class KD_III(_RotorBase):
    _name = 'Enigma KD - Rotor III'
    _short = 'kd3'
    _wiring = 'NWLHXGRBYOJSAZDVTPKFQMEUIC'
    _notches = 'ACGIMPTVY'


class KD_UKW(_ReflectorBase):
    """TECHINCALLY, this reflector is rewritable... but meh"""
    _name = 'Enigma KD - Reflector'
    _short = 'kd'
    _wiring = 'NSUOMKLIHZFGEADVXWBYCPRQTJ'


# # # Railway Enigma # # #
# Modified Enigma K for German Railway (Reichsbahn)
class Rail_I(_RotorBase):
    _name = 'Railway Enigma - Rotor I'
    _short = 'rail1'
    _wiring = 'JGDQOXUSCAMIFRVTPNEWKBLZYH'
    _notches = 'V'


class Rail_II(_RotorBase):
    _name = 'Railway Enigma - Rotor II'
    _short = 'rail2'
    _wiring = 'NTZPSFBOKMWRCJDIVLAEYUXHGQ'
    _notches = 'M'


class Rail_III(_RotorBase):
    _name = 'Railway Enigma - Rotor III'
    _short = 'rail3'
    _wiring = 'JVIUBHTCDYAKEQZPOSGXNRMWFL'
    _notches = 'G'


class Rail_UKW(_ReflectorBase):
    _name = 'Railway Enigma - Reflector'
    _short = 'rail'
    _wiring = 'QYHOGNECVPUZTFDJAXWMKISRBL'


# # # Enigma T # # #
# Japanese Enigma (Tirpitz)
class T_I(_RotorBase):
    _name = 'Enigma T - Rotor I'
    _short = 't1'
    _wiring = 'KPTYUELOCVGRFQDANJMBSWHZXI'
    _notches = 'EHMSY'


class T_II(_RotorBase):
    _name = 'Enigma T - Rotor II'
    _short = 't2'
    _wiring = 'UPHZLWEQMTDJXCAKSOIGVBYFNR'
    _notches = 'EHNTZ'


class T_III(_RotorBase):
    _name = 'Enigma T - Rotor III'
    _short = 't3'
    _wiring = 'QUDLYRFEKONVZAXWHMGPJBSICT'
    _notches = 'EHMSY'


class T_IV(_RotorBase):
    _name = 'Enigma T - Rotor IV'
    _short = 't4'
    _wiring = 'CIWTBKXNRESPFLYDAGVHQUOJZM'
    _notches = 'EHNTZ'


class T_V(_RotorBase):
    _name = 'Enigma T - Rotor V'
    _short = 't5'
    _wiring = 'UAXGISNJBVERDYLFZWTPCKOHMQ'
    _notches = 'GKNSZ'


class T_VI(_RotorBase):
    _name = 'Enigma T - Rotor VI'
    _short = 't6'
    _wiring = 'XFUZGALVHCNYSEWQTDMRBKPIOJ'
    _notches = 'FMQUY'


class T_VII(_RotorBase):
    _name = 'Enigma T - Rotor VII'
    _short = 't7'
    _wiring = 'BJVFTXPLNAYOZIKWGDQERUCHSM'
    _notches = 'GKNSZ'


class T_VIII(_RotorBase):
    _name = 'Enigma T - Rotor VIII'
    _short = 't8'
    _wiring = 'YMTPNZHWKODAJXELUQVGCBISFR'
    _notches = 'FMQUY'


class T_UKW(_ReflectorBase):
    _name = 'Enigma T - Reflector'
    _short = 't'
    _wiring = 'GEKPBTAUMOCNILJDXZYFHWVQSR'


def main():
    # Test the Reflector wirings
    ref_classes = _ReflectorBase.__subclasses__()
    for cl in sorted(ref_classes, key=lambda x: x._name):
        print('Testing', cl._name, '...')
        w = cl._wiring
        for i in range(len(w)):
            x = i
            y = cl._abet.index(w[x])
            z = cl._abet.index(w[y])
            if x != z:
                print(cl._name, 'FAILED')
                break


if __name__ == '__main__': main()
