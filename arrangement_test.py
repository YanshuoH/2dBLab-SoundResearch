import sys

from midiutil.MidiFile import NoteOn, TICKSPERQUARTERNOTE
from pydub import AudioSegment

from model.arrangement import Arrangement
from model.channel import channel_map, CHANNEL_NAME_DRUM_KIT
from model.note import drum_map
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

# exporting bass drum notes
bass_drum_beats_in_ms = []
ms_per_tick = 60 * 1000 / (tempo * TICKSPERQUARTERNOTE)
for event in midi_instance.tracks[channel_map[CHANNEL_NAME_DRUM_KIT]].eventList:
    if isinstance(event, NoteOn) and event.pitch == drum_map['BassDrum']:
        bass_drum_beats_in_ms.append(ms_per_tick * event.tick)
single_heart_beat = AudioSegment.from_file('./single_heartbeat.mp3', format='mp3')
heart_beat_duration_in_ms = len(single_heart_beat)
heartbeat_track = AudioSegment.empty()
for i, bass_drum_beat_note_on in enumerate(bass_drum_beats_in_ms):
    if i == 0:
        heartbeat_track += AudioSegment.silent(duration=bass_drum_beat_note_on)
    elif i + 1 < len(bass_drum_beats_in_ms):
        # fill the gap till the next heart beat
        gap = bass_drum_beats_in_ms[i + 1] - len(heartbeat_track)
        heartbeat_track += AudioSegment.silent(duration=gap)
    heartbeat_track += single_heart_beat
heartbeat_track.export('heartbeat_track.mp3', format='mp3')

save_midi_file('test.mid', midi_instance)
