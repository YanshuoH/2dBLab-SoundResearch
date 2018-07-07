import sys

from model.arrangement import Arrangement
from model.melody import Melody
from model.phrase_2 import Phrase2
from utils.utils import create_midi_file, read_note_from_sound_file, read_pitch_from_sound_file, save_midi_file

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
tempo = 90

midi_instance = create_midi_file(num_tracks=10, file_format=1)

note_result = read_note_from_sound_file(filename)
pitch_result = read_pitch_from_sound_file(filename)
emphasis_proportion_list = pitch_result['emphasis_proportion_list']
density_level_list = pitch_result['density_level_list']

arrangement = Arrangement(midi_instance=midi_instance, tempo=90, note_result=note_result,
                          density_level_list=density_level_list)
arrangement.build()

save_midi_file('test.mid', midi_instance)
