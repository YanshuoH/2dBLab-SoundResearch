from typing import List

from copy import copy, deepcopy

from model.chord import build_chord_names, Chord, Appregio
from model.drum import DrumBar
from model.note import Note, volume_map, note_name_to_pitch, note_name_octave_to_pitch, duration_map


class Phrase2:
    """
    Given list of barr of notes, it will compute the chord and appregio notes
    """

    def __init__(self, bars_of_notes: List[List[Note]], start_time: int = 0):
        self.bars_of_notes = bars_of_notes
        self.start_time = copy(start_time)
        self.bars_of_chord = self.__build_chord_names()

    def __build_chord_names(self):
        """
        convert bars of notes into plain note name like CDEFGAB
        """
        bars_of_note_names = []
        for one_bar in self.bars_of_notes:
            bar_of_note_names = []
            for note in one_bar:
                bar_of_note_names.append(note.note_name[0])
            bars_of_note_names.append(bar_of_note_names)

        return build_chord_names(bars_of_note_names)

    def build_chords(self, std_octave: int, volume: int = volume_map['p']):
        """
        in stead of chord names, build real notes of chords
        """
        chords = []
        start_time = copy(self.start_time)
        for chord_name in self.bars_of_chord:
            octave = copy(std_octave)
            # chord may need octave shifting when it comes to higher chord
            if chord_name in ['G', 'A', 'B']:
                octave -= 1
            # The nature octave is 3 below notes melody
            chord = Chord.create_from_name_and_octave(chord_name=chord_name, octave=std_octave,
                                                      time=start_time, duration=4,
                                                      volume=volume)
            chords.append(chord)
            start_time += 4
        return chords

    def build_double_chord(self, std_octave: int, volume: int = volume_map['p']):
        chords = []
        start_time = copy(self.start_time)
        for chord_name in self.bars_of_chord:
            octave = copy(std_octave)
            # chord may need octave shifting when it comes to higher chord
            if chord_name in ['G', 'A', 'B']:
                octave -= 1
            chord1 = Chord.create_from_name_and_octave(chord_name=chord_name, octave=std_octave,
                                                       time=start_time, duration=2,
                                                       volume=volume)
            chord2 = Chord.create_from_name_and_octave(chord_name=chord_name, octave=std_octave,
                                                       time=start_time + 2, duration=2,
                                                       volume=volume)
            chords.append(chord1)
            chords.append(chord2)
            start_time += 4
        return chords

    def build_guitar_chord(self, std_octave: int, volume: int = volume_map['ppp']):
        chords = []
        start_time = copy(self.start_time)
        for chord_name in self.bars_of_chord:
            octave = copy(std_octave)
            if chord_name in ['E', 'F', 'G']:
                octave -= 1
            # count the beat
            durations = [1, 0.5, 0.5, 1, 0.5, 0.25, 0.25]
            start_time_in_bar = copy(start_time)
            for duration in durations:
                chord = Chord.create_guitar_chord_from_name_and_octave(chord_name=chord_name, octave=std_octave,
                                                                       time=start_time_in_bar, duration=duration,
                                                                       volume=volume)
                start_time_in_bar += duration
                chords.append(chord)
            start_time += 4
        return chords

    def build_appregios(self, std_octave: int, volume: int = volume_map['f'], style: int = 1):
        appregios = []
        start_time = copy(self.start_time)
        for chord_name in self.bars_of_chord:
            octave = copy(std_octave)
            # chord may need octave shifting when it comes to A or B chord
            if chord_name in ['G', 'A', 'B']:
                octave -= 1
            # The nature octave is 2 below notes melody
            note_duration = duration_map['quarter_note']
            if style == 2:
                note_duration = duration_map['eighth_note']
            appregio = Appregio.create(chord_name=chord_name, octave=octave,
                                       time=start_time, volume=volume, note_duration=note_duration)
            appregios.append(appregio)
            start_time += 4
        return appregios

    def build_root_note(self, std_octave: int, volume: int = volume_map['p']):
        root_notes = []
        start_time = copy(self.start_time)
        for note_name in self.bars_of_chord:
            octave = copy(std_octave)
            note = Note(pitch=note_name_octave_to_pitch(note_name, octave), duration=4, time=start_time, volume=volume)
            root_notes.append(note)
            start_time += 4
        return root_notes

    def build_double_root_note(self, std_octave: int, volume: int = volume_map['p']):
        root_notes = []
        start_time = copy(self.start_time)
        for note_name in self.bars_of_chord:
            octave = copy(std_octave)
            # chord may need octave shifting when it comes to higher chord
            if note_name in ['G', 'A', 'B']:
                octave -= 1
            note1 = Note(pitch=note_name_octave_to_pitch(note_name, octave), duration=2, time=start_time, volume=volume)
            note2 = Note(pitch=note_name_octave_to_pitch(note_name, octave), duration=2, time=start_time + 2,
                         volume=volume)
            root_notes.append(note1)
            root_notes.append(note2)
            start_time += 4
        return root_notes

    def build_drum(self, volume: int = volume_map['p'], style: int = 1):
        start_time = copy(self.start_time)
        return DrumBar(start_time=start_time, std_volume=volume, bar_count=len(self.bars_of_notes)).build_style1()

    def standardize(self, std_octave: int = 6):
        """
        Sometimes we may need to standardize the note's pitches.
        Because raw input of sound could have many noise notes and human voice could be very flat,
        It is important to make a difference here.
        """
        self.bars_of_notes = self.__converge_notes(std_octave)
        return self

    def __converge_notes(self, reference_octave: int):
        # Try to identify the boundary
        octave_seq = []
        for one_bar in self.bars_of_notes:
            for note in one_bar:
                octave_seq.append(note.note_name[1])
        octave_seq_set = set(octave_seq)
        # move all into 2 octave
        octave_seq_set = sorted(octave_seq_set)
        # @TODO: test: potential improvement will be compute the middle hits to define the shifting algo
        # maybe a group of two ?
        i = round(len(octave_seq_set) / 2)
        set1 = octave_seq_set[0:i]
        set2 = octave_seq_set[i:len(octave_seq_set)]
        set1_to_octave = reference_octave
        set2_to_octave = reference_octave + 1
        # make a copy of notes and shift their octaves
        bars_of_notes = deepcopy(self.bars_of_notes)
        for one_bar in bars_of_notes:
            for note in one_bar:
                note_octave = note.note_name[1]
                if note_octave in set1:
                    note_name = note.note_name[0] + str(set1_to_octave)
                elif note_octave in set2:
                    note_name = note.note_name[0] + str(set2_to_octave)
                else:
                    note_name = note.note_name
                # redefine the pitch value
                # print('shifting... from %s to %s' % (note.note_name, note_name))
                note.pitch = note_name_to_pitch(note_name)
                note.note_name = note_name
        return bars_of_notes
