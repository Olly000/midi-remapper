# midi-remapper
This script opens a port of user's choosing and remaps incoming control change messages to those supplied in a mapping file (file map.txt uploaded as an example)
Accepts input on any MIDI channel and outputs it to a channel of users choice (defined when script runs).
Makes use of the Mido library with pygame.midi as a backend.
