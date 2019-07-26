#!/usr/bin/env python3

# import midi object library and set backend to pygame to allow access to midi ports.

import mido
import pygame.midi as pym
import tkinter as tk
import threading
from csv import reader
from sys import exit


mido.set_backend('mido.backends.pygame')

pym.init()

run_state = False


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

    def end_app(self):
        global run_state
        run_state = False
        self.master.destroy()
        print('App terminated by user')

    def pause_loop(self):
        global run_state
        run_state = False
        self.option_set.config(state='normal')
        print(run_state)

    def start_processor(self):
        global run_state
        run_state = True
        process = MidiReMap(self.grab_inputs())
        self.option_set.config(state='disabled')
        new_process_thread = threading.Thread(target=process.direct_midi)
        new_process_thread.start()
        print('new thread')

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
        self.option_set = tk.Button(root, text='Start', command=self.start_processor)
        pause = tk.Button(root, text='Pause', command=self.pause_loop)
        quit_button = tk.Button(root, text="Quit", bg="red", command=self.end_app)
        self.option_set.grid(column=0, padx=30, pady=30)
        pause.grid(column=1, padx=30, pady=10)
        quit_button.grid(column=1, padx=30, pady=30)


class MidiReMap:  # class containing methods for processing MIDI according to user input
    def __init__(self, inputs):
        self.inputs = inputs
        self.in_port = mido.open_input(self.inputs['MIDI in'])
        self.out_port = mido.open_output(self.inputs['MIDI out'])
        self.channel = int(self.inputs['channel']) - 1
        self.map = self.handle_map_file(self.inputs['map'])

    def open_out_port(self):
        return mido.open_output(self.inputs['MIDI out'])

    @staticmethod
    def handle_map_file(file_name):  # asks user for cc map and creates a dictionary based on it
        mappings = {}
        with open(file_name, 'r') as csvfile:
            for orig, new in reader(csvfile, delimiter=','):
                mappings[orig] = new
        return mappings

    def handle_cc(self, msg):
        if 'channel' in str(msg):
            print(msg)
            msg = self.check_cc(msg.copy(channel=self.channel))
        self.out_port.send(msg)

    def direct_midi(self):  # listens for MIDI input or key interruption
        global run_state
        if run_state:
            print('while loop started')
            for msg in self.in_port:
                print('msg loop started')
                if run_state:
                    self.handle_cc(msg)
                else:
                    print('msg loop exited')
                    break
        else:
            print('loop exited end d_m')
            return

    def port_listen(self):  # takes message from input port and sends it to out after processing
        global run_state
        while run_state:
            for msg in self.in_port:
                if run_state:
                    self.handle_cc(msg)
                else:
                    print('loop exited')
                    break

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
