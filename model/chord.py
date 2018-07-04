from copy import copy

from model.note import Note, note_name_octave_to_pitch, duration_map, c_major_pitch_list, standard_duration_list, \
    volume_map, standard_volume_list
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


def find_approximate_c_major_pitch(given_pitch: int):
    for j, c_major_pitch in enumerate(c_major_pitch_list):
        if c_major_pitch <= given_pitch and j + 1 < len(c_major_pitch_list) and c_major_pitch_list[
                    j + 1] >= given_pitch:
            # which is more close ?
            left = given_pitch - c_major_pitch
            right = c_major_pitch_list[j + 1] - given_pitch
            if left <= right:
                return c_major_pitch

            return c_major_pitch_list[j + 1]

    print("Warning====> no suitable c major note for pitch %d" % given_pitch)
    return None


def find_approximate_standard_duration(given_duration: float):
    for j, std_duration in enumerate(standard_duration_list):
        if std_duration <= given_duration:
            # could be the biggest
            if j == len(standard_duration_list) - 1:
                return std_duration
            next_std_duration = standard_duration_list[j+1]
            if next_std_duration >= given_duration:
                left = given_duration - std_duration
                right = next_std_duration - given_duration
                if left <= right:
                    return std_duration
                return next_std_duration
    return None


def find_approximate_standard_volume(given_volume: int):
    for j, std_volume in enumerate(standard_volume_list):
        if std_volume <= given_volume and j + 1 < len(standard_volume_list) and standard_volume_list[
                    j + 1] >= given_volume:
            left = given_volume - std_volume
            right = standard_volume_list[j + 1] - given_volume
            if left <= right:
                return std_volume
            return standard_volume_list[j + 1]


def shift_to_standard_volume(volume_list: List[int], fallback_volume: int = volume_map['mf']):
    chosen_ones = []
    for volume in volume_list:
        std_volume = find_approximate_standard_volume(volume)
        if std_volume is None:
            chosen_ones.append(fallback_volume)
            continue
        chosen_ones.append(std_volume)
    return chosen_ones


def shift_to_c_major_pitch(pitch_list: List[int]):
    chosen_ones = []
    for pitch in pitch_list:
        c_major_pitch = find_approximate_c_major_pitch(pitch)
        if c_major_pitch is None:
            chosen_ones.append(pitch)
            continue
        chosen_ones.append(c_major_pitch)
    return chosen_ones


def shift_to_standard_duration(duration_list: List[float], fallback_duration: int = duration_map['quarter_note']):
    chosen_ones = []
    for duration in duration_list:
        std_duration = find_approximate_standard_duration(duration)
        if std_duration is None:
            chosen_ones.append(fallback_duration)
            continue
        chosen_ones.append(std_duration)
    return chosen_ones


def build_chord_names(bar_notes: List[List[str]]):
    """
    Given a list of bars of which contains list of note names,
    this method returns a list of bars which contains list of chord name
    """
    bar_available_chords = []
    # find corresponding chords for each bar
    for one_bar in bar_notes:
        chord_names = chords_from_note_names(one_bar)
        print("===> chord name of choices %s from notes %s" % (chord_names, one_bar))
        bar_available_chords.append(chord_names)

    # now each bar may have several available chord
    # we want them to be different and want to use as many as possible different chords
    bar_chords = []
    used = set([])
    for i in range(len(bar_available_chords)):
        available_chords = bar_available_chords[i]
        if i == 0:
            # use directly first chord as reference
            bar_chords.append(available_chords[0])
            used.add(available_chords[0])
            continue

        if len(available_chords) > 0:
            # now we want to make a difference
            hit = False
            for chord in available_chords:
                if chord in used:
                    continue
                bar_chords.append(chord)
                used.add(chord)
                hit = True
                break

            # all chords are used before,
            # try not to be the same with the first one
            if hit is False:
                last_one = bar_chords[len(bar_chords) - 1]
                for chord in available_chords:
                    if chord != last_one:
                        bar_chords.append(chord)
                        used.add(chord)
                        hit = True
                        break
                # still false ? that is weird but we don't have much choice here
                if hit is False:
                    bar_chords.append(available_chords[0])
                    used.add(available_chords[0])
    return bar_chords
