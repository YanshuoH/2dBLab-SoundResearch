from typing import List

from midiutil import MIDIFile

from model.channel import CHANNEL_NAME_DRUM_KIT, CHANNEL_NAME_PIANO, CHANNEL_NAME_ELECTRIC_PIANO, \
    CHANNEL_NAME_ENSEMBLE_STRING_1, CHANNEL_NAME_ENSEMBLE_STRING_2, CHANNEL_NAME_ACOUSTIC_GUITAR, \
    CHANNEL_NAME_FINGER_STYLE_BASS, CHANNEL_NAME_CHURCH_ORGAN, CHANNEL_NAME_ELECTRIC_GUITAR_CLEAN
from model.melody import Melody
from model.note import volume_map, Note
from model.phrase_2 import Phrase2
from model.track import Track

MAX_LEVEL = 10
PIANO = 'piano'
PIANO_CHORD = 'piano_chord'
STRING_CHORD = 'string_chord'
GUITAR_CHORD = 'guitar_chord'
STRING_APPREGIO = 'string_appregio'
BASS = 'bass'
DRUM_LIGHT = 'drum_light'
PIANO_APPREGIO = 'piano_appregio'
DRUM_HEAVY = 'drum_heavy'
ORGAN = 'organ'
GUITAR_POWER_CHORD = 'guitar_power_chord'

arrangement_level_map = {
    0: [PIANO],
    1: [PIANO_CHORD],
    2: [STRING_CHORD],
    3: [],
    4: [GUITAR_CHORD, PIANO_APPREGIO],
    5: [STRING_APPREGIO, BASS, DRUM_LIGHT],
    6: [],
    7: [],
    8: [DRUM_HEAVY],
    # 9: [ORGAN],
    9: [],
}

arrangement_channel_map = {
    PIANO: CHANNEL_NAME_PIANO,
    PIANO_CHORD: CHANNEL_NAME_ELECTRIC_PIANO,
    STRING_CHORD: CHANNEL_NAME_ENSEMBLE_STRING_1,
    GUITAR_CHORD: CHANNEL_NAME_ACOUSTIC_GUITAR,
    STRING_APPREGIO: CHANNEL_NAME_ENSEMBLE_STRING_2,
    BASS: CHANNEL_NAME_FINGER_STYLE_BASS,
    DRUM_LIGHT: CHANNEL_NAME_DRUM_KIT,
    PIANO_APPREGIO: CHANNEL_NAME_ELECTRIC_PIANO,
    DRUM_HEAVY: CHANNEL_NAME_DRUM_KIT,
    ORGAN: CHANNEL_NAME_CHURCH_ORGAN,
    GUITAR_POWER_CHORD: CHANNEL_NAME_ELECTRIC_GUITAR_CLEAN,
}


def accumulate_arrangement_level_map():
    for i in range(MAX_LEVEL):
        if i == 0:
            continue
        arrangement_level_map[i].extend(arrangement_level_map[i - 1])


accumulate_arrangement_level_map()


