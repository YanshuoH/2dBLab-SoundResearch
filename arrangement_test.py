import sys

from model.arrangement import Arrangement
from utils.utils import create_midi_file, read_note_from_sound_file, read_pitch_from_sound_file, save_midi_file, \
    read_bpm_from_sound_file, get_heart_beat_track_and_save, normalize_bpm

if len(sys.argv) < 3:
    print('Usage: %s <filename> <destination>' % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
destination = sys.argv[2]

midi_instance = create_midi_file(num_tracks=10, file_format=1)

note_result = read_note_from_sound_file(filename)
pitch_result = read_pitch_from_sound_file(filename)
tempo = read_bpm_from_sound_file(filename)
print('====> tempo extracted value = %d' % tempo)
tempo = normalize_bpm(tempo)
print('====> tempo shifted to value = %d' % tempo)
emphasis_proportion_list = pitch_result['emphasis_proportion_list']
density_level_list = pitch_result['density_level_list']

FILLING_BARS = 2
arrangement = Arrangement(midi_instance=midi_instance, tempo=tempo, note_result=note_result,
                          density_level_list=density_level_list, start_time=FILLING_BARS * 4)
arrangement.build()

print('====> generating heartbeat sound track')

get_heart_beat_track_and_save(filename='heartbeat-01a.mp3', dest_filename=destination + 'heartbeat_track.mp3',
                              bar_count=len(arrangement.melody.bar_note_result_list) + FILLING_BARS * 2, bpm=tempo)

save_midi_file(destination + '.mid', midi_instance)
