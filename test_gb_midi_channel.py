from model.channel import channel_map, get_channel_program_int
from model.note import Note
from model.track import Track
from utils.utils import create_midi_file, save_midi_file

num_tracks = len(channel_map)
midi_instance = create_midi_file(num_tracks=num_tracks, file_format=1)
i = 0
for k, v in channel_map.items():
    track = Track.create_track(midi_instance=midi_instance, track=i, channel=v, tempo=90)
    print('track = %d, channel = %d' % (i, v))
    if v != 9:
        midi_instance.addProgramChange(i, i, 0, get_channel_program_int(v))
    track.add_note(Note(pitch=80, time=0, volume=80, duration=1))
    i += 1

save_midi_file('test_channel.mid', midi_instance)