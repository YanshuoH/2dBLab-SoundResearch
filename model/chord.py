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
        note_names = c_major_octave_chord(chord_name, octave)
        notes = []
        for note_name in note_names:
            note = Note(pitch=note_name_to_pitch(note_name), time=time, duration=duration, volume=volume)
            notes.append(note)
        return Chord(notes)


c_major_chord_map = dict(
    c_major=['C', 'E', 'G'],
    d_minor=['D', 'F', 'A'],
    e_minor=['E', 'G', 'B'],
    f_major=['F', 'A', 'C'],
    g_major=['G', 'B', 'D'],
    a_minor=['A', 'C', 'E'],
    b_diminished=['B', 'D', 'F', 'A']
)


def c_major_octave_chord(chord_name: str, octave: int):
    l = c_major_chord_map[chord_name]
    res = []
    for pitch in l:
        res.append(pitch + str(octave))
    return res
