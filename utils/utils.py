import os
from typing import List

import numpy
from aubio import notes, source, pitch, tempo
from midiutil import MIDIFile
from midiutil.MidiFile import TICKSPERQUARTERNOTE, NoteOn
from pydub import AudioSegment

from model.channel import channel_map, CHANNEL_NAME_DRUM_KIT
from model.note import Note, drum_map


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
    print("====> reading notes from sound file")
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


def read_bpm_from_sound_file(filename: str, samplerate: int = DEFAULT_SAMPLE_RATE):
    print("====> reading bpm from sound file")
    win_s, hop_s = 1024, 512
    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    '''
    phase  Phase based onset detection function

      This function uses information both in frequency and in phase to determine
      changes in the spectral content that might correspond to musical onsets. It
      is best suited for complex signals such as polyphonic recordings.

      Juan-Pablo Bello, Mike P. Davies, and Mark B. Sandler.  Phase-based note
      onset detection for music signals. In Proceedings of the IEEE International
      Conference on Acoustics Speech and Signal Processing, pages 441­444,
      Hong-Kong, 2003.
    '''
    o = tempo("phase", win_s, hop_s, samplerate)

    beats = []
    total_frames = 0
    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            # if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break

    def beats_to_bpm(beats, path):
        # if enough beats are found, convert to periods then to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60. / numpy.diff(beats)
            return numpy.median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0

    return beats_to_bpm(beats, filename)


def read_pitch_from_sound_file(filename: str, samplerate: int = DEFAULT_SAMPLE_RATE):
    """
    this method try to read pitches from a sound wave file with a list of dict of pitch and confidence
    """
    if os.path.isfile(filename) is False:
        raise Exception('File not found with filename = %s' % filename)

    print("====> reading pitch from sound file")
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

    group_result_with_log_density = compute_density_from_pitch_result(result)
    density_level_list = compute_density_level(group_result_with_log_density, result[len(result) - 1]['time'])
    print("====> density level list length %s" % len(density_level_list))
    proportion_list = get_emphasis_start_times(group_result_with_log_density, result[len(result) - 1]['time'])
    print("====> emphasis proportion list length = %d" % len(proportion_list))
    return dict(pitch_result=result, emphasis_proportion_list=proportion_list, density_level_list=density_level_list)


def compute_density_level(group_result_with_log_density: List[dict], length: float):
    """
    following result of function compute_density_from_pitch_result, this method will compute for each group,
    a readable (from 0 to 9) density value for further usage
    :param group_result_with_log_density:
    :param length end time
    :return:
    """
    log_density_list = [group['log_density'] for group in group_result_with_log_density]
    max_val = max(log_density_list)
    min_val = min(log_density_list)
    # split range with 10 and compute which to where
    range_val = max_val - min_val
    total_level = 9
    gap = range_val / total_level
    level_list = []
    for i, log_density in enumerate(log_density_list):
        level = 5
        if gap != 0:
            level = round((log_density - min_val) / gap)
        level_list.append(dict(level=level, start_time=group_result_with_log_density[i]['pitches'][0]['time']))

    for level_dict in level_list:
        start = level_dict['start_time'] / length
        level_dict['start_time'] = start
    return level_list


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


def get_emphasis_start_times(group_result_with_log_density: List[dict], length: float, coefficient: int = 0.8,
                             threshold: int = 1):
    """
    :param group_result_with_log_density compute_density_from_pitch_result function result
    :param coefficient compares to the max log value, which should we consider emphasis
    :param threshold means only pitch density more than threshold could use emphasis method
    :param length is the length of sound in second unit
    """
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


def drum_note_to_heart_beat_track(midi_instance: MIDIFile):
    """
    @Deprecated
    """
    # exporting bass drum notes
    bass_drum_beats_in_ms = []
    ms_per_tick = 60 * 1000 / (tempo * TICKSPERQUARTERNOTE)
    for event in midi_instance.tracks[channel_map[CHANNEL_NAME_DRUM_KIT]].eventList:
        if isinstance(event, NoteOn) and event.pitch == drum_map['BassDrum']:
            bass_drum_beats_in_ms.append(ms_per_tick * event.tick)
    single_heart_beat = AudioSegment.from_file('./single_heartbeat.mp3', format='mp3')
    heartbeat_track = AudioSegment.empty()
    for i, bass_drum_beat_note_on in enumerate(bass_drum_beats_in_ms):
        if i == 0:
            heartbeat_track += AudioSegment.silent(duration=bass_drum_beat_note_on)
        elif i + 1 < len(bass_drum_beats_in_ms):
            # if the next bass drum time is early than heartbeat track
            if len(heartbeat_track) > bass_drum_beats_in_ms[i + 1]:
                continue
            # fill the gap till the next heart beat
            gap = bass_drum_beats_in_ms[i + 1] - len(heartbeat_track)
            heartbeat_track += AudioSegment.silent(duration=gap)
        elif i == len(bass_drum_beats_in_ms) - 1:
            # ignore the last one
            continue
        heartbeat_track += single_heart_beat

    heartbeat_track.export('heartbeat_track.mp3', format='mp3')


def get_one_bar_heart_beat(filename: str, bpm: int):
    """
    given defined bpm, it generates a bar of heartbeat sound.
    given the fact that the heart beat track has a certain length of each beat, the bpm cannot be too high,
    which is undetermined yet.
    :return:
    """
    heart_beat_track = AudioSegment.from_file(file=filename, format='mp3')
    heart_beat_1 = heart_beat_track[70:180]
    heart_beat_2 = heart_beat_track[380:490]
    # AudioSegment.export(part, 'single_heartbeat1.mp3')

    tick_per_sec = 60 * 1000 / bpm

    # make a sequential beats by a quarter notes which means a tick contains 2 heat beats
    # and this is only applied for a half bar.
    # in conclusion, one bar has two sets of heart beats
    result_track = AudioSegment.empty()

    # first set
    result_track += heart_beat_1
    gap = tick_per_sec / 2 - len(result_track)
    result_track += AudioSegment.silent(gap)
    result_track += heart_beat_2
    # fill the gap
    gap = tick_per_sec * 2 - len(result_track)
    result_track += AudioSegment.silent(gap)

    # # second set
    result_track += heart_beat_1
    gap = tick_per_sec * 2.5 - len(result_track)
    result_track += AudioSegment.silent(gap)
    result_track += heart_beat_2
    # # fill the end gap
    gap = tick_per_sec * 4 - len(result_track)
    result_track += AudioSegment.silent(gap)

    return result_track


def get_heart_beat_track(filename: str, bar_count: int, bpm: int):
    result = AudioSegment.empty()
    for i in range(bar_count):
        result += get_one_bar_heart_beat(filename, bpm)
    return result


def get_heart_beat_track_and_save(filename: str, dest_filename: str, bar_count: int, bpm: int):
    result = get_heart_beat_track(filename, bar_count, bpm)
    # reduce 3dB of the result
    result = result - 3

    # tick_per_sec = 60 * 1000 / bpm
    # fade_time = round(tick_per_sec * 4)
    # result.fade_in(fade_time)
    # result.fade_out(fade_time)
    AudioSegment.export(result, dest_filename)


REF_BPM = 90
BOTTOM_BPM = 50


def normalize_bpm(bpm: int):
    """
    presume that general bpm of voice result is in range of 50 - 200
    and we may want to center speed to 90 as reference.
    so the algorithm could be:
    gap = abs(90 - x)
    result = 50 + gap
    :param bpm:
    :return:
    """
    return abs(REF_BPM - bpm) + BOTTOM_BPM
