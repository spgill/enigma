# stdlib imports
import math
import time
import tkinter
import tkinter.ttk

# local module imports
import chassis
import machine
import rotors


class MachineGUI(tkinter.Tk):
    """A Tkinter window creating a graphical simulation of an Enigma Machine"""

    def __init__(self, *args, **kwargs):
        """Overwrite the builtin init method"""
        super().__init__(*args, **kwargs)

        # Let's get this party started
        chassis.init_tk()
        self._config()
        self._setup()
        self.mainloop()

    def _config(self):
        """Configure the properties and constants of the gui"""
        # window properties
        self.title('Enigma Machine GUI')

        # constants
        self.CANVAS_ROTOR_SIZE = 256
        self.CANVAS_ROTOR_RADI = self.CANVAS_ROTOR_SIZE / 2
        self.CANVAS_ROTOR_PAD = 8

    def _setup(self):
        """Setup all the GUI elements"""

        # Collect a list of rotor names
        self.rotors_classes = rotors._RotorBase.__subclasses__()
        self.rotors_names = ['']
        self.rotors_lookup = {}
        for rotor in self.rotors_classes:
            if rotor == rotors._ReflectorBase:
                continue
            self.rotors_names.append(rotor._name)
            self.rotors_lookup[rotor._name] = rotor._short
        self.rotors_names.sort()

        # Collect a list of reflector names
        self.reflector_classes = rotors._ReflectorBase.__subclasses__()
        self.reflector_names = ['']
        self.reflector_lookup = {}
        for reflector in self.reflector_classes:
            self.reflector_names.append(reflector._name)
            self.reflector_lookup[reflector._name] = reflector._short

        # Create all the selection boxes for the different rotors and such
        self.rotors_options = [
            tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()
        ]
        for var in self.rotors_options:
            var.set(self.rotors_names[1])
        for i in range(3):
            tkinter.ttk.OptionMenu(self, self.rotors_options[i], *self.rotors_names)\
                .grid(column=i, row=0)
        self.reflector_option = tkinter.StringVar()
        self.reflector_option.set(self.reflector_names[1])
        tkinter.ttk.OptionMenu(self, self.reflector_option, *self.reflector_names)\
            .grid(column=3, row=0)

        # Get the canvas ready to go
        self.canvas = tkinter.Canvas(
            self,
            width=(self.CANVAS_ROTOR_SIZE * 4),
            height=self.CANVAS_ROTOR_SIZE
        )
        self.canvas.grid(column=0, row=1, columnspan=4)
        self.canvas_redraw()

        # Add the entry widgets for input and output
        self.var_input = tkinter.StringVar()
        tkinter.ttk.Label(self, text='Input:')\
            .grid(column=0, row=2, sticky='E')
        self.entry_input = tkinter.ttk.Entry(self, textvariable=self.var_input)
        self.entry_input.grid(column=1, row=2, columnspan=2, sticky='WE')

        self.var_output = tkinter.StringVar()
        tkinter.ttk.Label(self, text='Output:')\
            .grid(column=0, row=3, sticky='E')
        tkinter.ttk.Entry(self, textvariable=self.var_output, state='readonly')\
            .grid(column=1, row=3, columnspan=2, sticky='WE')

        # oh, add a button too
        self.button_start = tkinter.ttk.Button(
            self,
            text='START',
            command=self.start
        )
        self.button_start.grid(column=3, row=2, rowspan=2, sticky='WESN')

        # Configure the grid
        for x in range(4):
            self.grid_columnconfigure(x, weight=1)

    def canvas_redraw(self):
        """Clear the canvas and draw the basic shapes"""
        self.canvas.delete('all')
        self.rotors = [
            {'inner': [], 'outer': []},
            {'inner': [], 'outer': []},
            {'inner': [], 'outer': []},
            {'inner': [], 'outer': []}
        ]

        # Loop for three rotors and a reflector
        for i in range(4):

            # Calculate a few useful coordinates
            topleft = (tlx, tly) = (
                self.CANVAS_ROTOR_SIZE * i,
                0
            )
            bottomright = (brx, bry) = (
                self.CANVAS_ROTOR_SIZE * (i + 1),
                self.CANVAS_ROTOR_SIZE
            )
            center = (centerx, centery) = (
                self.CANVAS_ROTOR_SIZE / 2 + self.CANVAS_ROTOR_SIZE * i,
                self.CANVAS_ROTOR_SIZE / 2
            )
            # self.canvas.create_oval(topleft, bottomright)

            # Loop through the alphabet
            for j in range(26):
                letter = rotors._RotorBase._abet[j]
                # Do some trig B)
                angle = (2.0 * math.pi) / 26 * j - math.pi / 2
                anglex = math.cos(angle)
                angley = math.sin(angle)

                # outer circle
                self.canvas.create_oval(
                    (tlx + 2, tly + 2),
                    (brx - 2, bry - 2)
                )

                # outer pips
                self.canvas.create_oval(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 6) - 3,
                        centery + angley * (self.CANVAS_ROTOR_RADI - 6) - 3
                    ),
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 6) + 3,
                        centery + angley * (self.CANVAS_ROTOR_RADI - 6) + 3
                    )
                )
                self.rotors[i]['outer'].append(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 6),
                        centery + angley * (self.CANVAS_ROTOR_RADI - 6)
                    )
                )

                # outer letters
                self.canvas.create_text(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 16),
                        centery + angley * (self.CANVAS_ROTOR_RADI - 16)
                    ),
                    text=letter
                )

                # middle circle
                self.canvas.create_oval(
                    (tlx + 24, tly + 24),
                    (brx - 24, bry - 24),
                    dash=[2, 2]
                )

                # inner letters
                self.canvas.create_text(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 32),
                        centery + angley * (self.CANVAS_ROTOR_RADI - 32)
                    ),
                    text=letter
                )

                # inner pips
                self.canvas.create_oval(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 42) - 3,
                        centery + angley * (self.CANVAS_ROTOR_RADI - 42) - 3
                    ),
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 42) + 3,
                        centery + angley * (self.CANVAS_ROTOR_RADI - 42) + 3
                    )
                )
                self.rotors[i]['inner'].append(
                    (
                        centerx + anglex * (self.CANVAS_ROTOR_RADI - 42),
                        centery + angley * (self.CANVAS_ROTOR_RADI - 42)
                    )
                )

                # inner circle
                self.canvas.create_oval(
                    (tlx + 46, tly + 46),
                    (brx - 46, bry - 46)
                )

    def start(self):
        """Start the ciphering process"""
        # disable input
        self.button_start['state'] = 'disabled'
        self.entry_input['state'] = 'disabled'
        self.var_output.set('')

        # resolve the rotors and reflector
        m_rotors = [self.rotors_lookup[o.get()] for o in self.rotors_options]
        m_reflector = self.reflector_lookup[self.reflector_option.get()]

        # initialize the machine
        m = machine.Machine(None, m_rotors, m_reflector)

        # slowly feed the data through
        traces = m.transcode(self.var_input.get(), trace=True)
        for trace in traces:
            wires = []
            print(
                'TRACE',
                rotors._RotorBase._abet[trace[0][0]],
                'to',
                trace[-1],
                trace[:-1]
                )

            for i, (pin_in, pin_out) in enumerate(trace[0:3]):
                # print(i, pin_in, pin_out)
                wires.append(self.rotors[i]['outer'][pin_in])
                wires.append(self.rotors[i]['inner'][pin_out])

            wires.append(self.rotors[3]['outer'][trace[3][0]])
            wires.append(self.rotors[3]['inner'][trace[3][1]])
            # print(trace[3][0], trace[3][1])

            for i, (pin_in, pin_out) in enumerate(trace[4:7]):
                # print(i, pin_in, pin_out)
                wires.append(self.rotors[2 - i]['inner'][pin_in])
                wires.append(self.rotors[2 - i]['outer'][pin_out])

            wires.append((0, self.CANVAS_ROTOR_SIZE))

            # print()
            self.var_output.set(self.var_output.get() + trace[-1])

            self.canvas_redraw()
            wire_last = (0, 0)
            for wire in wires:
                self.canvas.create_line(wire_last, wire, fill='#ff0000')
                wire_last = wire

            self.update()
            time.sleep(0.1)

        # re-enabled input
        self.button_start['state'] = 'normal'
        self.entry_input['state'] = 'normal'


def main():
    """Main method for the gui. Run this to initialize a new instance"""
    chassis.init()
    MachineGUI()
