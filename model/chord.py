from copy import copy

from model.note import Note, note_name_to_pitch, note_name_octave_to_pitch
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
    pitch = note_name_octave_to_pitch(chord_name, octave)
    if pitch is None:
        raise Exception('unable to find %s note' % chord_name)

    # build the major chord
    pos = c_major_chord_pos[chord_name]
    pitches = [pitch]
    tmp = copy(pitch)
    for gap in major_progression_pitch_gap[pos]:
        tmp += gap
        pitches.append(tmp)
    return pitches


def chord_from_note_names(note_names: List[str]):
    pos_set = set([])
    for note_name in note_names:
        pos_set.add(c_major_chord_pos[note_name])

    # we have their pos, try to find the ideal chord position
    match_of_chord = {}
    for order, members in major_progression.items():
        hit = 0
        for s in pos_set:
            if s in members:
                hit += 1
        match_of_chord[order] = hit

    # if we have same hits
    # may be the first highest hit with the first note name
    highest_order = []
    max_hits = max(match_of_chord.values())
    for order, hits in match_of_chord.items():
        if hits == max_hits:
            highest_order.append(order)

    order_of_choice = highest_order[0]
    if len(highest_order) > 1:
        if list(pos_set)[0] in highest_order:
            order_of_choice = list(pos_set)[0]

    # this help us find the chord name from int order
    chord_name = (list(c_major_chord_pos.keys())[list(c_major_chord_pos.values()).index(order_of_choice)])
    return chord_name



