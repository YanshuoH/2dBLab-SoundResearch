from copy import copy

from model.note import Note, note_name_octave_to_pitch, duration_map
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


class Appregio:
    """
    Appregio class is a wrapper of multiple notes.
    It will play each notes in a chord sequentially.
    Each note share the same note_duration.

    A tricky thing with appregio is that to sound better, we add half duration for each note
    """

    def __init__(self, notes: List[Note]):
        self.notes = notes

    @staticmethod
    def create(chord_name: str, octave: int, time: int, volume: int, note_count: int = 4,
               note_duration: int = duration_map['quarter_note']):
        pitches = c_major_octave_chord(chord_name, octave)
        notes = []
        start_time = copy(time)
        extended_note_duration = copy(note_duration)
        extended_note_duration *= 1.5
        for pitch in pitches:
            note = Note(pitch=pitch, time=start_time, duration=extended_note_duration, volume=volume)
            notes.append(note)
            start_time += note_duration
        if len(pitches) < note_count:
            for pitch in reversed(pitches[0:len(pitches) - 1]):
                note = Note(pitch=pitch, time=start_time, duration=extended_note_duration, volume=volume)
                notes.append(note)
                start_time += note_duration
                if len(notes) == note_count:
                    break
        return Appregio(notes)


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

c_major_chord_order_map = {
    1: 'C',
    2: 'D',
    3: 'E',
    4: 'F',
    5: 'G',
    6: 'A',
    7: 'B',
}


def c_major_octave_chord(chord_name: str, octave: int):
    """
     Given chord name in c major chord progression,
     this returns the pitches for MIDI output
    """
    pitch = note_name_octave_to_pitch(chord_name, octave)
    if pitch is None:
        raise Exception('unable to find %s%s note' % (chord_name, octave))

    # build the major chord
    pos = c_major_chord_pos[chord_name]
    pitches = [pitch]
    tmp = copy(pitch)
    for gap in major_progression_pitch_gap[pos]:
        tmp += gap
        pitches.append(tmp)
    return pitches


def chords_from_note_names(note_names: List[str]):
    """
    Given a list of note names, will return the maximum hit of notes in chords
    """
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
    highest_orders = []
    max_hits = max(match_of_chord.values())
    for order, hits in match_of_chord.items():
        if hits == max_hits:
            highest_orders.append(order)

    # return the names of highest order of choice
    chord_names = []
    for order in highest_orders:
        for name, that_order in c_major_chord_pos.items():
            if order == that_order:
                chord_names.append(name)
                break
    return chord_names


def get_in_chord_notes(chord_name: str, note_names: List[str]):
    orders = major_progression[c_major_chord_pos[chord_name]]
    orders_of_note_names = [c_major_chord_pos[note_name] for note_name in note_names]
    set1 = set(orders)
    set2 = set(orders_of_note_names)
    remains = set1.intersection(set2)
    return [c_major_chord_order_map[remain] for remain in remains]


def is_next_order(current: str, target: str):
    """
    For example, D is next order of C, C is next order of B
    """
    c = c_major_chord_pos[current]
    t = c_major_chord_pos[target]
    if c == 7:
        c = 0
    if c + 1 == t:
        return True
    return False


def is_previous_order(current: str, target: str):
    """
    For example, B is previous order of C, C is previous order of D
    """
    c = c_major_chord_pos[current]
    t = c_major_chord_pos[target]
    if t == 7:
        t = 0
    if t + 1 == c:
        return True
    return False
