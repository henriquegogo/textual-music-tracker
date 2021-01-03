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


def rotate_pattern(pattern):
    notes = [list(line) for line in pattern.get('notes')]
    rotated = list(reversed(list(zip(*notes))))
    notes = list(reversed([''.join(list(reversed(line))) for line in rotated]))[4:]
    pattern['notes'] = notes

def process_patterns(patterns):
    bpm = int(info.get('bpm') or 120)
    max_length = 0

    for pattern in patterns:
        orientation = pattern.get('orientation')
        if orientation == 'horizontal': rotate_pattern(pattern)
        length = len(pattern.get('notes'))
        if length > max_length: max_length = length

    for i in range(max_length):
        for pattern in patterns:
            octave = int(pattern.get('octave') or 4)

            for note, velocity in enumerate(pattern.get('notes')[i]):
                note = (octave + 1) * 12 + note

                if velocity.isdigit():
                    message_type = NOTE_OFF if velocity == '0' else NOTE_ON
                    velocity = int(127 / 9 * float(velocity))
                    send_message(message_type, note, velocity)

        time.sleep(60 / bpm / 4)


def process_lines(lines):
    global info
    patterns = []
    pattern = None

    for line in lines:
        if ':' in line:
            key, value = line.split(':')
            dataset = pattern or info
            dataset[key.lower()] = value.strip()

        elif line == '# PATTERN':
            pattern = {'notes': []}

        elif pattern and any(char in line for char in '=-|0123456789'):
            pattern.get('notes').append(line)

        elif pattern and len(line) == 0:
            patterns.append(pattern)
            pattern = None

    process_patterns(patterns)


def show_usage_message():
    print('Usage: ./main.py FILENAME')


def open_file(filename):
    try:
        file = open(filename, 'r')

    except:
        print('Error reading file')

    lines = file.read().split('\n')
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
