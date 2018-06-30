from midiutil import MIDIFile

from model.chord import Chord
from model.note import Note


class Track:
    """
    Assume that one track only use one channel
    """

    def __init__(self, midi_instance: MIDIFile, track: int, channel: int, tempo: int):
        self.midi_instance = midi_instance
        self.track = track
        self.channel = channel
        self.tempo = tempo

    @staticmethod
    def create_track(midi_instance: MIDIFile, track: int, channel: int, tempo: int):
        # assume a static tempo
        midi_instance.addTempo(track=track, time=0, tempo=tempo)
        return Track(midi_instance, track, channel, tempo)

    def add_note(self, note: Note):
        self.midi_instance.addNote(track=self.track, channel=self.channel, pitch=note.pitch, time=note.time,
                                   duration=note.duration, volume=note.volume)

    def add_chord(self, chord: Chord):
        for note in chord.notes:
            self.add_note(note)
