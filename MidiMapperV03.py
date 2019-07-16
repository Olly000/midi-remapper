#!/usr/bin/env python3

# import midi object library and set backend to pygame to allow access to midi ports.

import mido
import pygame.midi as pym
import tkinter as tk
from csv import reader
from sys import exit


mido.set_backend('mido.backends.pygame')

pym.init()


class Interface(tk.Frame):  # Creates a GUI frame for user interaction
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.in_port = self.select_port(mido.get_input_names(), 'input')
        self.out_port = self.select_port(mido.get_output_names(), 'output')
        self.map_file = self.select_map_file()
        self.channel = self.create_channel_field()
        self.create_buttons()

    def grab_inputs(self):
        labels = ['MIDI in', 'MIDI out', 'channel', 'map']
        data = [self.in_port.get('active'), self.out_port.get('active'),
                self.channel.get(), self.map_file.get()]
        print(data)
        return dict(zip(labels, data))

    def start_processor(self):
        process = MidiReMap(self.grab_inputs())
        process.direct_midi()

    @staticmethod
    def select_port(port_list, direction):
        label = tk.Label(text='Select MIDI ' + direction)
        opt_box = tk.Listbox(root, width=30, height=len(port_list), selectmode='single')
        label.grid(sticky='w')
        opt_box.grid()
        for port in port_list:
            opt_box.insert('end', port)
        return opt_box

    @staticmethod
    def select_map_file():  # this could open a file browser rather than just an entry widget
        label = tk.Label(text='Choose mapping file: ')
        file_choose = tk.Entry(width=30, )
        label.grid(column=0, row=5)
        file_choose.grid(column=1, row=5, padx=10, sticky='w')
        return file_choose

    @staticmethod
    def create_channel_field():
        label = tk.Label(text='MIDI output channel: ')
        channel = tk.Entry(width=2)
        label.grid(column=0, row=4, pady=10)
        channel.grid(column=1, row=4, padx=10, pady=10, sticky='w')
        return channel

    def create_buttons(self):
        option_set = tk.Button(root, text='Update Settings', command=self.start_processor)
        quit_button = tk.Button(root, text="Quit", bg="red", command=self.master.destroy)
        option_set.grid(column=0, padx=30, pady=30)
        quit_button.grid(column=1, padx=30, pady=30)


class MidiReMap:  # class containing methods for processing MIDI according to user input
    def __init__(self, inputs):
        self.in_port = mido.open_input(inputs['MIDI in'])
        self.out_port = mido.open_output(inputs['MIDI out'])
        self.channel = int(inputs['channel']) - 1
        self.map = self.handle_map_file(inputs['map'])

    def direct_midi(self):  # listens for MIDI input or key interruption
        while True:
            try:
                self.port_listen()
            except KeyboardInterrupt:
                print('Terminated by User')
                exit(0)

    @staticmethod
    def handle_map_file(file_name):  # asks user for cc map and creates a dictionary based on it
        mappings = {}
        with open(file_name, 'r') as csvfile:
            for orig, new in reader(csvfile, delimiter=','):
                mappings[orig] = new
        return mappings

    def port_listen(self):  # takes message from input port and sends it to out after processing
        for msg in self.in_port:
            if 'channel' in str(msg):
                print(msg)
                msg = self.check_cc(msg.copy(channel=self.channel))
            self.out_port.send(msg)

    def check_cc(self, msg):  # checks MIDI input - sends to transform if cc or output if not.
        msg = msg.bytes()
        if msg[0] == (176 + self.channel):
            return mido.Message.from_bytes(self.transform_bit(msg))
        else:
            return mido.Message.from_bytes(msg)

    def transform_bit(self, msg):  # transforms cc number and returns msg to be output
        bit = str(msg[1])
        if bit in dict.keys(self.map):
            msg[1] = int(self.map[bit])
            return msg
        else:
            return msg


if __name__ == '__main__':

    root = tk.Tk()
    app = Interface(master=root)
    app.master.title("MIDI ReMapper")
    app.mainloop()
