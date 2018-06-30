from midiutil import MIDIFile

from model.chord import Chord
from model.note import Note, note_map
from model.track import Track


def create_midi_file(num_tracks: int, file_format: int):
    return MIDIFile(numTracks=num_tracks, file_format=file_format)


def save_midi_file(filename: str, midi_file: MIDIFile):
    with open(filename, "wb") as output_file:
        midi_file.writeFile(output_file)


midi_instance = create_midi_file(num_tracks=2, file_format=1)

tempo = 90
track1 = Track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)
track2 = Track(midi_instance=midi_instance, track=1, channel=0, tempo=tempo)

track1.add_note(Note(note_map['C6'], 0, 1, 60))
track1.add_note(Note(note_map['E6'], 1, 1, 80))
track1.add_note(Note(note_map['G6'], 2, 1, 100))
track1.add_note(Note(note_map['B6'], 3, 1, 100))

chord = Chord.create_from_name_and_octave(chord_name='c_major', octave=3, time=0, duration=4, volume=60)
track2.add_chord(chord)
save_midi_file('test.mid', midi_instance)
