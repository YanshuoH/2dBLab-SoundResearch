from copy import copy
from typing import List

from model.chord import chords_from_note_names, get_in_chord_notes, Chord, Appregio, build_chord_names
from model.note import note_name_octave_to_pitch, Note, volume_map, duration_map


class Phrase:
    """
    A phrase represents a set of chords and melody notes with a duration of defined bar_count.
    It generates Note entities and Chord entities for Track.add method's usage
    """

    def __init__(self, note_names: List[str], start_time: int,
                 bar_count: int = 4, std_octave: int = 4):
        self.note_names = note_names
        self.std_octave = std_octave
        self.start_time = start_time
        self.bar_count = bar_count
        self.std_octave = std_octave
        self.note_names_of_bars = self.build_note_names()
        self.chord_names_of_bars = self.build_chord_names()

    def build_chord_names(self):
        """
        using given notes to generate several chords of one phrase.
        """
        bar_notes = self.build_note_names()
        return build_chord_names(bar_notes)

    def build_note_names(self):
        """
        using given notes to generate a melody of one phrase.
        """
        bar_notes = []
        print('====> note_names length %d, bar_count %d' % (len(self.note_names), self.bar_count))
        if len(self.note_names) < self.bar_count:
            # so there's may be several bar definitions missing
            for note_name in self.note_names:
                bar_notes.append([note_name])
        else:
            # split notes by bar count
            note_count = len(self.note_names) // self.bar_count
            # each group has note number of note_count
            # if there's a datum in the end, append it to the last bar group
            pos = 0
            for i in range(self.bar_count):
                start = pos
                end = pos + note_count
                if i == self.bar_count - 1:
                    # last one use the last idx
                    # @TODO: the last phrase could be very nasty if we place all residue in the last bar
                    # @TODO: we may want the last note to be a resolution of chord, not a random ones
                    end = len(self.note_names)
                bar_notes.append(self.note_names[start:end])
                pos = end
        print('===> note names of phrase is %s' % bar_notes)
        return bar_notes

    def build_chords(self, volume: int = volume_map['p']):
        chords = []
        start_time = copy(self.start_time)
        for chord_name in self.chord_names_of_bars:
            octave = copy(self.std_octave)
            # chord may need octave shifting when it comes to A or B chord
            if chord_name == 'A' or chord_name == 'B':
                octave -= 1
            # The nature octave is 3 below notes melody
            chord = Chord.create_from_name_and_octave(chord_name=chord_name, octave=octave - 4,
                                                      time=start_time, duration=4,
                                                      volume=volume)
            chords.append(chord)
            start_time += 4
        return chords

    def build_appregios(self, volume: int = volume_map['mf']):
        appregios = []
        start_time = copy(self.start_time)
        for chord_name in self.chord_names_of_bars:
            octave = copy(self.std_octave)
            # chord may need octave shifting when it comes to A or B chord
            if chord_name == 'A' or chord_name == 'B':
                octave -= 1
            # The nature octave is 2 below notes melody
            appregio = Appregio.create(chord_name=chord_name, octave=octave - 1,
                                       time=start_time, volume=volume)
            appregios.append(appregio)
            start_time += 4
        return appregios

    def build_notes(self, volume: int = volume_map['f']):
        """
        1. how to define near notes' octave pitch is a tricky thing here.
            Human ear seems to be more acceptable when the nearliest notes played together.
            For example C6 with B5 is fine, but C6 with B6 could be nasty
        2. how to define note's duration is another funny thing...
            - if 1 bar has more than 4 notes?
            - if 1 bar has fewer than 4 notes?
            who should sustain longer ?
        """
        start_time = copy(self.start_time)
        notes = []

        for idx, one_bar in enumerate(self.note_names_of_bars):
            notes.extend(self.__build_one_bar_notes(self.chord_names_of_bars[idx], one_bar, start_time, volume))
            start_time += 4
        return notes

    def __build_one_bar_notes(self, chord_name: str, note_names: List[str], bar_start_time: int, volume: int):
        note_count = len(note_names)
        in_chord_notes = get_in_chord_notes(chord_name, note_names)
        print("===> given chord %s and note names %s, in chord notes is %s" % (chord_name, note_names, in_chord_notes))

        # find ones to stretch, no one, just ignore it
        stretch_note_idx = []
        for i in range(len(note_names)):
            if note_names[i] in in_chord_notes:
                stretch_note_idx.append(i)

        # value affection in conditions below
        max_stretch_count = 0
        std_duration = 0
        if note_count == 1:
            std_duration = duration_map['whole_note']
        elif note_count == 2:
            std_duration = duration_map['half_note']
        elif note_count == 3:
            max_stretch_count = 1
            std_duration = duration_map['quarter_note']
        elif note_count == 4:
            std_duration = duration_map['quarter_note']
            pass
        elif 4 < note_count < 8:
            max_stretch_count = 8 - note_count
            std_duration = duration_map['eighth_note']
            pass
        elif note_count == 8:
            std_duration = duration_map['eighth_note']
            pass
        elif 8 < note_count < 16:
            max_stretch_count = 16 - note_count
            std_duration = duration_map['sixteenth_note']
            pass
        elif 16 == note_count:
            std_duration = duration_map['sixteenth_note']
            pass
        elif note_count > 16:
            std_duration = duration_map['sixteenth_note']
            # here we need to cut something
            note_names = note_names[0:16]
            pass

        note_shifting_values = [0 for _ in note_names]
        prev_notes = set([])
        for i, note_name in enumerate(note_names):
            if i - 1 >= 0 and note_names[i - 1] == 'C' and note_names[i] == 'B':
                # if C's next is a be, lower the octave of B note to C
                note_shifting_values[i] = note_shifting_values[i - 1] - 1
                continue
            # if previous note is near order, shift the octave
            if note_name in prev_notes:
                # do shifting for doubling
                note_shifting_values[i] = 1
                # remove from set
                prev_notes.discard(note_name)
                continue
            prev_notes.add(note_name)
        notes = []
        start_time = copy(bar_start_time)
        stretch_count = 0
        for i, note_name in enumerate(note_names):
            # compute duration
            duration = std_duration
            if i in stretch_note_idx:
                if stretch_count > max_stretch_count:
                    break
                duration = std_duration * 2
                stretch_count += 1

            print("====> note name %s, duration %s, start time %s" % (note_name, duration, start_time))
            octave = self.std_octave + note_shifting_values[i]
            notes.append(Note(pitch=note_name_octave_to_pitch(note_name, octave), time=start_time,
                              duration=duration, volume=volume))
            start_time += duration
        return notes
