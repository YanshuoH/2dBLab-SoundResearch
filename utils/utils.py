import os
from typing import List

import numpy
from aubio._aubio import notes, source, pitch
from midiutil import MIDIFile

from model.note import Note


def create_midi_file(num_tracks: int, file_format: int):
    return MIDIFile(numTracks=num_tracks, file_format=file_format)


def save_midi_file(filename: str, midi_file: MIDIFile):
    with open(filename, "wb") as output_file:
        midi_file.writeFile(output_file)
    print("====> file %s saved." % filename)


DEFAULT_SAMPLE_RATE = 44100
DOWN_SAMPLE = 1


def read_note_from_sound_file(filename: str, samplerate: int = DEFAULT_SAMPLE_RATE):
    """
    this method try to read notes from a sound wave file with a list of dict of start_time, pitch and duration
    """
    win_s = 512 // DOWN_SAMPLE  # fft size
    hop_s = 256 // DOWN_SAMPLE  # hop size
    # adjust sample rate
    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    notes_o = notes("default", win_s, hop_s, samplerate)

    result = []
    total_frames = 0
    while True:
        samples, read = s()
        new_note = notes_o(samples)
        # note too high considered as noise
        if new_note[0] != 0 and new_note[0] <= 120:
            note_klass = Note(time=total_frames / float(samplerate), pitch=new_note[0], volume=new_note[1] - 20,
                              duration=new_note[2])
            result.append(note_klass)
        total_frames += read
        if read < hop_s:
            break

    return result


def read_pitch_from_sound_file(filename: str, samplerate: int = DEFAULT_SAMPLE_RATE):
    """
    this method try to read pitches from a sound wave file with a list of dict of pitch and confidence
    """
    if os.path.isfile(filename) is False:
        raise Exception('File not found with filename = %s' % filename)

    win_s = 4096 // DOWN_SAMPLE  # fft size
    hop_s = 512 // DOWN_SAMPLE  # hop size

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    tolerance = 0.8

    pitch_o = pitch("yin", win_s, hop_s, samplerate)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    result = []

    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        # the pitch value is not rounded and many zeroes occur
        that_pitch = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()
        result.append(dict(time=total_frames / float(samplerate), pitch=that_pitch, confidence=confidence))
        total_frames += read
        if read < hop_s:
            break

    tmp = compute_density_from_pitch_result(result)
    proportion_list = get_emphasis_start_times(tmp, result[len(result) - 1]['time'])
    return dict(pitch_result=result, emphasis_proportion_list=proportion_list)


def compute_density_from_pitch_result(pitch_result: List[dict]):
    group_result = []
    group = []
    for i, pitch_dict in enumerate(pitch_result):
        # current is not zero, but previous is zero
        # should flush the group
        if round(pitch_dict['pitch']) != 0 and i - 1 >= 0 and round(pitch_result[i - 1]['pitch']) == 0:
            group_result.append(group)
            group = []
        group.append(pitch_dict)

    # now for each group we have the elements which are essentially divided by time frame
    # we just need to identify the average density and get the highest ones
    density_list = [len(group) for group in group_result]
    # average_density = sum(density_list) / len(density_list)
    log_density_list = numpy.log10(density_list)

    # only for those group with density > coefficient * log_max_density is qualified to be the emphasis one.
    # but here we just give the density log result
    group_result_with_log_density = []
    for i, group in enumerate(group_result):
        group_result_with_log_density.append(dict(log_density=log_density_list[i], pitches=group))
    return group_result_with_log_density


def get_emphasis_start_times(group_result_with_log_density: List[dict], length: float, threshold: int = 2.5):
    """
    :param group_result_with_log_density compute_density_from_pitch_result function result
    :param threshold means only pitch density more than threshold could use emphasis method
    :param length is the length of sound in second unit
    """
    coefficient = 0.8
    log_density_list = [group['log_density'] for group in group_result_with_log_density]
    max_log_density = max(log_density_list)
    filter_value = coefficient * max_log_density

    pitch_group_list = []
    for group in group_result_with_log_density:
        if group['log_density'] >= threshold and group['log_density'] >= filter_value:
            pitch_group_list.append(group['pitches'])

    # now we have pitch group, we can know where to start emphasis and where to end
    range_time_list = []
    for pitch_group in pitch_group_list:
        start = pitch_group[0]['time']
        end = pitch_group[len(pitch_group) - 1]['time']
        range_time_list.append(dict(start=start, end=end))

    # transform proportion value for further beats computing
    proportion_list = []
    for range_time in range_time_list:
        start = range_time['start'] / length
        end = range_time['end'] / length
        proportion_list.append(dict(start=start, end=end))
    return proportion_list

