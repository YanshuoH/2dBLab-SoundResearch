from copy import copy

from model.chord import Chord, chords_from_note_names
from model.note import Note, note_name_octave_to_pitch
from model.track import Track

from algo.text import sanitize, build_melody_from_phrase
from utils import create_midi_file, save_midi_file

input_str = '''
O mistress mine, where are you roaming?
O stay and hear! your true-love's coming
That can sing both high and low;
Trip no further, pretty sweeting,
Journey's end in lovers' meeting-
Every wise man's son doth know.

What is love? 'tis not hereafter;
Present mirth hath present laughter;
What's to come is still unsure:
In delay there lies no plenty,-
Then come kiss me, Sweet and twenty,
Youth's a stuff will not endure.
'''

"""
A hundred miles, a hundred miles,
A hundred miles, a hundred miles
You can hear the whistle blow a hundred miles
Lord, I'm one, Lord, I'm two,
Lord, I'm three, Lord, I'm four
Lord, I'm five hundred miles away from home
"""

midi_instance = create_midi_file(num_tracks=1, file_format=1)
tempo = 90
track1 = Track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)

octave = 5
time = 0
bar_count = 2
volume = 80

phrases = sanitize(input_str)
notes = []
for phrase in phrases:
    note_dict_list = build_melody_from_phrase(phrase, bar_count, octave)
    phrase_time = copy(time)
    for note_dict in note_dict_list:
        note = Note(pitch=note_name_octave_to_pitch(note_dict['note_name'], note_dict['octave']), time=phrase_time,
                    duration=note_dict['duration'], volume=note_dict['volume'])
        notes.append(note)
        phrase_time += note_dict['duration']

    # get note names to build chord
    note_names = []
    for note_dict in note_dict_list:
        note_names.append(note_dict['note_name'])
    chord_name = chords_from_note_names(note_names)[0]
    print("====> chord of choice %s, from notes %s" % (chord_name, note_names))
    track1.add_chord(
        Chord.create_from_name_and_octave(chord_name=chord_name, octave=3, time=time, duration=bar_count * 4,
                                          volume=volume))

    # one phrase occupies 4 bar times
    time += 4 * bar_count

for note in notes:
    track1.add_note(note)

save_midi_file('test.mid', midi_instance)
