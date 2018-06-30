from copy import copy

from model.note import Note, note_name_to_pitch
from typing import List


class Chord:
    """
    A Chord class is a wrapper of multiple notes.
    It comes handy when we want to write several notes at the same time
    """

    def __init__(self, notes: List[Note]):
        self.notes = notes

    @staticmethod
    def create_from_name_and_octave(chord_name: str, octave: int, time: int, duration: int, volume: int):
        pitches = c_major_octave_chord(chord_name, octave)
        notes = []
        for pitch in pitches:
            note = Note(pitch=pitch, time=time, duration=duration, volume=volume)
            notes.append(note)
        return Chord(notes)


major_progression = {
    1: [1, 3, 5],  # 4, 3
    2: [2, 4, 6],  # 3, 4
    3: [3, 5, 7],  # 3, 4
    4: [4, 6, 8],  # 4, 3
    5: [5, 7, 9],  # 4, 3
    6: [6, 8, 10],  # 3, 4
    7: [7, 9, 11, 13],  # 3, 3, 4
}

major_progression_pitch_gap = {
    1: [4, 3],
    2: [3, 4],
    3: [3, 4],
    4: [4, 3],
    5: [4, 3],
    6: [3, 4],
    7: [3, 3, 4],
}

c_major_chord_pos = dict(
    C=1,
    D=2,
    E=3,
    F=4,
    G=5,
    A=6,
    B=7,
)


def c_major_octave_chord(chord_name: str, octave: int):
    note_name = chord_name + str(octave)
    pitch = note_name_to_pitch(note_name)
    if pitch is None:
        raise Exception('unable to find %s note' % note_name)

    # build the major chord
    pos = c_major_chord_pos[chord_name]
    pitches = [pitch]
    tmp = copy(pitch)
    for gap in major_progression_pitch_gap[pos]:
        tmp += gap
        pitches.append(tmp)
    return pitches
