import sys

from algo.sound import sanitize_pitch_list
from model.note import Note
from model.track import Track
from utils.utils import create_midi_file, save_midi_file, read_pitch_from_sound_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
pitch_result = read_pitch_from_sound_file(filename)
pitches = [pitch_dict['pitch'] for pitch_dict in pitch_result]
pitches = sanitize_pitch_list(pitches)
pitches = pitches[0:100]
midi_instance = create_midi_file(num_tracks=1, file_format=1)
tempo = 90
track1 = Track.create_track(midi_instance=midi_instance, track=0, channel=0, tempo=tempo)

time = 0
bar_count = 2
volume = 80

for pitch in pitches:
    note = Note(pitch=pitch, time=time, duration=0.25, volume=volume)
    track1.add_note(note)
    time += 0.25

save_midi_file('test.mid', midi_instance)
