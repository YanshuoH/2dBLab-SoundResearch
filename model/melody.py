from typing import List

from model.chord import shift_to_standard_duration, shift_to_c_major_pitch, shift_to_standard_volume
from model.note import Note


class Melody:
    """
    Given a list of notes with pitch, duration and volume.
    This class help us to build a melody regardless of notes' start time.
    It will divide all notes according to duration into bars of 4/4.
    """

    def __init__(self, note_list: List[Note]):
        self.input_note_list = note_list
        self.bar_note_result_list = []

    def build(self):
        # standardize the durations
        durations = [note.duration / 100 for note in self.input_note_list]
        durations = shift_to_standard_duration(durations)

        pitches = [note.pitch for note in self.input_note_list]
        pitches = shift_to_c_major_pitch(pitches)

        volumes = [note.volume for note in self.input_note_list]
        volumes = shift_to_standard_volume(volumes)

        std_notes = []
        for i, input_note in enumerate(self.input_note_list):
            # start time still unknown
            std_notes.append(Note(pitch=pitches[i], duration=durations[i], volume=volumes[i], time=0))

        # then with durations, we can split notes into bars.
        # the condition is simple, one bar should not have sum duration > 4
        bar_note_result_list = []
        bar_note_result = []
        beats_of_one_bar = 4
        sum_duration = 0
        for i, duration in enumerate(durations):
            if sum_duration + duration <= beats_of_one_bar:
                bar_note_result.append(std_notes[i])
                sum_duration += duration
            else:
                # create a new bar, persist that last bar
                bar_note_result_list.append(bar_note_result)
                bar_note_result = []
                sum_duration = 0

        # we have divided notes into melody
        # compute each note's start time
        start_time = 0
        for one_bar in bar_note_result_list:
            bar_start_time = start_time
            for note in one_bar:
                note.time = bar_start_time
                bar_start_time += note.duration
            start_time += beats_of_one_bar

        self.bar_note_result_list = bar_note_result_list
        return self
