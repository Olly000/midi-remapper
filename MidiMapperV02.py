#!/usr/bin/env python3

# import midi object library and set backend to pygame to allow access to midi ports.

import mido
import pygame.midi as pym
from csv import reader
from sys import exit


mido.set_backend('mido.backends.pygame')

pym.init()


class InputParam:  # accesses and stores the port, channel and map file to be used
    def __init__(self):
        self.map = self.get_map_file()
        self.port = self.get_port()
        self.channel = self.get_channel()

    @staticmethod
    def get_map_file():  # asks user for cc map and creates a dictionary based on it
        file_name = input('Which file should MidiMapper use to remap cc numbers?: ')
        mappings = {}
        with open(file_name, 'r') as csvfile:
            for orig, new in reader(csvfile, delimiter=','):
                mappings[orig] = new
        return mappings

    @staticmethod
    def get_port():  # informs user of available ports and returns their choice
        port_list = mido.get_input_names()
        print('Available MIDI ports are \n')
        for name in range(0, len(port_list)):
            print('%s' % name, port_list[name])
        return port_list[int(input('\n Choose port by number: '))]

    @staticmethod
    def get_channel():  # returns users choice of MIDI channels to output on
        return int(input('Which MIDI Channel do you want to output to?: ')) - 1


class MidiReMap:  # class containing methods for processing MIDI according to user input
    def __init__(self):
        self.inputs = InputParam()
        self.port = self.open_port()

    def direct_midi(self):  # listens for MIDI input or key interruption
        while True:
            try:
                self.port_listen()
            except KeyboardInterrupt:
                print('Terminated by User')
                exit(0)

    def open_port(self):  # opens the input/output port selected by user
        print('Port in use is %s, channel' % self.inputs.port, (self.inputs.channel + 1))
        return mido.open_ioport(self.inputs.port)

    def port_listen(self):  # takes message from input port and sends it to out after processing
        for msg in self.port:
            if 'channel' in str(msg):
                print(msg)
                msg = self.check_cc(msg.copy(channel=self.inputs.channel))
            self.port.send(msg)

    def check_cc(self, msg):  # checks MIDI input - sends to transform if cc or output if not.
        msg = msg.bytes()
        if msg[0] == (176 + self.inputs.channel):
            return mido.Message.from_bytes(self.transform_bit(msg))
        else:
            return mido.Message.from_bytes(msg)

    def transform_bit(self, msg):  # transforms cc number and returns msg to be output
        bit = str(msg[1])
        if bit in dict.keys(self.inputs.map):
            msg[1] = int(self.inputs.map[bit])
            return msg
        else:
            return msg


def lets_remap():  # creates an input object and runs the direct_midi looper
    remap = MidiReMap()
    remap.direct_midi()


if __name__ == '__main__':
    lets_remap()







