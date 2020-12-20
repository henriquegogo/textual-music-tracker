#!/usr/bin/env python

import sys
import time
import rtmidi

NOTE_ON = 0x90
NOTE_OFF = 0x80

midiout = None
info = {}

def send_message(message_type, note, velocity):
    midiout.send_message([message_type, note, velocity])
    print(message_type, note, velocity)


def process_track(track):
    bpm = int(info.get('bpm') or 120)
    octave = int(info.get('octave') or 4)

    for track_line in track:
        for note, velocity in enumerate(track_line):
            note = (octave + 1) * 12 + note

            if velocity.isdigit():
                message_type = NOTE_OFF if velocity == '0' else NOTE_ON
                velocity = int(127 / 9 * float(velocity))
                send_message(message_type, note, velocity)

        time.sleep(60 / bpm / 4)


def process_lines(lines):
    global info
    track = []

    for line in lines:
        key_value = line.split(':')

        if len(key_value) > 1 and key_value[1]:
            key, value = key_value
            info[key.lower()] = value.strip()

        elif '▏' not in line and '▁' not in line and '▔' not in line:
            track.append(line)

    process_track(track)


def show_usage_message():
    print('Usage: ./main.py FILENAME')


def open_file(filename):
    try:
        file = open(filename, 'r')
        lines = file.read().split('\n')

    except:
        print('Error reading file')

    process_lines(lines)


def initialize_midi():
    global midiout
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port('Textual Music Tracker')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        initialize_midi()
        open_file(sys.argv[1])

    else:
        show_usage_message()
