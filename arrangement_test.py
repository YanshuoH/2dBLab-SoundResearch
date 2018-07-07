import sys

from model.arrangement import Arrangement
from utils.utils import create_midi_file, read_note_from_sound_file, read_pitch_from_sound_file, save_midi_file, \
    read_bpm_from_sound_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

midi_instance = create_midi_file(num_tracks=10, file_format=1)

note_result = read_note_from_sound_file(filename)
pitch_result = read_pitch_from_sound_file(filename)
tempo = read_bpm_from_sound_file(filename)
print("====> tempo extracted value = %d" % tempo)
if tempo < 50:
    tempo = 60
elif tempo > 120:
    tempo = 90
print("====> tempo shifted to value = %d" % tempo)
emphasis_proportion_list = pitch_result['emphasis_proportion_list']
density_level_list = pitch_result['density_level_list']

arrangement = Arrangement(midi_instance=midi_instance, tempo=tempo, note_result=note_result,
                          density_level_list=density_level_list)
arrangement.build()

save_midi_file('test.mid', midi_instance)
