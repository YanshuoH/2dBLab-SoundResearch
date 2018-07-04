import uuid
from typing import List

from model.chord import shift_to_standard_duration, shift_to_c_major_pitch, build_chord_names
from model.note import reverse_note_map, duration_map, Note, note_name_octave_to_pitch


def sanitize_pitch_list(pitch_list: List[float]):
    """
    round the pitches, remove zeros
    """
    result = []
    for pitch in pitch_list:
        p = round(pitch)
        if p == 0:
            continue
        if p > 128:
            continue
        result.append(p)
    return result


def note_result_to_notes(note_result: List[dict], tempo: int, octave: int):
    """
    note_result consists a list of dict with keys: time, pitch, volume, duration.
    But the problem is that time stays in second and duration in some mist unit...
    So we just don't want notes to be overlapped.
    """
    # standardize the durations
    durations = [note_dict['duration'] / 100 for note_dict in note_result]
    durations = shift_to_standard_duration(durations)

    notes = [note_dict['pitch'] for note_dict in note_result]
    notes = shift_to_c_major_pitch(notes)

    # reformat note_list with new values, affect each note a uuid
    fmt_note_result = []
    for i, note_dict in enumerate(note_result):
        fmt_note = dict(uuid=uuid.uuid4(), pitch=notes[i], duration=durations[i], volume=note_dict['volume'])
        fmt_note_result.append(fmt_note)

    # now with durations, we can split notes into bars.
    # the condition is simple, one bar should not have sum duration > 4
    bar_note_pos_result = []
    bar_note_pos = []
    sum_duration = 0
    for i, duration in enumerate(durations):
        if sum_duration + duration <= 4:
            bar_note_pos.append(dict(pos=i, duration=duration))
            sum_duration += duration
        else:
            # create a new bar, persist that last bar
            bar_note_pos_result.append(bar_note_pos)
            bar_note_pos = []
            sum_duration = 0

    # and we can build chord for each bar
    bar_note_names = []
    for one_bar_note_pos in bar_note_pos_result:
        pitches = [notes[pos['pos']] for pos in one_bar_note_pos]
        note_names = [reverse_note_map[pitch][0] for pitch in pitches]
        bar_note_names.append(note_names)
    bar_chord_names = build_chord_names(bar_note_names)

    # now we can build the music with chord, appregio and melody
    start_time = 0
    octave = 5
    notes = []
    for i, one_bar in enumerate(bar_note_names):
        bar_time = start_time
        for j, note_name in enumerate(one_bar):
            duration = duration_map['quarter_note']
            pos_duration_dict_list = bar_note_pos_result[i]
            for d in pos_duration_dict_list:
                if d['pos'] == j:
                    duration = d['duration']
                    break
            note = Note(start_time=bar_time, pitch=note_name_octave_to_pitch())
            bar_time += duration
        start_time += 4

