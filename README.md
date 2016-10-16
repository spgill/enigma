<img src="https://raw.githubusercontent.com/spgill/enigma/master/icon.png" height="256">
Enigma Machine
===
Simple simulation of classic enigma machine encryption mechanics, written in Python.
Supports a wide array of historical rotor and reflector wirings.

Technical Details
---
* Developed and tested on Python 3.5.2 for Windows.
    * support for other versions and operating systems is likely, but not guaranteed.
* Designed to be run as a module, but can be initiated from the ```__main__.py``` script.
* Can be imported and used in your own applications, but no documentation is provided yet (though it shouldn't be too hard to figure out).

Downloading
---
This package can be downloaded and installed
directly from the repo using:

```pip install git+git://github.com/spgill/enigma```


Usage
---
```
usage: enigma [-h] [--plugboard PLUGBOARD [PLUGBOARD ...]]
              [--rotors ROTORS [ROTORS ...]] [--reflector REFLECTOR]
              [--state STATE] [--state-create] [--state-update]
              [--state-print] [--state-seed STATE_SEED] [--input INPUT]
              [--input-std] [--input-path INPUT_PATH] [--input-bz2]
              [--output-std] [--output-path OUTPUT_PATH] [--output-bz2]
              [--mode {classic,modern,byte}] [--chunk-size CHUNK_SIZE]
              [--benchmark] [--no-progress] [--verbose] [--typewriter]

Process some data through a simulated Enigma machine

optional arguments:
  -h, --help            show this help message and exit
  --plugboard PLUGBOARD [PLUGBOARD ...], -p PLUGBOARD [PLUGBOARD ...]
                        Specify a list of character pairings for the
                        plugboard. ex; AB CF HJ
  --rotors ROTORS [ROTORS ...], -ro ROTORS [ROTORS ...]
                        Specify a list of rotors in the following format:
                        SHORTNAME[:SETTING[:NOTCHES]] ex; com1:C:QV
  --reflector REFLECTOR, -rf REFLECTOR
  --state STATE, -s STATE
                        Path for the state file (loading or creating). Can be
                        used in lieu of manually specifying rotors and
                        reflectors.
  --state-create, -sc   Take the rotor and reflector args and save it to the
                        state file.
  --state-update, -su   After processing, save the changed rotor state back to
                        the state file. This allows for a continuous rotor
                        progression over multiple script invocations. THERE IS
                        NO ROLLBACK, SO BACK IT UP.
  --state-print, -sp    Print the state information to stdout and exit.
  --state-seed STATE_SEED, -ss STATE_SEED
                        String seed for a randomly generated state.
  --input INPUT, -i INPUT
                        Input a string via this command line argument.
  --input-std, -is      Read data from stdin pipe.
  --input-path INPUT_PATH, -ip INPUT_PATH
                        Open and read data from file path.
  --input-bz2, -iz      Run input through BZ2 decompression before processing.
  --output-std, -os     Write output to the stdout pipe.
  --output-path OUTPUT_PATH, -op OUTPUT_PATH
                        Write output to the specified file path.
  --output-bz2, -oz     Run output through BZ2 compression before writing.
  --mode {classic,modern,byte}, -m {classic,modern,byte}
                        Which mode the enigma machine will operate in.
                        (default: classic) Classic mode will only process
                        characters A through Z, will capitalize lowercase
                        letters, and will remove invalid ones. Modern mode
                        will preserve case, and invalid characters will pass
                        through unchanged (without affecting rotors). Byte
                        mode will process any 8-bit character, but REQUIRES
                        that byte-compatible rotors and reflectors be passed
                        into the machine.
  --chunk-size CHUNK_SIZE, -c CHUNK_SIZE
                        Chunk size for reading and writing data.
  --benchmark, -b       Benchmark the processing time (prints results to
                        stderr).
  --no-progress, -np    Suppress the progress meter that is normal written to
                        stderr.
  --verbose, -v         Enable verbosity; printing LOTS of messages to stderr.
  --typewriter, -t      Enable typewriter mode. Press a key, and the
                        translated key is written to the console; similar to
                        an actual enigma machine. Not particularly useful,
                        just really cool to play with. (currently Windows
                        only)
```
