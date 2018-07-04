import os

from aubio._aubio import notes, source, pitch
from midiutil import MIDIFile


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
        if new_note[0] != 0:
            result.append(dict(time=total_frames / float(samplerate), pitch=new_note[0], volume=new_note[1],
                               duration=new_note[2]))
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
        result.append(dict(pitch=that_pitch, confidence=confidence))
        total_frames += read
        if read < hop_s:
            break
    return result