class Arrangement:
    """
    Given file parsing results, it will create necessary tracks, build melody and other instruments with level mapping.
    Define each track volume and add created notes to corresponding tracks.
    In a word, it do all the jobs...
    """
    MELODY_OCTAVE = 4
    BAR_OF_PHRASE = 2
    NOTE_OF_BAR = 4

    def __init__(self, midi_instance: MIDIFile, tempo: int, note_result: List[dict], density_level_list: List[dict],
                 std_volume: int = volume_map['mf']):
        self.midi_instance = midi_instance
        self.tempo = tempo
        self.note_result = note_result
        self.density_level_list = density_level_list
        self.std_volume = std_volume
        self.track_map = Track.create_track_map(midi_instance=midi_instance, tempo=tempo)
        self.melody = None

    def build(self):
        # build melody first
        melody = Melody(self.note_result).build()
        self.melody = melody
        # divide melody bars with a group of 4, building phrases
        chunks = [melody.bar_note_result_list[x:x + Arrangement.BAR_OF_PHRASE] for x in
                  range(0, len(melody.bar_note_result_list), Arrangement.BAR_OF_PHRASE)]

        sum_beat = len(melody.bar_note_result_list) * Arrangement.BAR_OF_PHRASE
        chunk_level_list = self.__compute_chunks_level(chunks, sum_beat)
        begin_beat = 0
        for i, chunk in enumerate(chunks):
            phrase = Phrase2(bars_of_notes=chunk, start_time=begin_beat)
            bars_of_notes = phrase.standardize(std_octave=Arrangement.MELODY_OCTAVE).bars_of_notes
            # melody first
            for one_bar in bars_of_notes:
                for note in one_bar:
                    self.track_map[PIANO].add_note(note=note)

            # with defined level, decide what instruments to add
            self.__make_instruments_by_level(phrase=phrase, level=chunk_level_list[i])
            begin_beat += Arrangement.NOTE_OF_BAR * Arrangement.BAR_OF_PHRASE

    def __compute_chunks_level(self, chunks: List[List[Note]], sum_beat: int):
        """
        A chunk is 4 bars of notes
        """
        chunk_level_list = []
        for chunk in chunks:
            chunk_begin_time = chunk[0][0].time
            level = self.__find_density_level(chunk_begin_time / sum_beat)
            chunk_level_list.append(level)
        return chunk_level_list

    def __find_density_level(self, relative_position: float):
        for i, density_level in enumerate(self.density_level_list):
            if i == 0:
                continue
            prev_density_level = self.density_level_list[i - 1]
            current_density_level = self.density_level_list[i]
            if prev_density_level['start_time'] <= relative_position <= current_density_level['start_time']:
                return density_level['level']
        return 5

    def __make_instruments_by_level(self, phrase: Phrase2, level: int):
        instruments = arrangement_level_map[level]
        print('level = %d, instruments = %s' % (level, instruments))
        if PIANO_CHORD in instruments:
            chords = phrase.build_double_chord(Arrangement.MELODY_OCTAVE - 1)
            for chord in chords:
                self.track_map[CHANNEL_NAME_ELECTRIC_PIANO].add_chord(chord=chord)
        if STRING_CHORD in instruments:
            chords = phrase.build_chords(Arrangement.MELODY_OCTAVE - 1, volume=volume_map['pp'])
            for chord in chords:
                self.track_map[CHANNEL_NAME_ENSEMBLE_STRING_1].add_chord(chord=chord)
        if GUITAR_CHORD in instruments:
            chords = phrase.build_guitar_chord(Arrangement.MELODY_OCTAVE - 1, volume=volume_map['ppp'])
            for chord in chords:
                self.track_map[CHANNEL_NAME_ACOUSTIC_GUITAR].add_chord(chord=chord)
        if STRING_APPREGIO in instruments:
            appregios = phrase.build_appregios(Arrangement.MELODY_OCTAVE, volume=volume_map['ppp'])
            for appregio in appregios:
                self.track_map[CHANNEL_NAME_ENSEMBLE_STRING_2].add_appregio(appregio=appregio)
        if BASS in instruments:
            root_notes = phrase.build_double_root_note(std_octave=Arrangement.MELODY_OCTAVE - 3,
                                                       volume=volume_map['mf'])
            for note in root_notes:
                self.track_map[CHANNEL_NAME_FINGER_STYLE_BASS].add_note(note)
        if DRUM_LIGHT in instruments and DRUM_HEAVY not in instruments:
            drum_bar_notes = phrase.build_drum(volume=volume_map['p'])
            for one_bar in drum_bar_notes:
                for note in one_bar:
                    self.track_map[CHANNEL_NAME_DRUM_KIT].add_note(note)
        if PIANO_APPREGIO in instruments:
            appregios = phrase.build_appregios(Arrangement.MELODY_OCTAVE, volume=volume_map['p'], style=2)
            for appregio in appregios:
                self.track_map[CHANNEL_NAME_ELECTRIC_PIANO].add_appregio(appregio)
        if DRUM_HEAVY in instruments:
            drum_bar_notes = phrase.build_drum(volume=volume_map['mf'])
            for one_bar in drum_bar_notes:
                for note in one_bar:
                    self.track_map[CHANNEL_NAME_DRUM_KIT].add_note(note)
        if ORGAN in instruments:
            root_notes = phrase.build_root_note(std_octave=Arrangement.MELODY_OCTAVE + 1,
                                                volume=volume_map['ppp'])
            for note in root_notes:
                self.track_map[CHANNEL_NAME_CHURCH_ORGAN].add_note(note)
        if GUITAR_POWER_CHORD in instruments:
            pass
