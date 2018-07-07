from midiutil import MIDIFile

from model.channel import channel_map, get_channel_program_int, reversed_channel_map, channel_panning_map
from model.chord import Chord, Appregio
from model.note import Note


class Track:
    """
    Assume that one track only use one channel
    """

    PAN_CONTROLLER_NUMBER = 10

    def __init__(self, midi_instance: MIDIFile, track: int, channel: int, tempo: int, track_name: str = ''):
        self.midi_instance = midi_instance
        self.track = track
        self.channel = channel
        self.tempo = tempo
        self.track_name = track_name

    @staticmethod
    def create_track(midi_instance: MIDIFile, track: int, channel: int, tempo: int, track_name: str = ''):
        """
        :param midi_instance:
        :param track:
        :param channel:
        :param tempo:
        :param track_name
        :return: Track
        """
        # assume a static tempo
        midi_instance.addTempo(track=track, time=0, tempo=tempo)
        midi_instance.addTrackName(track=track, time=0, trackName=track_name)
        return Track(midi_instance, track, channel, tempo, track_name)

    @staticmethod
    def create_track_map(midi_instance: MIDIFile, tempo: int = 90):
        track_map = {}
        i = 0
        for k, v in channel_map.items():
            track = Track.create_track(midi_instance=midi_instance, track=i, channel=v, tempo=tempo, track_name=k)
            print('track = %d, channel = %d' % (i, v))
            if v != 9:
                midi_instance.addProgramChange(i, i, 0, get_channel_program_int(v))
            track_map[reversed_channel_map[v]] = track
            midi_instance.addControllerEvent(track=i, channel=v, time=0, controller_number=Track.PAN_CONTROLLER_NUMBER,
                                             parameter=channel_panning_map[k])
            i += 1
        return track_map

    def add_note(self, note: Note):
        # print("Track %d add note with pitch = %d, time = %f, duration = %f, volume = %d" %
        #       (self.track, note.pitch, note.time, note.duration, note.volume))
        self.midi_instance.addNote(track=self.track, channel=self.channel, pitch=note.pitch, time=note.time,
                                   duration=note.duration, volume=note.volume)

    def add_chord(self, chord: Chord):
        for note in chord.notes:
            self.add_note(note)

    def add_appregio(self, appregio: Appregio):
        for note in appregio.notes:
            self.add_note(note)
